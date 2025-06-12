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

    Seules les mesures strictement comprises entre la première et la dernière
    observation du jour sont conservées. Les lignes dont la valeur est égale,
    à ``tol`` près, au premier ou au dernier relevé sont retirées afin de
    supprimer les plateaux de bordure.

    La phase initiale strictement croissante et la phase finale, également
    croissante, sont ensuite ignorées pour ne conserver que les valeurs
    intermédiaires, depuis la fin de la première phase jusqu'au début de la
    dernière (points de transition inclus). Les extrema absolus sont recherchés
    dans cette fenêtre centrale : ils peuvent donc survenir juste à la sortie
    de la phase initiale ou au tout début de la phase finale, mais jamais dans
    les paliers frontaliers eux‑mêmes.

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

        t0 = grp["timestamp"].iloc[0]
        t1 = grp["timestamp"].iloc[-1]
        interior = grp[(grp["timestamp"] > t0) & (grp["timestamp"] < t1)].copy()
        if interior.empty:
            continue

        # Retire les éventuels plateaux de bordure (même valeur qu'en 1ère ou
        # dernière mesure du jour)
        first_val = grp["inch"].iloc[0]
        last_val = grp["inch"].iloc[-1]
        interior = interior[~np.isclose(interior["inch"], first_val, atol=tol)]
        interior = interior[~np.isclose(interior["inch"], last_val, atol=tol)]
        if interior.empty:
            continue

        vals = interior["inch"].to_numpy()
        if len(vals) < 2:
            continue

        diffs = np.diff(vals)

        # -- fin de la première phase croissante (index du dernier diff > 0)
        if (diffs <= 0).any():
            first_down = np.argmax(diffs <= 0)
        else:
            # pas de cassure : journée monotone, ignorer
            continue

        # -- début de la dernière phase croissante (index après la dernière cassure)
        if (diffs[::-1] <= 0).any():
            last_non_inc = len(diffs) - np.argmax(diffs[::-1] <= 0) - 1
        else:
            continue

        if last_non_inc < first_down:
            continue

        interior_mid = interior.iloc[first_down : last_non_inc + 1]
        if interior_mid.empty:
            continue

        val_max = interior_mid["inch"].max()
        time_max = interior_mid.loc[interior_mid["inch"].idxmax(), "timestamp"]

        val_min = interior_mid["inch"].min()
        time_min = interior_mid.loc[interior_mid["inch"].idxmin(), "timestamp"]

        records.append(
            {
                "day": day,
                "time_max": time_max,
                "val_max": val_max,
                "time_min": time_min,
                "val_min": val_min,
            }
        )

    return pd.DataFrame(records)


def get_extreme_half_hours(df_day_half_mean, df_day_half_median):
    """
    Récupère, pour chaque jour, l'heure (en demi-heure décimale) où se produit
    le max/min dans df_day_half_mean et df_day_half_median.
    """
    max_half_times_mean = df_day_half_mean.groupby("day").apply(
        lambda grp: grp.loc[grp["inch"].idxmax(), "half_hour"]
    )
    min_half_times_mean = df_day_half_mean.groupby("day").apply(
        lambda grp: grp.loc[grp["inch"].idxmin(), "half_hour"]
    )
    max_half_times_median = df_day_half_median.groupby("day").apply(
        lambda grp: grp.loc[grp["inch"].idxmax(), "half_hour"]
    )
    min_half_times_median = df_day_half_median.groupby("day").apply(
        lambda grp: grp.loc[grp["inch"].idxmin(), "half_hour"]
    )

    return {
        "max_half_times_mean": max_half_times_mean,
        "min_half_times_mean": min_half_times_mean,
        "max_half_times_median": max_half_times_median,
        "min_half_times_median": min_half_times_median,
    }
