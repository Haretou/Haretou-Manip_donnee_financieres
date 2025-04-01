"""
Configuration pour la connexion à la base de données
"""

# Configuration de la connexion à la base de données
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',        # À modifier selon votre configuration
    'password': '',        # À modifier selon votre configuration
    'database': 'ventes_db'
}

# Chemin vers le fichier de données
CSV_FILE_PATH = 'donnees_ventes.csv'

# Autres configurations
DATE_FORMAT = '%Y-%m-%d'