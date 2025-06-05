# time_calculator.py
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd


def calculate_central_times(df, daily_stats):
    """
    (Optionnel – si vous utilisez encore ici le half_hour)
    Ce code n’est plus nécessaire pour l’onglet 2/3,
    puisque l’on utilise compute_daily_extrema_timestamps à la place.
    """
    unique_days = sorted(daily_stats["day"].unique())
    min_times = []
    max_times = []
    tol = 1e-4

    for day in unique_days:
        day_df = df[df["day"] == day]
        local_min = daily_stats[daily_stats["day"] == day]["min"].iloc[0]
        local_max = daily_stats[daily_stats["day"] == day]["max"].iloc[0]

        first_ts = day_df["timestamp"].min()
        last_ts = day_df["timestamp"].max()
        day_df_filtered = day_df[
            (day_df["timestamp"] > first_ts) & (day_df["timestamp"] < last_ts)
        ]

        plateau_min_all = day_df_filtered[np.abs(day_df_filtered["inch"] - local_min) < tol]
        plateau_max_all = day_df_filtered[np.abs(day_df_filtered["inch"] - local_max) < tol]

        plateau_min = plateau_min_all.copy()
        plateau_max = plateau_max_all.copy()

        if (not plateau_min_all.empty) and (not plateau_max_all.empty):
            ts_min_first = plateau_min_all["timestamp"].min()
            ts_max_first = plateau_max_all["timestamp"].min()

            if ts_min_first < ts_max_first:
                plateau_min = plateau_min_all[plateau_min_all["timestamp"] > ts_max_first]
            else:
                plateau_min = plateau_min_all

            if ts_max_first > ts_min_first:
                plateau_max = plateau_max_all[plateau_max_all["timestamp"] < ts_min_first]
            else:
                plateau_max = plateau_max_all

        if not plateau_min.empty:
            times_min = (
                plateau_min["timestamp"].dt.hour
                + plateau_min["timestamp"].dt.minute / 60
                + plateau_min["timestamp"].dt.second / 3600
            )
            central_min = (times_min.min() + times_min.max()) / 2
        else:
            central_min = np.nan

        if not plateau_max.empty:
            times_max = (
                plateau_max["timestamp"].dt.hour
                + plateau_max["timestamp"].dt.minute / 60
                + plateau_max["timestamp"].dt.second / 3600
            )
            central_max = (times_max.min() + times_max.max()) / 2
        else:
            central_max = np.nan

        min_times.append(central_min)
        max_times.append(central_max)

    return np.array(min_times, dtype=np.float64), np.array(max_times, dtype=np.float64)


def compute_daily_extrema_timestamps(df: pd.DataFrame) -> pd.DataFrame:
    """
    Pour chaque jour complet présent dans df, identifie :
      - le MAXIMUM absolu de la journée, à condition qu’il ne soit pas à la toute
        dernière mesure (pas à 24 h);
      - le MINIMUM absolu de la journée, à condition qu’il ne soit pas à la toute
        première mesure (pas à 0 h) et qu’il survienne après ce maximum.

    df doit comporter au minimum les colonnes suivantes :
      - 'timestamp' (datetime64[ns]) trié par ordre chronologique,
      - 'inch'      (float) : valeur mesurée de la fissure.

    Retourne un DataFrame à colonnes :
      [ 'day',          # date (YYYY-MM-DD) de la journée
        'time_max',     # horodatage exact (datetime) de l’occurrence du max absolu
        'val_max',      # valeur de 'inch' au maximum absolu
        'time_min',     # horodatage exact (datetime) de l’occurrence du min absolu
        'val_min' ]     # valeur de 'inch' au minimum absolu
    Aucun jour valide ne génère NaN, car on suppose qu’il existe toujours
    au moins deux points « intérieurs » (hors 0 h/24 h).
    """
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")
    df["day"] = df["timestamp"].dt.date

    extrema_list = []
    for day, group in df.groupby("day"):
        if len(group) < 2:
            continue
        first_ts = group["timestamp"].min()
        last_ts = group["timestamp"].max()
        inner = group[(group["timestamp"] > first_ts) & (group["timestamp"] < last_ts)]
        if inner.empty:
            continue

        idx_max = inner["inch"].idxmax()
        ts_max = inner.loc[idx_max, "timestamp"]
        val_max = inner.loc[idx_max, "inch"]

        after_max = inner[inner["timestamp"] > ts_max]
        if after_max.empty:
            continue

        idx_min = after_max["inch"].idxmin()
        ts_min = after_max.loc[idx_min, "timestamp"]
        val_min = after_max.loc[idx_min, "inch"]

        if val_max > val_min:
            extrema_list.append({
                "day": day,
                "time_max": ts_max,
                "val_max": val_max,
                "time_min": ts_min,
                "val_min": val_min
            })

    return pd.DataFrame(extrema_list)


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
