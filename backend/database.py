#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module qui gère toutes les interactions avec la base de données (requêtes, connexions)
"""

import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG

class DatabaseManager:
    
    def __init__(self, config=None):
        self.config = config or DB_CONFIG
        self.connection = None
        self.cursor = None
    
    def connect(self):
        try:
            self.connection = mysql.connector.connect(**self.config)
            if self.connection.is_connected():
                self.cursor = self.connection.cursor(dictionary=True)
                return True
        except Error as e:
            print(f"Erreur lors de la connexion à la base de données: {e}")
            return False
    
    def disconnect(self):
        if self.connection and self.connection.is_connected():
            if self.cursor:
                self.cursor.close()
            self.connection.close()
    
    def execute_query(self, query, params=None, commit=False):
        """Exécute une requête SQL"""
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return None
        
        try:
            self.cursor.execute(query, params or ())
            if commit:
                self.connection.commit()
            return True
        except Error as e:
            print(f"Erreur lors de l'exécution de la requête: {e}")
            return False
    
    def fetch_all(self, query, params=None):
        if not self.execute_query(query, params):
            return []
        
        try:
            return self.cursor.fetchall()
        except Error as e:
            print(f"Erreur lors de la récupération des résultats: {e}")
            return []
    
    def fetch_one(self, query, params=None):
        if not self.execute_query(query, params):
            return None
        
        try:
            return self.cursor.fetchone()
        except Error as e:
            print(f"Erreur lors de la récupération du résultat: {e}")
            return None
    
    # Méthodes spécifiques pour l'application
    
    def get_total_sales(self):
        query = """
        SELECT SUM(quantite * prix_unitaire) AS total_ventes
        FROM ventes
        """
        result = self.fetch_one(query)
        return result['total_ventes'] if result else 0
    
    def get_sales_by_store(self):
        query = """
        SELECT magasin, SUM(quantite * prix_unitaire) AS total_ventes
        FROM ventes
        GROUP BY magasin
        ORDER BY total_ventes DESC
        """
        return self.fetch_all(query)
    
    def get_sales_by_product(self):
        query = """
        SELECT produit, SUM(quantite) AS quantite_totale, 
               SUM(quantite * prix_unitaire) AS total_ventes
        FROM ventes
        GROUP BY produit
        ORDER BY total_ventes DESC
        """
        return self.fetch_all(query)
    
    def get_sales_by_date(self, period='monthly'):
        if period == 'daily':
            date_format = '%Y-%m-%d'
            group_by = 'date'
        elif period == 'monthly':
            date_format = '%Y-%m'
            group_by = "DATE_FORMAT(date, '%Y-%m')"
        else:  # yearly
            date_format = '%Y'
            group_by = "DATE_FORMAT(date, '%Y')"
        
        query = f"""
        SELECT DATE_FORMAT(date, '{date_format}') AS periode,
               SUM(quantite * prix_unitaire) AS total_ventes
        FROM ventes
        GROUP BY {group_by}
        ORDER BY periode
        """
        return self.fetch_all(query)
    
    def get_best_selling_products(self, limit=5):
        query = """
        SELECT produit, SUM(quantite) AS quantite_totale
        FROM ventes
        GROUP BY produit
        ORDER BY quantite_totale DESC
        LIMIT %s
        """
        return self.fetch_all(query, (limit,))
    
    def get_sales_data_for_dashboard(self):
        return {
            'total_sales': self.get_total_sales(),
            'sales_by_store': self.get_sales_by_store(),
            'sales_by_product': self.get_sales_by_product(),
            'monthly_sales': self.get_sales_by_date('monthly'),
            'best_selling_products': self.get_best_selling_products()
        }


# Exemple d'utilisation
if __name__ == "__main__":
    db = DatabaseManager()
    if db.connect():
        print("Connexion réussie!")
        
        # Exemple de requête
        total = db.get_total_sales()
        print(f"Total des ventes: {total} €")
        
        # Fermeture de la connexion
        db.disconnect()
    else:
        print("Échec de la connexion.")