import pandas as pd
import numpy as np
import os


# Fonction pour charger tous les fichiers CSV dans un répertoire donné
def load_data_from_directory(directory_path):
    dataframes = []
    for file in os.listdir(directory_path):
        if file.endswith('.csv') or file.endswith('.xls'):
            file_path = os.path.join(directory_path, file)
            df = pd.read_csv(file_path) if file.endswith('.csv') else pd.read_excel(file_path)
            df['Source File'] = file  # Ajoute une colonne pour indiquer la source
            dataframes.append(df)
    return pd.concat(dataframes, ignore_index=True)


# Fonction pour identifier et comparer les données de la dernière semaine
def analyze_recent_week(directory_path, recent_file):
    # Charger toutes les données
    all_data = load_data_from_directory(directory_path)

    # Charger uniquement les données du dernier fichier (la semaine en question)
    recent_data = pd.read_excel(os.path.join(directory_path, recent_file))

    # Afficher les colonnes pour avoir une vue d'ensemble
    print("Colonnes du fichier récent :", recent_data.columns)

    # Vérification des valeurs manquantes dans les deux jeux de données
    print("\nValeurs manquantes dans le fichier récent :")
    print(recent_data.isna().sum())

    print("\nValeurs manquantes dans l'ensemble des données précédentes :")
    print(all_data.isna().sum())

    # Vérification des valeurs négatives ou suspectes pour certaines colonnes pertinentes
    if 'Wind speed(km/h)' in recent_data.columns:
        print("\nStatistiques des vitesses du vent dans le fichier récent :")
        print(recent_data['Wind speed(km/h)'].describe())

        print("\nStatistiques des vitesses du vent dans l'ensemble des données précédentes :")
        print(all_data['Wind speed(km/h)'].describe())

        # Vérifier la présence de valeurs négatives ou de NaN
        print("\nVérification des valeurs négatives dans le fichier récent pour 'Wind speed(km/h)':")
        print(recent_data[recent_data['Wind speed(km/h)'] < 0])

        print("\nVérification des valeurs NaN dans le fichier récent pour 'Wind speed(km/h)':")
        print(recent_data[recent_data['Wind speed(km/h)'].isna()])

    # Comparaison de la distribution des autres colonnes clés
    if 'Wind direction radians' in recent_data.columns:
        print("\nStatistiques de la direction du vent dans le fichier récent :")
        print(recent_data['Wind direction radians'].describe())

        print("\nStatistiques de la direction du vent dans l'ensemble des données précédentes :")
        print(all_data['Wind direction radians'].describe())

    # Comparer d'autres colonnes si nécessaire
    # ...

    return recent_data, all_data


# Appel principal pour explorer les données
if __name__ == "__main__":
    directory_path = 'data/Meteo/'  # Chemin vers votre dossier contenant les données météo
    recent_file = '20240902_20241006.xls'  # Nom du dernier fichier à vérifier

    recent_data, all_data = analyze_recent_week(directory_path, recent_file)
