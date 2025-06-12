# time_calculator.py
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd


def calculate_central_times(df, daily_stats=None):
    """
    Renvoie deux arrays (min_times, max_times) en heures décimales, basés sur
    compute_daily_extrema_timestamps(df). daily_stats est ignoré.
    """

    daily_ext = compute_daily_extrema_timestamps(df)
    # Trier par jour pour l’ordre
    daily_ext = daily_ext.sort_values("day")

    # Convertir timestamps en heures décimales
    to_hours = lambda ts: ts.dt.hour + ts.dt.minute / 60 + ts.dt.second / 3600

    max_times = to_hours(daily_ext["time_max"])
    min_times = to_hours(daily_ext["time_min"])

    return np.array(min_times, dtype=float), np.array(max_times, dtype=float)


def compute_daily_extrema_timestamps(df: pd.DataFrame) -> pd.DataFrame:
    """Calcule les heures et valeurs extrêmes de chaque journée.

    Les segments monotones en début et fin de journée sont écartés afin de ne
    conserver que le cœur de la variation journalière. Les signaux de
    variations sont obtenus via ``np.sign`` sur les différences successives ;
    les plateaux (valeur nulle) sont propagés pour être assimilés aux tendances
    voisines. Une fois ce cœur isolé, les éventuels plateaux aux nouvelles
    extrémités (valeur égale, à ``tol`` près, à la première ou dernière mesure
    retenue) sont également retirés.

    Returns
    -------
    pd.DataFrame
        Colonnes ``['day', 'time_max', 'val_max', 'time_min', 'val_min']`` pour
        chaque jour disposant encore de données intérieures.
    """
    import pandas as pd
    import numpy as np

    df2 = df.copy()
    df2["timestamp"] = pd.to_datetime(df2["timestamp"])
    df2 = df2.sort_values("timestamp")
    df2["day"] = df2["timestamp"].dt.date

    tol = 1e-4
    records = []

    for day, grp in df2.groupby("day"):
        if len(grp) < 3:
            continue

        signs = np.sign(np.diff(grp["inch"].to_numpy()))

        if np.all(signs == 0):
            continue

        # Propage le dernier signe non nul afin de considérer les plateaux comme
        # faisant partie de la tendance précédente/suivante
        filled = signs.copy()
        for i in range(1, len(filled)):
            if filled[i] == 0:
                filled[i] = filled[i - 1]
        for i in range(len(filled) - 2, -1, -1):
            if filled[i] == 0:
                filled[i] = filled[i + 1]

        start_idx = 1
        switch_down = np.where((filled[:-1] > 0) & (filled[1:] < 0))[0]
        if switch_down.size:
            start_idx = switch_down[0] + 1

        end_idx = len(grp) - 2
        switch_up = np.where((filled[:-1] < 0) & (filled[1:] > 0))[0]
        if switch_up.size:
            end_idx = switch_up[-1] + 1

        if start_idx >= end_idx:
            continue

        interior = grp.iloc[start_idx : end_idx + 1].copy()

        # Retire les éventuels plateaux de bordure (même valeur qu'en 1ère ou
        # dernière mesure conservée)
        first_val = interior["inch"].iloc[0]
        last_val = interior["inch"].iloc[-1]
        interior = interior[~np.isclose(interior["inch"], first_val, atol=tol)]
        interior = interior[~np.isclose(interior["inch"], last_val, atol=tol)]
        if interior.empty:
            continue

        # Max et min absolus sur les données restantes (ordre indifférent)
        val_max = interior["inch"].max()
        time_max = interior.loc[interior["inch"].idxmax(), "timestamp"]

        val_min = interior["inch"].min()
        time_min = interior.loc[interior["inch"].idxmin(), "timestamp"]

        records.append({
            "day":      day,
            "time_max": time_max,
            "val_max":  val_max,
            "time_min": time_min,
            "val_min":  val_min
        })

    return pd.DataFrame(records)


def get_extreme_half_hours(df_day_half_mean, df_day_half_median):
    """
    Récupère, pour chaque jour, l'heure (en demi-heure décimale) où se produit
    le max/min dans df_day_half_mean et df_day_half_median.
    """
    max_half_times_mean = df_day_half_mean.groupby('day').apply(
        lambda grp: grp.loc[grp['inch'].idxmax(), 'half_hour']
    )
    min_half_times_mean = df_day_half_mean.groupby('day').apply(
        lambda grp: grp.loc[grp['inch'].idxmin(), 'half_hour']
    )
    max_half_times_median = df_day_half_median.groupby('day').apply(
        lambda grp: grp.loc[grp['inch'].idxmax(), 'half_hour']
    )
    min_half_times_median = df_day_half_median.groupby('day').apply(
        lambda grp: grp.loc[grp['inch'].idxmin(), 'half_hour']
    )

    return {
        "max_half_times_mean": max_half_times_mean,
        "min_half_times_mean": min_half_times_mean,
        "max_half_times_median": max_half_times_median,
        "min_half_times_median": min_half_times_median
    }
