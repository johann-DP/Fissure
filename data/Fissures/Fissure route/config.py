# Répertoires de base
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data_route")
RESULTS_DIR = os.path.join(BASE_DIR, "results_route")

# Chemins des fichiers de données
BASE_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data_route")
MUR_FILE = os.path.join(BASE_DATA_DIR, "mur_route.xlsx")
# WEATHER_FILE = os.path.join(BASE_DATA_DIR, "20250119_20250219.xls")

# Paramètres globaux
MESURE_HOUR = 7
MAX_LAG_HOURS = 15 * 24

# Paramètres pour la parallélisation
USE_PARALLEL = True  # Passez à False pour un mode séquentiel (cachez le backend de Parallel)

# Autres paramètres par défaut (pour la sélection, etc.)
DEFAULT_N_FEATURES = 20
