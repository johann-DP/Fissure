import numpy as np
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from rosely import WindRose


def visualize_normalized_boxplots(df_normalized):
    # Définir une palette de couleurs plus neutre
    neutral_color_scale = [
        "#4C78A8",  # Blue
        "#F58518",  # Orange
        "#E45756",  # Red
        "#72B7B2",  # Teal
        "#54A24B",  # Green
        "#ECAE8C",  # Sand
    ]

    # Transformer le DataFrame pour avoir une colonne pour les catégories
    df_melt = df_normalized.melt(var_name="Variables", value_name="Valeurs")

    # Créer la figure de boxplot avec Plotly Express
    fig = px.box(
        df_melt,
        x="Variables",
        y="Valeurs",
        color="Variables",
        points="all",
        color_discrete_sequence=neutral_color_scale,
    )

    # Mettre à jour les titres et les étiquettes des axes
    fig.update_layout(
        title="Boxplots des variables météorologiques normalisées",
        font=dict(size=20),
        xaxis_title="Variables",
        yaxis_title="Valeurs",
        autosize=True,
        legend_title_font=dict(size=18),
        legend=dict(font=dict(size=10)),
    )

    # Mettre à jour la taille des markers
    fig.update_traces(marker=dict(size=4))

    return fig


def plot_humidity(df_cleaned):
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True)

    # Subplot pour les humidités intérieure et extérieure
    fig.add_trace(
        go.Scatter(
            x=df_cleaned["Time"],
            y=df_cleaned["Indoor Hum(%)"],
            mode="lines",
            name="Indoor Humidity",
            line=dict(color="blue", width=1),
            opacity=0.3,
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=df_cleaned["Time"],
            y=df_cleaned["Indoor Hum(%) MA"],
            mode="lines",
            name="Indoor Humidity MA",
            line=dict(color="blue", width=2),
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=df_cleaned["Time"],
            y=df_cleaned["Outdoor Hum(%)"],
            mode="lines",
            name="Outdoor Humidity",
            line=dict(color="green", width=1),
            opacity=0.3,
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=df_cleaned["Time"],
            y=df_cleaned["Outdoor Hum(%) MA"],
            mode="lines",
            name="Outdoor Humidity MA",
            line=dict(color="green", width=2),
        ),
        row=1,
        col=1,
    )

    # Subplot pour les quantités d'eau par mètre cube intérieur
    fig.add_trace(
        go.Scatter(
            x=df_cleaned["Time"],
            y=df_cleaned["Indoor Water Content (g/m³)"],
            mode="lines",
            name="Indoor Water Content",
            line=dict(color="lightblue", width=1),
            opacity=0.3,
        ),
        row=2,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=df_cleaned["Time"],
            y=df_cleaned["Indoor Water Content (g/m³) MA"],
            mode="lines",
            name="Indoor Water Content MA",
            line=dict(color="lightblue", width=2),
        ),
        row=2,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=df_cleaned["Time"],
            y=df_cleaned["Indoor Water Content Max (g/m³)"],
            mode="lines",
            name="Indoor Water Content Max",
            line=dict(color="orange", width=1),
            opacity=0.3,
        ),
        row=2,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=df_cleaned["Time"],
            y=df_cleaned["Indoor Water Content Max (g/m³) MA"],
            mode="lines",
            name="Indoor Water Content Max MA",
            line=dict(color="orange", width=2),
        ),
        row=2,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=df_cleaned["Time"],
            y=df_cleaned["Indoor Water Content Min (g/m³)"],
            mode="lines",
            name="Indoor Water Content Min",
            line=dict(color="darkblue", width=1),
            opacity=0.3,
        ),
        row=2,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=df_cleaned["Time"],
            y=df_cleaned["Indoor Water Content Min (g/m³) MA"],
            mode="lines",
            name="Indoor Water Content Min MA",
            line=dict(color="darkblue", width=2),
        ),
        row=2,
        col=1,
    )

    # Subplot pour les quantités d'eau par mètre cube extérieur
    fig.add_trace(
        go.Scatter(
            x=df_cleaned["Time"],
            y=df_cleaned["Outdoor Water Content (g/m³)"],
            mode="lines",
            name="Outdoor Water Content",
            line=dict(color="lightgreen", width=1),
            opacity=0.3,
        ),
        row=3,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=df_cleaned["Time"],
            y=df_cleaned["Outdoor Water Content (g/m³) MA"],
            mode="lines",
            name="Outdoor Water Content MA",
            line=dict(color="lightgreen", width=2),
        ),
        row=3,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=df_cleaned["Time"],
            y=df_cleaned["Outdoor Water Content Max (g/m³)"],
            mode="lines",
            name="Outdoor Water Content Max",
            line=dict(color="red", width=1),
            opacity=0.3,
        ),
        row=3,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=df_cleaned["Time"],
            y=df_cleaned["Outdoor Water Content Max (g/m³) MA"],
            mode="lines",
            name="Outdoor Water Content Max MA",
            line=dict(color="red", width=2),
        ),
        row=3,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=df_cleaned["Time"],
            y=df_cleaned["Outdoor Water Content Min (g/m³)"],
            mode="lines",
            name="Outdoor Water Content Min",
            line=dict(color="darkgreen", width=1),
            opacity=0.3,
        ),
        row=3,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=df_cleaned["Time"],
            y=df_cleaned["Outdoor Water Content Min (g/m³) MA"],
            mode="lines",
            name="Outdoor Water Content Min MA",
            line=dict(color="darkgreen", width=2),
        ),
        row=3,
        col=1,
    )

    # Mise en forme de la disposition de la figure
    fig.update_layout(
        title="Évolution de l'humidité et des quantités d'eau par mètre cube d'air",
        height=1100,
        showlegend=True,
        legend=dict(font=dict(size=10)),
        font=dict(size=20),
    )

    fig.update_yaxes(title_text="Humidity (%)", row=1, col=1)
    fig.update_yaxes(title_text="Indoor Water Content (g/m³)", row=2, col=1)
    fig.update_yaxes(title_text="Outdoor Water Content (g/m³)", row=3, col=1)
    fig.update_xaxes(title_text="Time", row=3, col=1)

    return fig


def plot_temperature_extremes(df_cleaned):
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df_cleaned["Time"],
            y=df_cleaned["Indoor Tem.Max(°C)"],
            mode="lines",
            name="Indoor Max Temperature",
            line=dict(color="blue", width=1),
            opacity=0.3,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df_cleaned["Time"],
            y=df_cleaned["Indoor Tem.Max(°C) MA"],
            mode="lines",
            name="Indoor Max Temperature MA",
            line=dict(color="blue", width=2),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df_cleaned["Time"],
            y=df_cleaned["Indoor Tem.Min(°C)"],
            mode="lines",
            name="Indoor Min Temperature",
            line=dict(color="green", width=1),
            opacity=0.3,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df_cleaned["Time"],
            y=df_cleaned["Indoor Tem.Min(°C) MA"],
            mode="lines",
            name="Indoor Min Temperature MA",
            line=dict(color="green", width=2),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df_cleaned["Time"],
            y=df_cleaned["Outdoor Tem.Max(°C)"],
            mode="lines",
            name="Outdoor Max Temperature",
            line=dict(color="purple", width=1),
            opacity=0.3,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df_cleaned["Time"],
            y=df_cleaned["Outdoor Tem.Max(°C) MA"],
            mode="lines",
            name="Outdoor Max Temperature MA",
            line=dict(color="purple", width=2),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df_cleaned["Time"],
            y=df_cleaned["Outdoor Tem.Min(°C)"],
            mode="lines",
            name="Outdoor Min Temperature",
            line=dict(color="orange", width=1),
            opacity=0.3,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df_cleaned["Time"],
            y=df_cleaned["Outdoor Tem.Min(°C) MA"],
            mode="lines",
            name="Outdoor Min Temperature MA",
            line=dict(color="orange", width=2),
        )
    )

    fig.update_layout(
        title="Évolution des températures maximales et minimales",
        xaxis_title="Time",
        yaxis_title="Temperature (°C)",
        font=dict(size=20),
        legend=dict(font=dict(size=10)),
        autosize=True,
        height=None,
        width=None,
    )

    return fig


def plot_precipitation(df_cleaned):
    fig = go.Figure()

    # Ajout de la trace pour les précipitations horaires avec une couleur bleue standard
    fig.add_trace(
        go.Scatter(
            x=df_cleaned["Time"],
            y=df_cleaned["Rainfull(Hour)(mm)"],
            mode="lines",
            name="Rainfall per Hour",
            line=dict(width=1, color="blue"),
            opacity=0.5,
        )
    )

    # Ajout de la trace pour les précipitations journalières avec une couleur bleu foncé
    fig.add_trace(
        go.Scatter(
            x=df_cleaned["Time"],
            y=df_cleaned["Rainfull(Day)(mm)"],
            mode="lines",
            name="Rainfall per Day",
            line=dict(width=2, color="darkblue"),
        )
    )

    fig.update_layout(
        title="Évolution des précipitations (échelle log)",
        font=dict(size=20),
        xaxis_title="Time",
        yaxis_title="Rainfall (mm)",
        yaxis_type="log",
        legend=dict(font=dict(size=10)),
        autosize=True,
    )

    return fig


def plot_wind_speed_direction(df_cleaned):
    # Graphique pour la vitesse du vent
    fig1 = go.Figure()
    fig1.add_trace(
        go.Scatter(
            x=df_cleaned["Time"],
            y=df_cleaned["Wind speed(km/h)"],
            mode="lines",
            name="Wind Speed",
            line=dict(color="red", width=1),
            opacity=0.15,
        )
    )
    fig1.add_trace(
        go.Scatter(
            x=df_cleaned["Time"],
            y=df_cleaned["Wind speed(km/h) MA"],
            mode="lines",
            name="Wind Speed MA",
            line=dict(color="red", width=2),
            opacity=0.5,
        )
    )

    fig1.update_layout(
        title="Évolution de la vitesse du vent",
        font=dict(size=20),
        xaxis_title="Time",
        yaxis_title="Wind Speed (km/h)",
        legend=dict(font=dict(size=10)),
        autosize=True,
    )

    # # Graphique pour la direction du vent avec un subplot supplémentaire pour l'angle
    # fig2 = make_subplots(rows=2, cols=1, vertical_spacing=0.1)
    #
    # # Traces pour sinus et cosinus
    # fig2.add_trace(
    #     go.Scatter(
    #         x=df_cleaned["Time"],
    #         y=df_cleaned["Wind direction sin"],
    #         mode="lines",
    #         name="Wind Direction Sin",
    #         line=dict(color="blue", width=1),
    #         opacity=0.15,
    #     ),
    #     row=2,
    #     col=1,
    # )
    # fig2.add_trace(
    #     go.Scatter(
    #         x=df_cleaned["Time"],
    #         y=df_cleaned["Wind direction sin MA"],
    #         mode="lines",
    #         name="Wind Direction Sin MA",
    #         line=dict(color="blue", width=2),
    #     ),
    #     row=2,
    #     col=1,
    # )
    # fig2.add_trace(
    #     go.Scatter(
    #         x=df_cleaned["Time"],
    #         y=df_cleaned["Wind direction cos"],
    #         mode="lines",
    #         name="Wind Direction Cos",
    #         line=dict(color="green", width=1),
    #         opacity=0.15,
    #     ),
    #     row=2,
    #     col=1,
    # )
    # fig2.add_trace(
    #     go.Scatter(
    #         x=df_cleaned["Time"],
    #         y=df_cleaned["Wind direction cos MA"],
    #         mode="lines",
    #         name="Wind Direction Cos MA",
    #         line=dict(color="green", width=2),
    #     ),
    #     row=2,
    #     col=1,
    # )
    #
    # # Trace pour l'angle de direction du vent
    # fig2.add_trace(
    #     go.Scatter(
    #         x=df_cleaned["Time"],
    #         y=df_cleaned["Wind direction"],
    #         mode="lines",
    #         name="Wind Direction",
    #         line=dict(color="darkblue", width=2),
    #         opacity=0.15,
    #     ),
    #     row=1,
    #     col=1,
    # )
    # fig2.add_trace(
    #     go.Scatter(
    #         x=df_cleaned["Time"],
    #         y=df_cleaned["Wind direction MA"],
    #         mode="lines",
    #         name="Wind Direction MA",
    #         line=dict(color="darkblue", width=2),
    #         opacity=0.5,
    #     ),
    #     row=1,
    #     col=1,
    # )
    #
    # fig2.update_layout(
    #     title="Analyse détaillée de la direction du vent",
    #     font=dict(size=20),
    #     legend=dict(font=dict(size=10)),
    #     autosize=True,
    # )
    #
    # fig2.update_xaxes(title_text="Date", row=2, col=1)
    # fig2.update_yaxes(title_text="Direction (sin et cos)", row=2, col=1)
    # fig2.update_yaxes(title_text="Angle (°)", row=1, col=1)

    # Creating the plotly wind rose figure

    fig2 = go.Figure()

    # Conversion des degrés en radians pour la visualisation
    df_cleaned['Wind direction radians'] = np.deg2rad(df_cleaned['Wind direction'])

    # Ajouter la trace principale pour la direction et la vitesse du vent
    fig2.add_trace(go.Scatterpolar(
        r=np.log1p(df_cleaned['Wind speed(km/h)']),  # Échelle logarithmique pour la vitesse du vent
        theta=-np.degrees(df_cleaned['Wind direction radians']),  # Conversion en degrés avec inversion de l'axe
        mode='markers',
        name='Wind Speed and Direction',
        marker=dict(
            color=df_cleaned['Wind speed(km/h)'],  # Couleur en fonction de la vitesse du vent
            colorscale='thermal',
            reversescale=True,
            cmin=0,
            cmax=df_cleaned['Wind speed(km/h)'].max(),
            size=10,  # Taille des marqueurs
            opacity=(df_cleaned['Wind speed(km/h)'] - df_cleaned['Wind speed(km/h)'].min()) / (df_cleaned['Wind speed(km/h)'].max() - df_cleaned['Wind speed(km/h)'].min()) * (1 - np.exp(-0.5*df_cleaned['Wind speed(km/h)'])),
            colorbar=dict(
                title=dict(text="Wind Speed (km/h)", side="right", font=dict(size=18)),  # Titre de la barre de couleur
                tickvals=[1, 2, 5, 10, 15],  # Valeurs correspondant à l'échelle log
                ticktext=[" 1", " 2", " 5", " 10", "15"],  # Textes correspondants
                thickness=50,  # Épaisseur de la barre de couleur
                len=0.8,  # Longueur de la barre de couleur
                x=0.85,
            ),
        ),
    ))

    # Identification des 5 valeurs les plus élevées de vitesse du vent
    top_5_speeds = df_cleaned.nlargest(5, 'Wind speed(km/h)')

    # Ajout d'une trace Scatterpolar pour les annotations des 5 valeurs les plus fortes
    fig2.add_trace(
        go.Scatterpolar(
            r=np.log1p(top_5_speeds["Wind speed(km/h)"] - 2),  # Appliquer une échelle logarithmique pour le rayon
            theta=-np.degrees(top_5_speeds['Wind direction radians']),  # Convertir les radians en degrés
            mode="text",
            text=[f"{speed:.1f} km/h<br>{date.strftime('%Y-%m-%d')}" for speed, date in zip(top_5_speeds['Wind speed(km/h)'], top_5_speeds['Time'])],  # Texte de l'annotation
            textposition=["bottom left", "top left", "bottom left", "bottom left", "bottom left"],
            textfont=dict(size=12, color="black"),
            showlegend=False
        )
    )

    # Mise à jour de la mise en page pour une meilleure lisibilité et esthétique
    fig2.update_layout(
        width=2800,
        height=1350,
        title=dict(
            text="Visualisation radiale de la direction et de la vitesse du vent",
            font=dict(size=26),  # Taille du titre
            # x=0.5,  # Centrer le titre
            y=0.98
        ),
        polar=dict(
            domain=dict(
                x=[0, 1],
                y=[0, 0.95]
            ),
            radialaxis=dict(
                range=[0, np.log1p(df_cleaned['Wind speed(km/h)'].max())],  # Échelle logarithmique pour l'axe radial
                tickvals=np.log1p([1, 2, 5, 10, 20, 50]),  # Ticks correspondant à une échelle logarithmique
                ticktext=[" 1", " 2", " 5", " 10", " 20", " 50"],  # Textes des ticks pour plus de clarté
                showline=True,
                linewidth=1.5,
                tickangle=45,  # Orientation des étiquettes des ticks
                tickfont=dict(size=14, color='blue'),  # Taille et couleur des étiquettes des ticks
                gridcolor="blue",  # Couleur de la grille
                gridwidth=0.7,  # Épaisseur de la grille
            ),
            angularaxis=dict(
                tickvals=[0, 45, 90, 135, 180, 225, 270, 315],  # Points cardinaux
                ticktext=["N", "NE", "E", "SE", "S", "SW", "W", "NW"],  # Étiquettes des directions
                direction="clockwise",  # Sens de rotation conforme à la direction du vent
                rotation=90,  # Rotation pour aligner le 0° vers le haut
                tickfont=dict(size=20, color='blue'),  # Taille et couleur des étiquettes des points cardinaux
                gridcolor="blue",
                gridwidth=0.7,  # Épaisseur de la grille angulaire
            ),
        ),
        margin=dict(l=0, r=20, b=0, t=35),
        legend=dict(
            font=dict(size=12),
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5
        ),
        autosize=False,
    )

    return fig1, fig2


def plot_light_uv(df_cleaned):
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True)

    # Trace for Light Intensity and its moving average
    fig.add_trace(
        go.Scatter(
            x=df_cleaned["Time"],
            y=df_cleaned["Light intensity"],
            mode="lines",
            name="Light Intensity",
            line=dict(color="blue", width=1),
            opacity=0.3,
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=df_cleaned["Time"],
            y=df_cleaned["Light intensity MA"],
            mode="lines",
            name="Light Intensity MA",
            line=dict(color="blue", width=2),
        ),
        row=1,
        col=1,
    )

    # Trace for UV Rating and its moving average
    fig.add_trace(
        go.Scatter(
            x=df_cleaned["Time"],
            y=df_cleaned["UV rating"],
            mode="lines",
            name="UV Rating",
            line=dict(color="green", width=1),
            opacity=0.3,
        ),
        row=2,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=df_cleaned["Time"],
            y=df_cleaned["UV rating MA"],
            mode="lines",
            name="UV Rating MA",
            line=dict(color="green", width=2),
        ),
        row=2,
        col=1,
    )

    # Calculate and plot the ratio differences
    mean_light_intensity = df_cleaned["Light intensity"].mean()
    mean_uv_rating = df_cleaned["UV rating"].mean()
    df_cleaned["light_ratio"] = df_cleaned["Light intensity"] / mean_light_intensity
    df_cleaned["uv_ratio"] = df_cleaned["UV rating"] / mean_uv_rating
    df_cleaned["ratio_diff"] = df_cleaned["light_ratio"] - df_cleaned["uv_ratio"]
    df_cleaned["ratio_diff MA"] = df_cleaned["ratio_diff"].rolling(window=30).mean()

    fig.add_trace(
        go.Scatter(
            x=df_cleaned["Time"],
            y=df_cleaned["ratio_diff"],
            mode="lines",
            name="Ratio Difference",
            line=dict(color="red", width=1),
            opacity=0.3,
        ),
        row=3,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=df_cleaned["Time"],
            y=df_cleaned["ratio_diff MA"],
            mode="lines",
            name="Ratio Difference MA",
            line=dict(color="red", width=2),
        ),
        row=3,
        col=1,
    )

    fig.update_layout(
        title="Évolution de l'intensité lumineuse, de l'indice UV et de leur différence de ratio",
        font=dict(size=20),
        autosize=True,
        height=None,
        width=None,
    )

    fig.update_yaxes(title_text="Light Intensity", row=1, col=1)
    fig.update_yaxes(title_text="UV Rating", row=2, col=1)
    fig.update_yaxes(title_text="Ratio Difference", row=3, col=1)
    fig.update_xaxes(title_text="Time", row=3, col=1)

    return fig


def plot_moving_averages(df_cleaned):
    fig = go.Figure()

    # Traces for Indoor and Outdoor Temperature
    fig.add_trace(
        go.Scatter(
            x=df_cleaned["Time"],
            y=df_cleaned["Indoor Tem(°C)"],
            mode="lines",
            name="Indoor Temperature",
            line=dict(color="blue", width=1),
            opacity=0.3,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df_cleaned["Time"],
            y=df_cleaned["Indoor Tem(°C) MA"],
            mode="lines",
            name="Indoor Temperature MA",
            line=dict(color="blue", width=2),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df_cleaned["Time"],
            y=df_cleaned["Outdoor Tem(°C)"],
            mode="lines",
            name="Outdoor Temperature",
            line=dict(color="green", width=1),
            opacity=0.3,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df_cleaned["Time"],
            y=df_cleaned["Outdoor Tem(°C) MA"],
            mode="lines",
            name="Outdoor Temperature MA",
            line=dict(color="green", width=2),
        )
    )

    fig.update_layout(
        title="Évolution de la température intérieure et extérieure",
        font=dict(size=20),
        xaxis_title="Time",
        yaxis_title="Temperature (°C)",
        legend=dict(font=dict(size=10)),
        autosize=True,
        height=None,
        width=None,
    )

    return fig


def plot_weekly_statistics(df_cleaned, variable_base_names):
    plotly_figures = []

    for base_name in variable_base_names:
        # Filter columns corresponding to statistics of base_name
        stats_columns = [
            col
            for col in df_cleaned.columns
            if "dt" not in col
            and base_name in col
            and any(
                stat in col
                for stat in ["mean", "median", "std", "skew", "calculate_kurtosis"]
            )
        ]
        n = len(stats_columns) // 2
        stats_columns = stats_columns[:n]

        # Create subplots for means, medians, std, skewness, and kurtosis
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True)

        # Plot mean and median on subplot 1
        for col in stats_columns:
            if "mean" in col or "median" in col:
                fig.add_trace(
                    go.Scatter(
                        x=df_cleaned["Time"],
                        y=df_cleaned[col],
                        mode="lines",
                        name=col.split("_")[1],
                    ),
                    row=1,
                    col=1,
                )

        # Plot std on subplot 2
        for col in stats_columns:
            if "std" in col:
                fig.add_trace(
                    go.Scatter(
                        x=df_cleaned["Time"],
                        y=df_cleaned[col],
                        mode="lines",
                        name=col.split("_")[1],
                        line=dict(color="blue"),
                    ),
                    row=2,
                    col=1,
                )

        # Plot skewness and kurtosis on subplot 3
        for col in stats_columns:
            if "skew" in col:
                fig.add_trace(
                    go.Scatter(
                        x=df_cleaned["Time"],
                        y=df_cleaned[col],
                        mode="lines",
                        name=col.split("_")[1],
                        line=dict(dash="dash", color="orange"),
                    ),
                    row=3,
                    col=1,
                )
            if "calculate_kurtosis" in col:
                fig.add_trace(
                    go.Scatter(
                        x=df_cleaned["Time"],
                        y=df_cleaned[col],
                        mode="lines",
                        name=col.split("_")[2],
                        line=dict(dash="dash", color="red"),
                    ),
                    row=3,
                    col=1,
                )

        # Update layout
        fig.update_layout(
            height=1100,
            showlegend=True,
            title_text=f"Évolution des statistiques pour {base_name}",
            font=dict(size=20),
        )

        fig.update_yaxes(title_text="Value", row=1, col=1)
        fig.update_yaxes(title_text="Standard Deviation", row=2, col=1)
        fig.update_yaxes(title_text="Skewness", row=3, col=1, secondary_y=False)
        fig.update_yaxes(title_text="Kurtosis", row=3, col=1, secondary_y=True)
        fig.update_xaxes(title_text="Time", row=3, col=1)

        plotly_figures.append(fig)

    return plotly_figures


def plot_correlation_matrix(df_filtered):
    corr = df_filtered.corr()
    mask = np.triu(np.ones_like(corr, dtype=bool))

    # Apply mask to correlation matrix
    corr = corr.mask(mask)

    # Create a heatmap with Plotly
    fig = ff.create_annotated_heatmap(
        z=corr.values,
        x=list(corr.columns),
        y=list(corr.index),
        annotation_text=corr.round(2).values,
        colorscale="RdBu",
        showscale=True,
        reversescale=True,
        zmin=-1,
        zmax=1,
    )

    # Update layout for better appearance
    fig.update_layout(
        title="Correlation Matrix",
        xaxis_nticks=36,
        autosize=True,
        width=None,
        height=None,
    )

    return fig


def plot_pairplot(
    df, title="Matrices des scatterplots et distributions des variables de base"
):
    variables = df.columns
    num_vars = len(variables)
    fig = make_subplots(
        rows=num_vars,
        cols=num_vars,
        shared_xaxes=False,
        shared_yaxes=False,
        vertical_spacing=0.05,
        horizontal_spacing=0.05,
    )

    # Palette de couleurs
    color_palette = ["#4C78A8", "#F58518", "#E45756", "#72B7B2", "#54A24B", "#ECAE8C"]

    for i, var1 in enumerate(variables):
        color = color_palette[i % len(color_palette)]  # Cycle through colors
        for j, var2 in enumerate(variables):
            if i == j:  # Diagonal, plot histograms
                hist = go.Histogram(
                    x=df[var1], nbinsx=20, name=var1, marker_color=color
                )
                fig.add_trace(hist, row=i + 1, col=j + 1)
            else:  # Off-diagonal, plot scatterplots
                scatter = go.Scattergl(
                    x=df[var2],
                    y=df[var1],
                    mode="markers",
                    marker=dict(size=3, opacity=0.6, color=color),
                    name=f"{var1} vs {var2}",
                )
                fig.add_trace(scatter, row=i + 1, col=j + 1)

                # Update y-axes range for scatterplots based on y data
                y_range = [df[var1].min(), df[var1].max()]
                fig.update_yaxes(range=y_range, row=i + 1, col=j + 1)

            # Update axis labels
            if i == num_vars - 1:
                fig.update_xaxes(title_text=var2, row=i + 1, col=j + 1)
            if j == 0:
                fig.update_yaxes(title_text=var1, row=i + 1, col=j + 1)

    fig.update_layout(height=1100, width=2500, title_text=title, title_font_size=20)
    return fig
