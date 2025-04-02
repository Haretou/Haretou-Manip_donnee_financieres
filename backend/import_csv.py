#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour importer les données CSV dans la base de données MySQL/phpMyAdmin
"""

import csv
import datetime
import mysql.connector
import os
import sys

# Assurez-vous que les imports peuvent fonctionner même si le script est exécuté depuis un autre dossier
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

try:
    from config import DB_CONFIG
except ImportError:
    # Configuration par défaut si le fichier config.py n'est pas disponible
    DB_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'ventes_db'
    }

def format_date(date_str):
    """Convertit une date au format français en format SQL"""
    try:
        # Liste des formats de date possibles, du plus spécifique au plus général
        formats = [
            '%Y-%m-%d %H:%M:%S.%f',  # 2023-12-16 06:32:43.636363640
            '%Y-%m-%d %H:%M:%S',     # 2023-12-16 06:32:43
            '%Y-%m-%dT%H:%M:%S.%f',  # 2023-12-16T06:32:43.636363640 (format ISO)
            '%Y-%m-%dT%H:%M:%S',     # 2023-12-16T06:32:43 (format ISO)
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
                return date_obj.strftime('%Y-%m-%d')  # Retourne au format SQL standard
            except (ValueError, TypeError):
                continue
                
        # Si c'est juste une chaîne de date, tenter un split sur l'espace pour ne garder que la date
        if ' ' in date_str:
            date_part = date_str.split(' ')[0]
            for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y', '%d.%m.%Y']:
                try:
                    date_obj = datetime.datetime.strptime(date_part.strip(), fmt)
                    return date_obj.strftime('%Y-%m-%d')
                except (ValueError, TypeError):
                    continue
                    
        # Si aucun format ne fonctionne
        raise ValueError(f"Format de date non reconnu: {date_str}")
        
    except Exception as e:
        print(f"Erreur lors du formatage de la date {date_str}: {e}")
        return None

def create_tables_if_not_exist(cursor):
    """Crée les tables nécessaires si elles n'existent pas déjà"""
    try:
        # Vérifie si la table 'ventes' existe
        cursor.execute("SHOW TABLES LIKE 'ventes'")
        if cursor.fetchone() is None:
            print("La table 'ventes' n'existe pas. Création de la table...")
            
            # Crée la table ventes
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
    
    # Vérification de l'existence du fichier
    if not os.path.exists(csv_file):
        print(f"Erreur: Le fichier {csv_file} n'existe pas.")
        return
    
    # Connexion à la base de données
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print("Connexion à la base de données réussie!")
        
        # Créer les tables si nécessaire
        if not create_tables_if_not_exist(cursor):
            cursor.close()
            conn.close()
            return
            
    except mysql.connector.Error as err:
        print(f"Erreur de connexion à la base de données: {err}")
        return
    
    # Lecture et importation des données
    try:
        # Déterminer l'encodage du fichier
        encodings = ['utf-8', 'iso-8859-1', 'latin1', 'cp1252']
        
        for encoding in encodings:
            try:
                with open(csv_file, 'r', encoding=encoding) as f:
                    f.read(1024)  # Lire un échantillon pour tester l'encodage
                print(f"Utilisation de l'encodage {encoding}")
                break
            except UnicodeDecodeError:
                continue
        
        with open(csv_file, 'r', encoding=encoding) as f:
            # Détermine le délimiteur
            sample = f.read(1024)
            f.seek(0)
            
            delimiter = ','
            if sample.count(';') > sample.count(','):
                delimiter = ';'
            print(f"Détection du délimiteur: '{delimiter}'")
            
            csv_reader = csv.DictReader(f, delimiter=delimiter)
            count = 0
            
            # Vérifier les noms de colonnes et faire des corrections si nécessaire
            field_names = csv_reader.fieldnames
            print(f"Colonnes détectées: {field_names}")
            
            field_mapping = {}
            expected_fields = ['Date', 'Magasin', 'Produit', 'Quantité vendue', 'Prix unitaire']
            
            for expected in expected_fields:
                if expected in field_names:
                    field_mapping[expected] = expected
                else:
                    # Rechercher des colonnes similaires
                    for field in field_names:
                        if expected.lower() in field.lower():
                            field_mapping[expected] = field
                            break
            
            print(f"Mapping des colonnes: {field_mapping}")
            
            # Vérifier si toutes les colonnes nécessaires sont mappées
            if len(field_mapping) < len(expected_fields):
                missing = [exp for exp in expected_fields if exp not in field_mapping]
                print(f"Colonnes manquantes: {missing}")
                print("Assurez-vous que votre CSV contient ces colonnes.")
                return
            
            for row in csv_reader:
                # Formatage des données
                date = format_date(row[field_mapping['Date']])
                if date is None:
                    print(f"Erreur avec la ligne {count+2}: date invalide")
                    continue
                    
                magasin = row[field_mapping['Magasin']].strip()
                produit = row[field_mapping['Produit']].strip()
                
                # Gestion des différents formats possibles pour quantité et prix
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
                
                # Insertion dans la base de données
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
            
            # Commit des changements
            conn.commit()
            print(f"Importation terminée! {count} lignes importées avec succès.")
    
    except Exception as e:
        print(f"Erreur lors de l'importation: {e}")
    
    finally:
        # Fermeture de la connexion
        cursor.close()
        conn.close()
        print("Connexion fermée.")

if __name__ == "__main__":
    # Déterminer le chemin du fichier CSV
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    
    csv_file = os.path.join(project_dir, 'donnees_ventes.csv')
    
    # Vérifier si un argument est passé (chemin personnalisé)
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    
    print(f"Importation du fichier: {csv_file}")
    
    # Lancer l'importation
    import_data(csv_file)
    print("Script d'importation terminé!")