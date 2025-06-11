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
    """
    Pour chaque jour, identifie les extrema absolus hors 00:00 et 24:00,
    en rejetant tout niveau (max ou min) qui apparaît aussi à la première
    ou à la dernière mesure du jour (palier frontière).
    Retourne ['day','time_max','val_max','time_min','val_min'].
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

        t0 = grp["timestamp"].iloc[0]
        t1 = grp["timestamp"].iloc[-1]
        interior = grp[(grp["timestamp"] > t0) & (grp["timestamp"] < t1)]
        if len(interior) < 2:
            continue

        # --- MAX ---
        val_max = interior["inch"].max()
        # rejet si ce niveau apparaît à la frontière
        bmax = grp[np.abs(grp["inch"] - val_max) < tol]
        if (bmax["timestamp"] == t0).any() or (bmax["timestamp"] == t1).any():
            continue

        pm = interior[np.abs(interior["inch"] - val_max) < tol]
        time_max = pm["timestamp"].iloc[0]

        # --- MIN (phase décroissante après time_max) ---
        aft = interior[interior["timestamp"] > time_max]
        if aft.empty:
            continue

        val_min = aft["inch"].min()
        bmin = grp[np.abs(grp["inch"] - val_min) < tol]
        if (bmin["timestamp"] == t0).any() or (bmin["timestamp"] == t1).any():
            continue

        pmn = aft[np.abs(aft["inch"] - val_min) < tol]
        time_min = pmn["timestamp"].iloc[0]

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
