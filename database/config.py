"""
Configuration de la base de données MySQL
"""
import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis un fichier .env s'il existe
load_dotenv()

# Configuration de la base de données
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'root'),  # Modifié pour un mot de passe courant avec MAMP
    'database': os.getenv('DB_NAME', 'ventes_db'),
    'port': int(os.getenv('DB_PORT', '8889'))  # Modifié pour le port par défaut de MAMP
}

# Création d'un fichier .env par défaut s'il n'existe pas
def create_env_file():
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write("""# Configuration de la base de données
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=root
DB_NAME=ventes_db
DB_PORT=8889
""")
        print("Fichier .env créé avec succès.")

if __name__ == "__main__":
    create_env_file()