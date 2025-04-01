#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module pour l'analyse des données de ventes
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime
import csv
from database import DatabaseManager

class SalesAnalyzer:
    """Classe pour analyser les données de ventes"""
    
    def __init__(self, db_manager=None):
        """Initialise l'analyseur avec un gestionnaire de base de données"""
        self.db = db_manager or DatabaseManager()
        if not self.db.connection or not self.db.connection.is_connected():
            self.db.connect()
    
    def load_data_from_csv(self, csv_file):
        """Charge les données depuis un fichier CSV"""
        try:
            # Lecture du fichier CSV
            df = pd.read_csv(csv_file, encoding='utf-8')
            
            # Nettoyage des noms de colonnes
            df.columns = df.columns.str.strip()
            
            # Gestion des différents formats de colonnes possibles
            if 'Quantité vendue' in df.columns:
                df.rename(columns={'Quantité vendue': 'quantite'}, inplace=True)
            elif 'Quantite vendue' in df.columns:
                df.rename(columns={'Quantite vendue': 'quantite'}, inplace=True)
            
            if 'Prix unitaire' in df.columns:
                df.rename(columns={'Prix unitaire': 'prix_unitaire'}, inplace=True)
            elif 'Prix' in df.columns:
                df.rename(columns={'Prix': 'prix_unitaire'}, inplace=True)
            
            # Conversion des types
            df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y', errors='coerce')
            df['quantite'] = pd.to_numeric(df['quantite'], errors='coerce')
            df['prix_unitaire'] = pd.to_numeric(df['prix_unitaire'].str.replace(',', '.'), errors='coerce')
            
            # Calcul du montant total
            df['montant'] = df['quantite'] * df['prix_unitaire']
            
            return df
        except Exception as e:
            print(f"Erreur lors du chargement du fichier CSV: {e}")
            return None
    
    def load_data_from_db(self):
        """Charge les données depuis la base de données"""
        query = """
        SELECT date, magasin, produit, quantite, prix_unitaire,
               quantite * prix_unitaire AS montant
        FROM ventes
        """
        data = self.db.fetch_all(query)
        return pd.DataFrame(data) if data else None
    
    def calculate_total_sales(self, df=None):
        """Calcule le montant total des ventes"""
        if df is None:
            return self.db.get_total_sales()
        return df['montant'].sum()
    
    def sales_by_store(self, df=None):
        """Analyse les ventes par magasin"""
        if df is None:
            return self.db.get_sales_by_store()
        
        store_sales = df.groupby('Magasin')['montant'].sum().reset_index()
        store_sales.columns = ['magasin', 'total_ventes']
        return store_sales.to_dict('records')
    
    def sales_by_product(self, df=None):
        """Analyse les ventes par produit"""
        if df is None:
            return self.db.get_sales_by_product()
        
        product_sales = df.groupby('Produit').agg({
            'quantite': 'sum',
            'montant': 'sum'
        }).reset_index()
        product_sales.columns = ['produit', 'quantite_totale', 'total_ventes']
        return product_sales.to_dict('records')
    
    def sales_trend(self, df=None, period='M'):
        """Analyse la tendance des ventes (D: quotidien, M: mensuel, Y: annuel)"""
        if df is None:
            return self.db.get_sales_by_date('monthly' if period == 'M' else 'daily' if period == 'D' else 'yearly')
        
        if period == 'D':
            df['periode'] = df['Date'].dt.strftime('%Y-%m-%d')
        elif period == 'M':
            df['periode'] = df['Date'].dt.strftime('%Y-%m')
        else:  # 'Y'
            df['periode'] = df['Date'].dt.strftime('%Y')
        
        trend = df.groupby('periode')['montant'].sum().reset_index()
        trend.columns = ['periode', 'total_ventes']
        return trend.to_dict('records')
    
    def best_selling_products(self, df=None, limit=5):
        """Identifie les produits les plus vendus"""
        if df is None:
            return self.db.get_best_selling_products(limit)
        
        top_products = df.groupby('Produit')['quantite'].sum().reset_index()
        top_products.columns = ['produit', 'quantite_totale']
        top_products = top_products.sort_values('quantite_totale', ascending=False).head(limit)
        return top_products.to_dict('records')
    
    def generate_full_report(self, output_format='json'):
        """Génère un rapport complet d'analyse"""
        # Chargement des données
        df = self.load_data_from_db()
        if df is None:
            print("Impossible de charger les données depuis la base de données.")
            return None
        
        # Préparation du rapport
        report = {
            'date_generation': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_ventes': self.calculate_total_sales(df),
            'ventes_par_magasin': self.sales_by_store(df),
            'ventes_par_produit': self.sales_by_product(df),
            'tendance_mensuelle': self.sales_trend(df, period='M'),
            'produits_populaires': self.best_selling_products(df)
        }
        
        # Exportation du rapport
        if output_format == 'json':
            with open('rapport_ventes.json', 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=4)
            print("Rapport JSON généré: rapport_ventes.json")
        
        elif output_format == 'csv':
            # Export des différentes sections du rapport en CSV
            for section, data in report.items():
                if isinstance(data, list):
                    keys = data[0].keys() if data else []
                    with open(f'rapport_{section}.csv', 'w', newline='', encoding='utf-8') as f:
                        writer = csv.DictWriter(f, fieldnames=keys)
                        writer.writeheader()
                        writer.writerows(data)
            print("Rapports CSV générés dans le dossier courant.")
        
        return report
    
    def export_data_for_dashboard(self):
        """Exporte les données pour le tableau de bord"""
        if not self.db.connection or not self.db.connection.is_connected():
            self.db.connect()
        
        dashboard_data = self.db.get_sales_data_for_dashboard()
        
        with open('../frontend/js/dashboard_data.js', 'w', encoding='utf-8') as f:
            f.write(f"const dashboardData = {json.dumps(dashboard_data, ensure_ascii=False, indent=2)};")
        
        print("Données exportées pour le tableau de bord.")
        return dashboard_data

# Exemple d'utilisation
if __name__ == "__main__":
    analyzer = SalesAnalyzer()
    report = analyzer.generate_full_report(output_format='json')
    analyzer.export_data_for_dashboard()
    
    # Fermeture de la connexion
    analyzer.db.disconnect()