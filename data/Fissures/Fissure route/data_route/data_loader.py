# -*- coding: utf-8 -*-
import os
import shutil
import paramiko
import pandas as pd
from datetime import datetime, timedelta


def fetch_remote_csv(
        hostname: str,
        port: int,
        username: str,
        password: str,
        local_path: str,
        remote_path: str,
        do_backup: bool = True
):
    """
    Se connecte via SSH/SFTP au host pour récupérer le fichier CSV distant.
    Si do_backup est True et que local_path existe, on fait une sauvegarde horodatée avant de le remplacer.

    Paramètres :
    - hostname, port, username, password : identifiants pour la connexion SSH
    - local_path : chemin local où sera stocké le CSV
    - remote_path : chemin distant (sur le Raspberry / autre machine)
    - do_backup  : bool, pour effectuer (ou non) une copie de sauvegarde du fichier local existant

    Retourne :
    - None, mais récupère le fichier "remote_path" vers "local_path".
    - Affiche des informations de debug via print (ou logs).
    """
    # Sauvegarde locale si on l'exige et que le fichier existe déjà
    if do_backup and os.path.exists(local_path):
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        backup_path = os.path.join(os.path.dirname(local_path), f"measurements_{yesterday}.csv")
        shutil.copy2(local_path, backup_path)
        print(f"Sauvegarde effectuée : {local_path} -> {backup_path}")
    else:
        print(f"Aucun fichier local '{local_path}' trouvé pour la sauvegarde (ou backup désactivé).")

    # Connexion SSH / SFTP
    try:
        transport = paramiko.Transport((hostname, port))
        transport.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.get(remote_path, local_path)
        print(f"Transfert réussi : {remote_path} --> {local_path}")
        sftp.close()
        transport.close()
    except Exception as e:
        print("Erreur lors du transfert SSH/SFTP :", e)


def load_data(local_path, start_day_str, end_day_str):
    """
    Charge le CSV `local_path` dans un DataFrame, applique les filtres temporels
    et renvoie le DataFrame filtré et formaté (colonnes additionnelles, etc.).
    """
    start_day = pd.to_datetime(start_day_str)
    end_day = pd.to_datetime(end_day_str)

    df = pd.read_csv(local_path, header=None)
    df.columns = ['timestamp', 'inch']
    df['inch'] = pd.to_numeric(df['inch'], errors='coerce')
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp')

    # Filtre temporel (du début à la fin, fin inclus jusqu'à 23:59 du jour end_day)
    mask_time = (df['timestamp'] >= start_day) & (df['timestamp'] < (end_day + pd.Timedelta(days=1)))
    df = df[mask_time]

    # Filtre sur la fréquence (conservation des points espacés d'au moins 10s ou premier point)
    mask_freq = (df['timestamp'].diff() >= pd.Timedelta(seconds=10)) | (df['timestamp'].diff().isna())
    df = df[mask_freq]

    # Ajout de colonnes temporelles et unité métrique
    df['day'] = df['timestamp'].dt.date
    df['mm'] = df['inch'] * 25.4
    df['hour'] = df['timestamp'].dt.hour + df['timestamp'].dt.minute / 60 + df['timestamp'].dt.second / 3600
    df['hour_bin'] = df['timestamp'].dt.hour
    df['half_hour'] = df['timestamp'].dt.hour + (df['timestamp'].dt.minute // 30) * 0.5

    return df
