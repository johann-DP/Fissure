import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.stats import linregress, pearsonr, spearmanr
from sklearn.linear_model import LinearRegression

from analysis.models import model_fissures_with_explanatory_vars


def ajouter_troisieme_subplot(fig, df, df_old):
    """Ajoute un troisième subplot comparant Bureau_old et Bureau avec ajustement par régression linéaire."""

    # Filtrer les données de df_old pour ne conserver que celles à partir de 2015
    df_old_filtered = df_old[df_old["Date"] >= "2015-01-01"]

    # Convertir les dates filtrées en format numérique pour la régression
    df_old_dates_numeric = df_old_filtered["Date"].map(pd.Timestamp.toordinal)

    # Réaliser la régression linéaire sur les données filtrées de df_old
    slope, intercept, r_value, p_value, std_err = linregress(
        df_old_dates_numeric,
        df_old_filtered["Bureau_old"] / df_old_filtered["Bureau_old"].mean() * 100
        - 100,
    )

    # Calculer la date minimale de df['Date'] en format numérique
    min_date = df["Date"].min().toordinal()

    # Calculer la valeur prédite y_pred pour la date minimale
    y_pred = slope * min_date + intercept

    # Tracer les données avec y ajusté par y_pred
    fig.add_trace(
        go.Scatter(
            x=df_old_filtered["Date"],
            y=df_old_filtered["Bureau_old"] / df_old_filtered["Bureau_old"].mean() * 100
            - 100,
            mode="lines",
            name="Bureau Old",
            line=dict(color="gray"),
        ),
        row=3,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=(
                df["Bureau"] / df["Bureau"].mean() * 100
                - 100
                - (df["Bureau"] / df["Bureau"].mean() * 100 - 100).min()
            )
            * 1.12
            + y_pred,
            mode="lines",
            name="Bureau",
            line=dict(color="blue"),
        ),
        row=3,
        col=1,
    )

    # Mise à jour des axes
    fig.update_xaxes(title_text="Date", row=3, col=1, type="date")
    fig.update_yaxes(title_text="Comparaison des écarts", row=3, col=1)

    return fig


def dataviz_evolution(df, df_old):
    # Vérification et conversion des dates en type datetime si nécessaire
    if not pd.api.types.is_datetime64_any_dtype(df["Date"]):
        df["Date"] = pd.to_datetime(df["Date"])
    if not pd.api.types.is_datetime64_any_dtype(df_old["Date"]):
        df_old["Date"] = pd.to_datetime(df_old["Date"])

    # Création de la figure avec 3 subplots
    fig = make_subplots(rows=3, cols=1, shared_xaxes=False)

    # Premier graphique (inchangé)
    bureau_norm = df["Bureau"] / df["Bureau"].mean() * 100 - 100
    mur_exterieur_norm = df["Mur extérieur"] / df["Mur extérieur"].mean() * 100 - 100
    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=bureau_norm,
            mode="lines",
            name="Bureau",
            line=dict(color="blue"),
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=mur_exterieur_norm,
            mode="lines",
            name="Mur Extérieur",
            line=dict(color="green"),
        ),
        row=1,
        col=1,
    )
    corr_pearson = pearsonr(df["Bureau"], df["Mur extérieur"])
    corr_spearman = spearmanr(df["Bureau"], df["Mur extérieur"])
    fig.add_annotation(
        x=df["Date"][2],
        y=1.5,
        text=f"Pearson: {corr_pearson[0]:.2f}<br>Spearman: {corr_spearman[0]:.2f}",
        showarrow=False,
        font=dict(size=16),
        row=1,
        col=1,
    )
    fig.update_yaxes(title_text="Écart (en %)", row=1, col=1)

    # Deuxième graphique (inchangé)
    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df["Variation Bureau"],
            mode="lines",
            name="Variations Bureau",
            line=dict(color="red"),
        ),
        row=2,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df["Variation Mur"],
            mode="lines",
            name="Variations Mur",
            line=dict(color="orange"),
        ),
        row=2,
        col=1,
    )
    fig.add_hline(y=0, line=dict(color="gray", dash="dash", width=0.5), row=2, col=1)
    corr_pearson2 = pearsonr(
        df["Variation Bureau"].dropna(), df["Variation Mur"].dropna()
    )
    corr_spearman2 = spearmanr(
        df["Variation Bureau"].dropna(), df["Variation Mur"].dropna()
    )
    fig.add_annotation(
        x=df["Date"][2],
        y=0.5,
        text=f"Pearson: {corr_pearson2[0]:.2f}<br>Spearman: {corr_spearman2[0]:.2f}",
        showarrow=False,
        font=dict(size=16),
        row=2,
        col=1,
    )
    fig.update_yaxes(title_text="Variation (en mm)", row=2, col=1)

    # Appel de la fonction pour ajouter le troisième subplot
    fig = ajouter_troisieme_subplot(fig, df, df_old)

    # Mise à jour globale de la mise en page
    fig.update_layout(
        title="Evolution des écarts, de leurs variations et des mesures historiques",
        autosize=True,
        height=1100,
        width=None,
        legend=dict(orientation="h", x=0, y=-0.2),
        font=dict(size=20),
    )

    return fig


def calculate_durations(df_paliers):
    durations = []
    for i in range(len(df_paliers)):
        start_date = df_paliers.iloc[i]["Début"]
        end_date = df_paliers.iloc[i]["Fin"]
        duration = (end_date - start_date).days
        durations.append(duration)
    return durations


def calculate_heights(df_paliers):
    heights = []
    for i in range(len(df_paliers) - 1):
        height = (
            df_paliers.iloc[i + 1]["Valeur moyenne"]
            - df_paliers.iloc[i]["Valeur moyenne"]
        )
        heights.append(height)
    return heights


# Fonction pour convertir les hauteurs de mm à µm
def convert_mm_to_um(height_mm):
    return int(round(height_mm * 1000))


def preprocessing_old_new(df_fissures, df_fissures_old):
    # Lecture des données
    df_old = df_fissures_old
    df_new = df_fissures

    # Filtrer les données de la première phase après le 1er janvier 2015 pour la régression linéaire
    df_old_filtered = df_old[df_old["Date"] >= "2015-01-01"]

    # Régression linéaire sur les données filtrées de la première phase
    X_old_filtered = (
        df_old_filtered["Date"] - df_old_filtered["Date"].min()
    ).dt.days.values.reshape(-1, 1)
    y_old_filtered = df_old_filtered["Bureau_old"].values
    model = LinearRegression().fit(X_old_filtered, y_old_filtered)

    # Prédiction pour la première date de la seconde phase
    X_new_start = np.array(
        [(df_new["Date"].iloc[0] - df_old_filtered["Date"].min()).days]
    ).reshape(-1, 1)
    predicted_start = (
        model.predict(X_new_start)[0] - 0.103
    )  # Offset dû à la fluctuation de la première mesure

    # Ajustement proportionnel
    scaling_factor = 1.12  # Estimation due au changement de hauteur de prise de mesures
    df_new["Bureau_new_adjusted"] = predicted_start + scaling_factor * (
        df_new["Bureau"] - df_new["Bureau"].iloc[0]
    )

    # Concaténer les deux séries
    df_combined = pd.concat(
        [
            df_old[["Date", "Bureau_old"]].rename(columns={"Bureau_old": "Bureau"}),
            df_new[["Date", "Bureau_new_adjusted"]].rename(
                columns={"Bureau_new_adjusted": "Bureau"}
            ),
        ]
    )

    # Vérifier et supprimer les doublons dans l'index
    df_combined = (
        df_combined.drop_duplicates(subset="Date").set_index("Date").sort_index()
    )

    # Diviser les données pour les tracer séparément
    df_combined_old = df_combined.loc[df_old["Date"].min() : df_old["Date"].max()]
    df_combined_new = df_combined.loc[df_new["Date"].min() : df_new["Date"].max()]

    # Calculer X et y combinés pour les deux phases
    X_old_combined = (df_combined_old.index - df_combined_old.index.min()).days.values
    y_old_combined = df_combined_old["Bureau"].values
    X_new_combined = (df_combined_new.index - df_combined_new.index.min()).days.values
    y_new_combined = df_combined_new["Bureau"].values

    # Points de rupture pour la première phase avec 16 segments
    manual_breaks_old_dates = [
        "2010-12-01",
        "2012-06-01",
        "2013-04-01",
        "2013-06-01",
        "2014-04-01",
        "2014-06-01",
        "2015-03-01",
        "2015-10-01",
        "2016-03-01",
        "2016-09-01",
        "2016-12-10",
        "2017-07-01",
        "2018-03-15",
        "2018-04-15",
        "2019-02-01",
        "2019-07-01",
        "2020-09-01",
    ]
    manual_breaks_old = [
        df_combined_old.index.get_loc(
            df_combined_old.index[
                df_combined_old.index.get_indexer(
                    [pd.to_datetime(date)], method="nearest"
                )[0]
            ]
        )
        for date in manual_breaks_old_dates
    ]

    # Points de rupture pour la deuxième phase avec 5 segments
    manual_breaks_new_dates = [
        "2023-12-01",
        "2024-01-15",
        "2024-02-01",
        "2024-06-01",
        "2024-07-05",
        "2024-09-01",
    ]
    manual_breaks_new = [
        df_combined_new.index.get_loc(
            df_combined_new.index[
                df_combined_new.index.get_indexer(
                    [pd.to_datetime(date)], method="nearest"
                )[0]
            ]
        )
        for date in manual_breaks_new_dates
    ]

    # Générer les segments pour la première phase
    segments_old = []
    paliers_old = []  # Liste pour stocker les paliers

    # Traitement des paliers
    for i in range(len(manual_breaks_old) - 1):
        start = manual_breaks_old[i]
        end = manual_breaks_old[i + 1]
        if i == 0:
            pass  # déporté sur une fonction séparée
        elif i % 2 == 0:
            pass  # déporté sur une fonction séparée
        else:  # Segments plats (pente nulle)
            avg_value = np.mean(y_old_combined[start : end + 1])
            y_pred = np.full(end + 1 - start, avg_value)
            segments_old.append((df_combined_old.index[start : end + 1], y_pred))
            paliers_old.append(
                [df_combined_old.index[start], df_combined_old.index[end], avg_value]
            )

    # Générer les segments pour la deuxième phase
    segments_new = []
    paliers_new = []  # Liste pour stocker les paliers

    for i in range(len(manual_breaks_new) - 1):
        start = manual_breaks_new[i]
        end = manual_breaks_new[i + 1]
        if i % 2 == 0:  # Segments plats (pente nulle)
            avg_value = np.mean(y_new_combined[start : end + 1])
            y_pred = np.full(end + 1 - start, avg_value)
            segments_new.append((df_combined_new.index[start : end + 1], y_pred))
            # Ajouter les paliers au DataFrame
            paliers_new.append(
                [df_combined_new.index[start], df_combined_new.index[end], avg_value]
            )

    # Création des DataFrames pour les paliers
    df_paliers_old = pd.DataFrame(
        paliers_old, columns=["Début", "Fin", "Valeur moyenne"]
    )
    df_paliers_new = pd.DataFrame(
        paliers_new, columns=["Début", "Fin", "Valeur moyenne"]
    )

    return (
        df_combined_old,
        df_combined_new,
        X_old_combined,
        y_old_combined,
        X_new_combined,
        y_new_combined,
        manual_breaks_old,
        manual_breaks_new,
        segments_old,
        paliers_old,
        segments_new,
        paliers_new,
        df_paliers_old,
        df_paliers_new,
    )


def plot_scatter_plotly(
    df_combined_old, y_old_combined, df_combined_new, y_new_combined
):
    fig = go.Figure()

    # Scatter plot pour la période ancienne
    fig.add_trace(
        go.Scatter(
            x=df_combined_old.index,
            y=y_old_combined,
            mode="markers",
            marker=dict(color="gray", size=5),
            name="Période Ancienne",
        )
    )

    # Scatter plot pour la période récente
    fig.add_trace(
        go.Scatter(
            x=df_combined_new.index,
            y=y_new_combined,
            mode="markers",
            marker=dict(color="blue", size=5),
            name="Période Récente (Ajustée)",
        )
    )

    fig.update_layout(
        width=None,
        height=None,
        xaxis_title="Date",
        yaxis_title="Écartement de la Fissure (mm)",
        title="Évolution de l'Écartement de la Fissure",
        showlegend=True,
    )

    fig_plot_scatter_plotly = fig

    return fig_plot_scatter_plotly


def plot_segments_plotly(fig_plot_scatter_plotly, segments_old, segments_new):
    # Tracer les segments pour la première phase (en bleu)
    for segment in segments_old:
        if (
            len(segment[0]) > 1 and len(segment[1]) > 1
        ):  # S'assurer qu'il y a bien des points à tracer
            fig_plot_scatter_plotly.add_trace(
                go.Scatter(
                    x=segment[0],
                    y=segment[1],
                    mode="lines",
                    line=dict(color="gray", width=2),
                    showlegend=False,
                )
            )

    # Tracer les segments pour la deuxième phase (en rouge)
    for segment in segments_new:
        if len(segment[0]) > 1 and len(segment[1]) > 1:
            fig_plot_scatter_plotly.add_trace(
                go.Scatter(
                    x=segment[0],
                    y=segment[1],
                    mode="lines",
                    line=dict(color="blue", width=2),
                    showlegend=False,
                )
            )

    fig_plot_segments_plotly = fig_plot_scatter_plotly
    return fig_plot_segments_plotly


def plot_additional_segments_plotly(
    fig_plot_segments_plotly,
    df_combined_old,
    y_old_combined,
    df_paliers_old,
    df_paliers_new,
):
    # Ajouter le segment du premier point au début du premier palier
    premier_point_x = df_combined_old.index[0]
    premier_point_y = y_old_combined[0]
    debut_premier_palier_x = df_paliers_old.iloc[0]["Début"]
    debut_premier_palier_y = df_paliers_old.iloc[0]["Valeur moyenne"]

    fig_plot_segments_plotly.add_trace(
        go.Scatter(
            x=[premier_point_x, debut_premier_palier_x],
            y=[premier_point_y, debut_premier_palier_y],
            mode="lines",
            line=dict(color="gray", width=2, dash="dash"),
            showlegend=False,
        )
    )

    # Ajouter les segments entre paliers pour la première phase (en bleu)
    for i in range(len(df_paliers_old) - 1):
        fig_plot_segments_plotly.add_trace(
            go.Scatter(
                x=[df_paliers_old.iloc[i]["Fin"], df_paliers_old.iloc[i + 1]["Début"]],
                y=[
                    df_paliers_old.iloc[i]["Valeur moyenne"],
                    df_paliers_old.iloc[i + 1]["Valeur moyenne"],
                ],
                mode="lines",
                line=dict(color="gray", width=2, dash="dash"),
                showlegend=False,
            )
        )

    # Ajouter les segments entre paliers pour la deuxième phase (en rouge)
    for i in range(len(df_paliers_new) - 1):
        fig_plot_segments_plotly.add_trace(
            go.Scatter(
                x=[df_paliers_new.iloc[i]["Fin"], df_paliers_new.iloc[i + 1]["Début"]],
                y=[
                    df_paliers_new.iloc[i]["Valeur moyenne"],
                    df_paliers_new.iloc[i + 1]["Valeur moyenne"],
                ],
                mode="lines",
                line=dict(color="blue", width=2, dash="dash"),
                showlegend=False,
            )
        )

    fig_plot_additional_segments_plotly = fig_plot_segments_plotly

    return fig_plot_additional_segments_plotly


def annotate_durations_plotly(
    fig_plot_additional_segments_plotly,
    df_paliers_old,
    df_paliers_new,
    horizontal_durations_old,
    horizontal_durations_new,
):
    # Ajouter les annotations pour les paliers (durée) pour la première phase
    for i in range(len(df_paliers_old)):
        duration_days = horizontal_durations_old[i]
        mid_point = (
            df_paliers_old.iloc[i]["Début"]
            + (df_paliers_old.iloc[i]["Fin"] - df_paliers_old.iloc[i]["Début"]) / 2
        )
        fig_plot_additional_segments_plotly.add_annotation(
            x=mid_point,
            y=df_paliers_old.iloc[i]["Valeur moyenne"],
            text=f"{duration_days} jours",
            showarrow=True,
            arrowhead=2,
            ax=0,
            ay=30,
            font=dict(color="blue", size=10),
            bgcolor="cornsilk",
            # opacity=0.6
        )

    # Ajouter les annotations pour les paliers (durée) pour la deuxième phase
    for i in range(len(df_paliers_new)):
        duration_days = horizontal_durations_new[i]
        mid_point = (
            df_paliers_new.iloc[i]["Début"]
            + (df_paliers_new.iloc[i]["Fin"] - df_paliers_new.iloc[i]["Début"]) / 2
        )
        fig_plot_additional_segments_plotly.add_annotation(
            x=mid_point,
            y=df_paliers_new.iloc[i]["Valeur moyenne"],
            text=f"{duration_days} jours",
            showarrow=True,
            arrowhead=2,
            ax=15,
            ay=30,
            font=dict(color="blue", size=10),
            bgcolor="cornsilk",
        )

    fig_annotate_durations_plotly = fig_plot_additional_segments_plotly

    return fig_annotate_durations_plotly


def add_vertical_segments_and_heights_plotly(
    fig_annotate_durations_plotly,
    df_paliers_old,
    df_paliers_new,
    horizontal_heights_old,
    horizontal_heights_new,
):
    # Ajouter les segments verticaux et les annotations pour les hauteurs pour la première phase
    for i in range(len(df_paliers_old) - 1):
        height_um = convert_mm_to_um(horizontal_heights_old[i])
        fig_annotate_durations_plotly.add_trace(
            go.Scatter(
                x=[df_paliers_old.iloc[i]["Fin"], df_paliers_old.iloc[i]["Fin"]],
                y=[
                    df_paliers_old.iloc[i]["Valeur moyenne"],
                    df_paliers_old.iloc[i + 1]["Valeur moyenne"],
                ],
                mode="lines",
                line=dict(color="gray", width=2, dash="solid"),
                opacity=0.3,
                showlegend=False,
            )
        )
        fig_annotate_durations_plotly.add_annotation(
            x=df_paliers_old.iloc[i]["Fin"],
            y=(
                df_paliers_old.iloc[i]["Valeur moyenne"]
                + df_paliers_old.iloc[i + 1]["Valeur moyenne"]
            )
            / 2,
            text=f"{height_um} µm",
            showarrow=True,
            arrowhead=2,
            ax=-50,
            ay=-10,
            font=dict(color="blue", size=10),
            bgcolor="lightgray",
            # opacity=0.6
        )

    # Ajouter les segments verticaux et les annotations pour les hauteurs pour la deuxième phase
    for i in range(len(df_paliers_new) - 1):
        height_um = convert_mm_to_um(horizontal_heights_new[i])
        fig_annotate_durations_plotly.add_trace(
            go.Scatter(
                x=[df_paliers_new.iloc[i]["Fin"], df_paliers_new.iloc[i]["Fin"]],
                y=[
                    df_paliers_new.iloc[i]["Valeur moyenne"],
                    df_paliers_new.iloc[i + 1]["Valeur moyenne"],
                ],
                mode="lines",
                line=dict(color="blue", width=2, dash="solid"),
                opacity=0.3,
                showlegend=False,
            )
        )
        fig_annotate_durations_plotly.add_annotation(
            x=df_paliers_new.iloc[i]["Fin"],
            y=(
                df_paliers_new.iloc[i]["Valeur moyenne"]
                + df_paliers_new.iloc[i + 1]["Valeur moyenne"]
            )
            / 2,
            text=f"{height_um} µm",
            showarrow=True,
            arrowhead=2,
            ax=-50,
            ay=-10,
            font=dict(color="blue", size=10),
            bgcolor="lightgray",
            # opacity=0.6
        )

    fig_add_vertical_segments_and_heights_plotly = fig_annotate_durations_plotly
    return fig_add_vertical_segments_and_heights_plotly


def dataviz_old_new(df_fissures, df_fissures_old):
    # Prétraitement des données
    (
        df_combined_old,
        df_combined_new,
        X_old_combined,
        y_old_combined,
        X_new_combined,
        y_new_combined,
        manual_breaks_old,
        manual_breaks_new,
        segments_old,
        paliers_old,
        segments_new,
        paliers_new,
        df_paliers_old,
        df_paliers_new,
    ) = preprocessing_old_new(df_fissures, df_fissures_old)

    # Appel à la fonction de modélisation avec les paliers
    model_results = model_fissures_with_explanatory_vars(df_paliers_old, df_paliers_new)

    # Afficher les RMSE pour chaque modèle
    for model_name, result in model_results.items():
        print(f"{model_name} - RMSE: {result['rmse']:.4f}")

    # Vérifier l'absence de doublons
    if df_combined_old.index.duplicated().any():
        print("Doublons dans df_combined_old")
        print(df_combined_old[df_combined_old.index.duplicated(keep=False)])

    if df_combined_new.index.duplicated().any():
        print("Doublons dans df_combined_new")
        print(df_combined_new[df_combined_new.index.duplicated(keep=False)])

    # Calculer les durées et les hauteurs pour les annotations
    horizontal_durations_old = calculate_durations(df_paliers_old)
    horizontal_durations_new = calculate_durations(df_paliers_new)
    horizontal_heights_old = calculate_heights(df_paliers_old)
    horizontal_heights_new = calculate_heights(df_paliers_new)

    # Créer la figure initiale avec les scatter plots
    fig = plot_scatter_plotly(
        df_combined_old, y_old_combined, df_combined_new, y_new_combined
    )

    # Ajouter les segments de paliers
    fig = plot_segments_plotly(fig, segments_old, segments_new)

    # Ajouter le segment du premier point au début du premier palier et les segments entre paliers
    fig = plot_additional_segments_plotly(
        fig, df_combined_old, y_old_combined, df_paliers_old, df_paliers_new
    )

    # Ajouter les annotations pour les durées des paliers
    fig = annotate_durations_plotly(
        fig,
        df_paliers_old,
        df_paliers_new,
        horizontal_durations_old,
        horizontal_durations_new,
    )

    # Ajouter les segments verticaux et les annotations pour les hauteurs
    fig = add_vertical_segments_and_heights_plotly(
        fig,
        df_paliers_old,
        df_paliers_new,
        horizontal_heights_old,
        horizontal_heights_new,
    )

    # Configuration finale du graphique avec les détails sur les dates et l'axe des x
    fig.update_layout(
        title="Évolution de l'Écartement de la Fissure avec Modélisation des Paliers",
        xaxis_title="Date",
        yaxis_title="Écartement de la Fissure (mm)",
        showlegend=True,
        xaxis=dict(showgrid=True, tickformat="%Y-%m"),
        yaxis=dict(showgrid=True),
        font=dict(color="black", size=20),
        autosize=True,
        width=None,
        height=None,
    )

    return fig
