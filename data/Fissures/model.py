import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import timedelta, datetime
from scipy.stats import pearsonr
from sklearn.linear_model import (LinearRegression, Lasso, Ridge, ElasticNet,
                                  ARDRegression, BayesianRidge)
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error, r2_score
from sklearn.model_selection import LeaveOneOut, cross_val_predict
import warnings

warnings.filterwarnings("ignore")

# =====================================================
# Paramètres et chemins d'accès
# =====================================================
data_folder = r"C:\Users\johan\PycharmProjects\Fissure-master\data\Fissures"
results_folder = os.path.join(data_folder, "Results_model")  # Dossier de sortie (déjà créé)
meteo_file = os.path.join(data_folder, "20250118_20250210.xls")
mur_file = os.path.join(data_folder, "mur_route.xlsx")

# =====================================================
# Paramètres pour la construction des features
# =====================================================
# Variables météorologiques à retenir
vars_a_retenir = [
    'Outdoor Tem(°C)',
    'Outdoor Tem.Max(°C)',
    'Outdoor Tem.Min(°C)',
    'Outdoor Hum(%)',
    'Outdoor Hum.Max(%)',
    'Outdoor Hum.Min(%)',
    'Rainfull(Hour)(mm)',
    'Rainfull(Day)(mm)',
    'Wind speed(Hour)(km/h)',
    'Pressure(hpa)'
]
# Remonter jusqu'à 15 jours en arrière, heure par heure
max_lag_hours = 15 * 24  # 360 heures
# On suppose que la mesure de 'inch' est prise à 07:00
mesure_hour = 7

# =====================================================
# 1. Lecture et préparation des données météo (horaire)
# =====================================================
df_meteo = pd.read_excel(meteo_file)

# Conserver la colonne 'Time' et les variables à retenir
cols_to_keep = ['Time'] + [v for v in vars_a_retenir if v in df_meteo.columns]
df_meteo = df_meteo[cols_to_keep]

# Conversion de 'Time' en datetime et retrait d'éventuels fuseaux horaires
df_meteo['Time'] = pd.to_datetime(df_meteo['Time'], errors='coerce')
if df_meteo['Time'].iloc[0].tzinfo is not None:
    df_meteo['Time'] = df_meteo['Time'].dt.tz_convert(None)

# Arrondir les temps à l'heure (floor)
df_meteo['rounded_time'] = df_meteo['Time'].dt.floor('H')
# Créer un DataFrame indexé par 'rounded_time'
df_meteo_hourly = df_meteo.drop_duplicates(subset='rounded_time').set_index('rounded_time')

# Pour l'imputation en cas de données manquantes, calculer la moyenne globale de chaque variable retenue
meteo_means = df_meteo_hourly[vars_a_retenir].mean()

# =====================================================
# 2. Lecture et préparation des données du mur (inch)
# =====================================================
df_mur = pd.read_excel(mur_file)
# Conserver la 1ère colonne (date) et la 5ème (inch)
df_mur = df_mur.iloc[:, [0, 4]]
df_mur.columns = ['date', 'inch']
df_mur['date'] = pd.to_datetime(df_mur['date'], dayfirst=True)

# =====================================================
# 3. Construction de la base avec les lags horaires
# =====================================================
# Pour chaque mesure de 'inch', récupérer pour chacune des variables retenues
# la valeur mesurée pour chaque heure de lag (de 1 à 360).
features_list = []
for idx, row in df_mur.iterrows():
    # Considérer que la mesure est prise à l'heure fixe 'mesure_hour' du jour indiqué
    mur_date = row['date'].date()
    measurement_time = pd.Timestamp(datetime.combine(mur_date, datetime.min.time())) + pd.Timedelta(hours=mesure_hour)
    measurement_time = measurement_time.floor('H')

    feature_dict = {}
    for var in vars_a_retenir:
        for lag in range(1, max_lag_hours + 1):
            target_time = measurement_time - timedelta(hours=lag)
            try:
                value = df_meteo_hourly.at[target_time, var]
            except KeyError:
                value = np.nan
            # Imputation avec la moyenne globale de la variable en cas de donnée manquante
            if pd.isna(value):
                value = meteo_means[var]
            feature_dict[f"{var}_lag{lag}"] = value
    feature_dict['date'] = measurement_time
    feature_dict['inch'] = row['inch']
    features_list.append(feature_dict)

df_features = pd.DataFrame(features_list)
df_features.reset_index(drop=True, inplace=True)

# Séparer la cible et les variables explicatives
X = df_features.drop(columns=['date', 'inch'])
y = df_features['inch']


# =====================================================
# 4. Sélection de features (prédimensionnement)
# =====================================================
# Avec un nombre potentiellement très élevé de features (10 x 360 = 3600),
# et un effectif très faible (nombre de mesures de 'inch'),
# nous réduisons la dimension en gardant les 10 features ayant la plus forte corrélation absolue avec y.
def safe_corr(series):
    if series.std() == 0:
        return 0
    return np.abs(np.corrcoef(series, y)[0, 1])


corr_series = X.apply(safe_corr)
top_features = corr_series.sort_values(ascending=False).head(10).index.tolist()
X_reduced = X[top_features]

print("Top features sélectionnées (basées sur la corrélation absolue avec 'inch') :")
for feat in top_features:
    print(f"  {feat} (corrélation absolue = {corr_series[feat]:.4f})")

# =====================================================
# 5. Définition des modèles, évaluation en LOOCV et tests statistiques
# =====================================================
models = {
    "OLS": LinearRegression(),
    "LASSO": Lasso(alpha=1e-3, max_iter=10000, random_state=42),
    "Ridge": Ridge(alpha=1.0, max_iter=10000, random_state=42),
    "ElasticNet": ElasticNet(alpha=0.1, l1_ratio=0.5, max_iter=10000, random_state=42),
    "ARD": ARDRegression(),
    "BayesianRidge": BayesianRidge()
}

loo = LeaveOneOut()


def compute_metrics(y_true, y_pred, num_params):
    n = len(y_true)
    rmse_val = np.sqrt(mean_squared_error(y_true, y_pred))
    mape_val = mean_absolute_percentage_error(y_true, y_pred) * 100  # en %
    r2_val = r2_score(y_true, y_pred)
    # Calcul de l'Adjusted R2 (peut être NaN pour n très faible)
    adj_r2 = 1 - (1 - r2_val) * (n - 1) / (n - num_params - 1) if (n - num_params - 1) > 0 else np.nan
    rss = np.sum((y_true - y_pred) ** 2)
    aic = n * np.log(rss / n) + 2 * num_params if rss > 0 else -np.inf
    bic = n * np.log(rss / n) + num_params * np.log(n) if rss > 0 else -np.inf
    return rmse_val, mape_val, r2_val, adj_r2, aic, bic


performance_results = []
model_names = []
for name, model in models.items():
    # Prédictions en validation leave-one-out
    y_pred_cv = cross_val_predict(model, X_reduced, y, cv=loo)
    # Entraîner le modèle sur l'ensemble complet pour extraire les coefficients
    model.fit(X_reduced, y)
    if hasattr(model, 'coef_'):
        num_params = len(model.coef_)
    else:
        num_params = X_reduced.shape[1]

    rmse_val, mape_val, r2_val, adj_r2, aic, bic = compute_metrics(y, y_pred_cv, num_params)
    # Test statistique : calcul du coefficient de corrélation de Pearson et p-value
    r_val, p_val = pearsonr(y, y_pred_cv)

    performance_results.append({
        "Model": name,
        "RMSE": rmse_val,
        "MAPE (%)": mape_val,
        "R2": r2_val,
        "Adjusted_R2": adj_r2,
        "AIC": aic,
        "BIC": bic,
        "Num_Params": num_params,
        "Pearson_r": r_val,
        "p_value": p_val
    })
    model_names.append(name)

    print(f"\nModèle: {name}")
    print(f"  RMSE        : {rmse_val:.4f}")
    print(f"  MAPE        : {mape_val:.2f}%")
    print(f"  R2          : {r2_val * 100:.2f}%")
    print(f"  AIC         : {aic:.1f}")
    print(f"  BIC         : {bic:.1f}")
    print(f"  Nombre de paramètres : {num_params}")
    print(f"  Pearson r   : {r_val:.2f} (p = {p_val:.3f})")

    # Création d'une figure avec deux subplots côte à côte
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Sous-plot de gauche : Mesuré vs. Prévu + annotations (incluant les tests statistiques)
    ax_left = axes[0]
    ax_left.scatter(y, y_pred_cv, color='blue', zorder=3)
    ax_left.plot([y.min(), y.max()], [y.min(), y.max()], color='red', linestyle='--', zorder=2)
    ax_left.set_xlabel("Mesuré (inch)")
    ax_left.set_ylabel("Prévu (inch)")
    ax_left.set_title(f"{name} : Mesuré vs. Prévu")
    textstr = (f"RMSE: {rmse_val:.4f}\n"
               f"MAPE: {mape_val:.2f}%\n"
               f"R2: {r2_val * 100:.2f}%\n"
               f"AIC: {aic:.1f}\n"
               f"BIC: {bic:.1f}\n"
               f"Pearson r: {r_val:.2f} (p = {p_val:.3f})")
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    ax_left.text(0.05, 0.95, textstr, transform=ax_left.transAxes, fontsize=10,
                 verticalalignment='top', bbox=props)

    # Sous-plot de droite : Top Feature Importances (coefficients)
    ax_right = axes[1]
    if hasattr(model, 'coef_'):
        coefs = model.coef_
        features = X_reduced.columns
        coef_series = pd.Series(coefs, index=features)
        # Trier par ordre décroissant de la valeur absolue
        coef_series_sorted = coef_series.reindex(coef_series.abs().sort_values(ascending=False).index)
        # Conserver au maximum 10 variables (ici, déjà réduit)
        if len(coef_series_sorted) > 10:
            coef_series_top = coef_series_sorted.head(10)
        else:
            coef_series_top = coef_series_sorted
        ax_right.barh(coef_series_top.index, coef_series_top.values, color='green')
        ax_right.set_xlabel("Coefficient")
        ax_right.set_title("Top Variables Explicatives")
        ax_right.invert_yaxis()  # La plus importante en haut

        # Sauvegarder les coefficients dans un CSV
        coef_df = coef_series_top.reset_index()
        coef_df.columns = ["Feature", "Coefficient"]
        coef_csv_path = os.path.join(results_folder, f"coefficients_{name}.csv")
        coef_df.to_csv(coef_csv_path, index=False)
    else:
        ax_right.text(0.5, 0.5, "Aucun coefficient exploitable", horizontalalignment='center',
                      verticalalignment='center', fontsize=12)

    plt.suptitle(f"Modèle {name}", fontsize=16)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    fig_path = os.path.join(results_folder, f"model_{name}.png")
    plt.savefig(fig_path)
    plt.close()

# =====================================================
# Comparaison globale des modèles
# =====================================================
performance_df = pd.DataFrame(performance_results)
performance_df_sorted = performance_df.sort_values(by="RMSE")
performance_csv_path = os.path.join(results_folder, "model_performance.csv")
performance_df_sorted.to_csv(performance_csv_path, index=False)

print("\n----- Classement des modèles par RMSE (du plus performant au moins performant) -----")
print(performance_df_sorted[
          ["Model", "RMSE", "MAPE (%)", "R2", "Adjusted_R2", "AIC", "BIC", "Num_Params", "Pearson_r", "p_value"]])

# Figure de comparaison globale (bar plot des RMSE)
plt.figure(figsize=(10, 6))
plt.bar(performance_df_sorted["Model"], performance_df_sorted["RMSE"], color='skyblue')
plt.xlabel("Modèle")
plt.ylabel("RMSE")
plt.title("Comparaison des RMSE des modèles (LOOCV)")
plt.tight_layout()
comparison_fig_path = os.path.join(results_folder, "models_comparison.png")
plt.savefig(comparison_fig_path)
plt.close()

print("\nLes résultats (CSV et figures) ont été sauvegardés dans le dossier :")
print(results_folder)
