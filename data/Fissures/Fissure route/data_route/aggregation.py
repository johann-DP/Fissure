# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import Tuple, Dict
import numpy as np
import pandas as pd
from scipy.stats import t


# ---------------------------------------------------------------- daily-stats
def calculate_daily_stats(df: pd.DataFrame):
    """
    Calcule pour chaque jour :
      - min et max en excluant les mesures EXACTEMENT à 0 h et 24 h,
      - mean, median (toujours sur toutes les mesures),
      - day_start, day_end, noon,
      - diff_mm = (max - min)*25.4,
      - diff_global_max_mm et diff_global_min_mm.
    """
    import numpy as np
    import pandas as pd

    # 1) Première passe : on récupère quand même les
    #    min/max/mean/median globaux par jour (sur toutes les mesures).
    daily = (
        df.groupby('day')['inch']
          .agg(['min', 'max', 'mean', 'median'])
          .reset_index()
    )

    # 2) On convertit le champ 'day' en timestamp de début/jour
    daily['day_start'] = pd.to_datetime(daily['day'])
    daily['day_end'] = daily['day_start'] + pd.Timedelta(days=1)
    daily['noon'] = daily['day_start'] + pd.Timedelta(hours=12)

    # 3) Pour chaque jour, on recalcule "min_int" et "max_int" en éliminant
    #    la mesure à 0 h (first_ts) et la mesure à 24 h (last_ts).
    #    Si, après exclusion, il n'y a plus de mesure, on force NaN.
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    for idx, row in daily.iterrows():
        jour = row['day']
        # a) extraire toutes les mesures du jour
        day_df = df[df['day'] == jour]

        # b) repérer la première et la dernière timestamp de la journée
        first_ts = day_df['timestamp'].min()
        last_ts  = day_df['timestamp'].max()

        # c) ne garder QUE les mesures strictement à l'intérieur de la journée
        interior = day_df[
            (day_df['timestamp'] > first_ts) &
            (day_df['timestamp'] < last_ts)
        ]

        if not interior.empty:
            # nouveau min / max à l'intérieur
            daily.at[idx, 'min'] = interior['inch'].min()
            daily.at[idx, 'max'] = interior['inch'].max()
        else:
            # si pas de mesure intérieure (par exemple, une seule mesure ce jour-là)
            daily.at[idx, 'min'] = np.nan
            daily.at[idx, 'max'] = np.nan

    # 4) On recalcule 'diff_mm' sur la base des nouveaux min et max
    daily['diff_mm'] = (daily['max'] - daily['min']) * 25.4

    # 5) On garde les gmin / gmax sur l'ensemble du DataFrame
    gmin = df['inch'].min()
    gmax = df['inch'].max()
    daily['diff_global_max_mm'] = (gmax - daily['max']) * 25.4
    daily['diff_global_min_mm'] = (daily['min'] - gmin) * 25.4

    return daily, gmin, gmax


# ------------------------------------------------------- Student + bootstrap
def calculate_confidence_intervals(df: pd.DataFrame,
                                   daily_stats: pd.DataFrame,
                                   force_normal_test: bool = True):
    ci_lo, ci_hi, normal = [], [], []
    for day, g in df.groupby("day")['inch']:
        n = len(g)
        if n < 3:
            ci_lo.append(np.nan)
            ci_hi.append(np.nan)
            normal.append(False)
            continue
        m, s = g.mean(), g.std(ddof=1)
        margin = t.ppf(0.975, n - 1) * s / np.sqrt(n)
        ci_lo.append(m - margin)
        ci_hi.append(m + margin)
        normal.append(force_normal_test)
    daily_stats = daily_stats.copy()
    daily_stats['ci_lower'] = ci_lo
    daily_stats['ci_upper'] = ci_hi
    daily_stats['normal'] = normal
    return daily_stats


# ---------------------------------------------------- agrégation ½-heure etc.
def aggregate_by_half_hour(df: pd.DataFrame):
    df_mean = df.groupby(['day', 'half_hour'])['inch'].mean().reset_index()
    df_median = df.groupby(['day', 'half_hour'])['inch'].median().reset_index()

    grid = pd.DataFrame({'half_hour': np.arange(0, 24, 0.5)})
    jour_moyen = grid.merge(df_mean.groupby('half_hour')['inch'].mean().reset_index(),
                            on='half_hour', how='left')
    jour_median = grid.merge(df_median.groupby('half_hour')['inch'].median().reset_index(),
                             on='half_hour', how='left')
    return df_mean, df_median, jour_moyen, jour_median


def extract_extremes(df_mean: pd.DataFrame, df_median: pd.DataFrame) -> Dict[str, object]:
    jm = df_mean.groupby('half_hour')['inch'].mean().reset_index()
    jmed = df_median.groupby('half_hour')['inch'].median().reset_index()

    max_hh_mean = jm.loc[jm['inch'].idxmax(), 'half_hour']
    min_hh_mean = jm.loc[jm['inch'].idxmin(), 'half_hour']
    max_hh_med = jmed.loc[jmed['inch'].idxmax(), 'half_hour']
    min_hh_med = jmed.loc[jmed['inch'].idxmin(), 'half_hour']

    return {
        'max_half_mean': max_hh_mean,
        'min_half_mean': min_hh_mean,
        'data_max_mean': df_mean.loc[df_mean['half_hour'] == max_hh_mean, 'inch'],
        'data_min_mean': df_mean.loc[df_mean['half_hour'] == min_hh_mean, 'inch'],
        'max_half_median': max_hh_med,
        'min_half_median': min_hh_med,
        'data_max_median': df_median.loc[df_median['half_hour'] == max_hh_med, 'inch'],
        'data_min_median': df_median.loc[df_median['half_hour'] == min_hh_med, 'inch'],
    }
