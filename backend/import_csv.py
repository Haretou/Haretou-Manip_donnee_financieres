#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour importer les données CSV dans la base de données MySQL/phpMyAdmin
"""

import csv
import datetime
import mysql.connector
from config import DB_CONFIG

def format_date(date_str):
    """Convertit une date au format français en format SQL"""
    try:
        # Essaie de parser différents formats de date possibles
        for fmt in ['%d/%m/%Y', '%Y-%m-%d']:
            try:
                date_obj = datetime.datetime.strptime(date_str, fmt)
                return date_obj.strftime('%Y-%m-%d')
            except ValueError:
                continue
        raise ValueError(f"Format de date non reconnu: {date_str}")
    except Exception as e:
        print(f"Erreur lors du formatage de la date {date_str}: {e}")
        return None

def import_data(csv_file):
    """Importe les données du fichier CSV vers la base de données"""
    
    # Connexion à la base de données
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print("Connexion à la base de données réussie!")
    except mysql.connector.Error as err:
        print(f"Erreur de connexion à la base de données: {err}")
        return
    
    # Lecture et importation des données
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            csv_reader = csv.DictReader(f)
            count = 0
            
            for row in csv_reader:
                # Formatage des données
                date = format_date(row['Date'])
                magasin = row['Magasin']
                produit = row['Produit']
                
                # Gestion des différents formats possibles pour quantité et prix
                try:
                    quantite = int(row['Quantité vendue'].replace(' ', ''))
                except (ValueError, KeyError):
                    try:
                        quantite = int(row['Quantite vendue'].replace(' ', ''))
                    except (ValueError, KeyError):
                        print(f"Erreur avec la ligne {count+1}: impossible de lire la quantité")
                        continue
                
                try:
                    prix = float(row['Prix unitaire'].replace(',', '.').replace(' ', ''))
                except (ValueError, KeyError):
                    try:
                        prix = float(row['Prix'].replace(',', '.').replace(' ', ''))
                    except (ValueError, KeyError):
                        print(f"Erreur avec la ligne {count+1}: impossible de lire le prix")
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
    import_data('donnees_ventes.csv')
    print("Script d'importation terminé!")