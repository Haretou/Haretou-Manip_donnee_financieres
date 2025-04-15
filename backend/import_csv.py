"""
Script pour importer les données du fichier CSV vers la base de données MySQL
"""

import csv
import datetime
import mysql.connector
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

try:
    from config import DB_CONFIG
except ImportError:
    DB_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'ventes_db'
    }

def format_date(date_str):
    """Convertit une date au format français en format SQL"""
    try:
        formats = [
            '%Y-%m-%d %H:%M:%S.%f',  
            '%Y-%m-%d %H:%M:%S',     
            '%Y-%m-%dT%H:%M:%S.%f',  
            '%Y-%m-%dT%H:%M:%S',     
            '%d/%m/%Y %H:%M:%S',     # 16/12/2023 06:32:43 (format français avec heure)
            '%d/%m/%Y',              # 16/12/2023 (format français)
            '%Y-%m-%d',              # 2023-12-16 (format SQL)
            '%m/%d/%Y',              # 12/16/2023 (format américain)
            '%d-%m-%Y',              # 16-12-2023 (format avec tirets)
            '%d.%m.%Y'               # 16.12.2023 (format avec points)
        ]

        # Essai de chaque format
        for fmt in formats:
            try:
                date_obj = datetime.datetime.strptime(date_str.strip(), fmt)
                return date_obj.strftime('%Y-%m-%d')  # renvoie en SQL 
            except (ValueError, TypeError):
                continue
                
        if ' ' in date_str:
            date_part = date_str.split(' ')[0]
            for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y', '%d.%m.%Y']:
                try:
                    date_obj = datetime.datetime.strptime(date_part.strip(), fmt)
                    return date_obj.strftime('%Y-%m-%d')
                except (ValueError, TypeError):
                    continue
                    
        raise ValueError(f"Format de date non reconnu: {date_str}")
        
    except Exception as e:
        print(f"Erreur lors du formatage de la date {date_str}: {e}")
        return None

def create_tables_if_not_exist(cursor):
    """Crée les tables nécessaires si elles n'existent pas déjà"""
    try:
        cursor.execute("SHOW TABLES LIKE 'ventes'")
        if cursor.fetchone() is None:
            print("La table 'ventes' n'existe pas. Création de la table...")
            
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS ventes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                date DATE NOT NULL,
                magasin VARCHAR(100) NOT NULL,
                produit VARCHAR(200) NOT NULL,
                quantite INT NOT NULL,
                prix_unitaire DECIMAL(10, 2) NOT NULL,
                INDEX idx_date (date),
                INDEX idx_magasin (magasin),
                INDEX idx_produit (produit)
            ) ENGINE=InnoDB;
            """
            cursor.execute(create_table_sql)
            print("Table 'ventes' créée avec succès!")
            
        return True
    except mysql.connector.Error as err:
        print(f"Erreur lors de la vérification/création des tables: {err}")
        return False

def import_data(csv_file):
    """Importe les données du fichier CSV vers la base de données"""
    
    if not os.path.exists(csv_file):
        print(f"Erreur: Le fichier {csv_file} n'existe pas.")
        return
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print("Connexion à la base de données réussie!")
        
        if not create_tables_if_not_exist(cursor):
            cursor.close()
            conn.close()
            return
            
    except mysql.connector.Error as err:
        print(f"Erreur de connexion à la base de données: {err}")
        return
    
    try:
        encodings = ['utf-8', 'iso-8859-1', 'latin1', 'cp1252']
        
        for encoding in encodings:
            try:
                with open(csv_file, 'r', encoding=encoding) as f:
                    f.read(1024)  
                print(f"Utilisation de l'encodage {encoding}")
                break
            except UnicodeDecodeError:
                continue
        
        with open(csv_file, 'r', encoding=encoding) as f:
            sample = f.read(1024)
            f.seek(0)
            
            delimiter = ','
            if sample.count(';') > sample.count(','):
                delimiter = ';'
            print(f"Détection du délimiteur: '{delimiter}'")
            
            csv_reader = csv.DictReader(f, delimiter=delimiter)
            count = 0
            
            field_names = csv_reader.fieldnames
            print(f"Colonnes détectées: {field_names}")
            
            field_mapping = {}
            expected_fields = ['Date', 'Magasin', 'Produit', 'Quantité vendue', 'Prix unitaire']
            
            for expected in expected_fields:
                if expected in field_names:
                    field_mapping[expected] = expected
                else:
                    for field in field_names:
                        if expected.lower() in field.lower():
                            field_mapping[expected] = field
                            break
            
            print(f"Mapping des colonnes: {field_mapping}")
            
            if len(field_mapping) < len(expected_fields):
                missing = [exp for exp in expected_fields if exp not in field_mapping]
                print(f"Colonnes manquantes: {missing}")
                print("Assurez-vous que votre CSV contient ces colonnes.")
                return
            
            for row in csv_reader:
                date = format_date(row[field_mapping['Date']])
                if date is None:
                    print(f"Erreur avec la ligne {count+2}: date invalide")
                    continue
                    
                magasin = row[field_mapping['Magasin']].strip()
                produit = row[field_mapping['Produit']].strip()
                
                try:
                    quantite_str = row[field_mapping['Quantité vendue']].replace(' ', '').replace(',', '.')
                    quantite = int(float(quantite_str))
                except (ValueError, KeyError):
                    print(f"Erreur avec la ligne {count+2}: impossible de lire la quantité")
                    continue
                
                try:
                    prix_str = row[field_mapping['Prix unitaire']].replace(' ', '').replace(',', '.')
                    prix = float(prix_str)
                except (ValueError, KeyError):
                    print(f"Erreur avec la ligne {count+2}: impossible de lire le prix")
                    continue
                
                sql = """
                INSERT INTO ventes (date, magasin, produit, quantite, prix_unitaire)
                VALUES (%s, %s, %s, %s, %s)
                """
                values = (date, magasin, produit, quantite, prix)
                
                try:
                    cursor.execute(sql, values)
                    count += 1
                    if count % 100 == 0:
                        print(f"{count} lignes importées...")
                except mysql.connector.Error as err:
                    print(f"Erreur lors de l'insertion de la ligne {count+1}: {err}")
                    continue
            
            conn.commit()
            print(f"Importation terminée! {count} lignes importées avec succès.")
    
    except Exception as e:
        print(f"Erreur lors de l'importation: {e}")
    
    finally:
        cursor.close()
        conn.close()
        print("Connexion fermée.")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    
    csv_file = os.path.join(project_dir, 'donnees_ventes.csv')
    
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    
    print(f"Importation du fichier: {csv_file}")
    
    import_data(csv_file)
    print("Script d'importation terminé!")