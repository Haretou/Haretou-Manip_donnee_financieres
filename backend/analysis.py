#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Analyse les données de ventes et génère les statistiques pour le tableau de bord
"""

import pandas as pd
import numpy as np
import json
import os
import sys
from datetime import datetime
import csv
from decimal import Decimal

# Assurez-vous que les imports peuvent fonctionner même si le script est exécuté depuis un autre dossier
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from database import DatabaseManager

# Classe d'encodeur JSON personnalisée pour gérer les types Decimal
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

class SalesAnalyzer:
    
    def __init__(self, db_manager=None):
        self.db = db_manager or DatabaseManager()
        if not self.db.connection or not self.db.connection.is_connected():
            self.db.connect()
    
    def load_data_from_csv(self, csv_file):
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
            df['prix_unitaire'] = pd.to_numeric(df['prix_unitaire'].astype(str).str.replace(',', '.'), errors='coerce')
            
            # Calcul du montant total
            df['montant'] = df['quantite'] * df['prix_unitaire']
            
            return df
        except Exception as e:
            print(f"Erreur lors du chargement du fichier CSV: {e}")
            return None
    
    def load_data_from_db(self):
        query = """
        SELECT date, magasin, produit, quantite, prix_unitaire,
               quantite * prix_unitaire AS montant
        FROM ventes
        """
        data = self.db.fetch_all(query)
        
        if not data:
            print("Pas de données disponibles dans la base de données.")
            return None
            
        converted_data = []
        for row in data:
            converted_row = {}
            for key, value in row.items():
                if isinstance(value, Decimal):
                    converted_row[key] = float(value)
                else:
                    converted_row[key] = value
            converted_data.append(converted_row)
            
        df = pd.DataFrame(converted_data)
        
        column_mapping = {
            'date': 'Date',
            'magasin': 'Magasin',
            'produit': 'Produit',
            'quantite': 'quantite',
            'prix_unitaire': 'prix_unitaire',
            'montant': 'montant'
        }
        
        df.rename(columns=column_mapping, inplace=True)
        
        if 'Date' in df.columns and not pd.api.types.is_datetime64_any_dtype(df['Date']):
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            
        return df
    
    def calculate_total_sales(self, df=None):
        if df is None:
            total = self.db.get_total_sales()
            return float(total) if isinstance(total, Decimal) else total
        return float(df['montant'].sum())
    
    def sales_by_store(self, df=None):
        if df is None:
            stores = self.db.get_sales_by_store()
            for store in stores:
                for key, value in store.items():
                    if isinstance(value, Decimal):
                        store[key] = float(value)
            return stores
        
        store_sales = df.groupby('Magasin')['montant'].sum().reset_index()
        
        if 'quantite' in df.columns:
            store_quantity = df.groupby('Magasin')['quantite'].sum().reset_index()
            store_quantity.rename(columns={'quantite': 'quantite_totale'}, inplace=True)
            store_sales = pd.merge(store_sales, store_quantity, on='Magasin', how='left')
        
        store_sales.columns = ['magasin', 'total_ventes'] if len(store_sales.columns) == 2 else ['magasin', 'total_ventes', 'quantite_totale']
        return store_sales.to_dict('records')
    
    def sales_by_product(self, df=None):
        if df is None:
            products = self.db.get_sales_by_product()
            for product in products:
                for key, value in product.items():
                    if isinstance(value, Decimal):
                        product[key] = float(value)
            return products
        
        product_sales = df.groupby('Produit').agg({
            'quantite': 'sum',
            'montant': 'sum'
        }).reset_index()
        
        product_sales.columns = ['produit', 'quantite_totale', 'total_ventes']
        return product_sales.to_dict('records')
    
    def sales_trend(self, df=None, period='M'):
        if df is None:
            trends = self.db.get_sales_by_date('monthly' if period == 'M' else 'daily' if period == 'D' else 'yearly')
            for trend in trends:
                for key, value in trend.items():
                    if isinstance(value, Decimal):
                        trend[key] = float(value)
            return trends
        
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
        if df is None:
            products = self.db.get_best_selling_products(limit)
            # Convertir les valeurs Decimal
            for product in products:
                for key, value in product.items():
                    if isinstance(value, Decimal):
                        product[key] = float(value)
            return products
        
        top_products = df.groupby('Produit')['quantite'].sum().reset_index()
        top_products.columns = ['produit', 'quantite_totale']
        top_products = top_products.sort_values('quantite_totale', ascending=False).head(limit)
        return top_products.to_dict('records')
    
    def convert_decimal_values(self, data):
        if isinstance(data, dict):
            return {k: self.convert_decimal_values(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.convert_decimal_values(item) for item in data]
        elif isinstance(data, Decimal):
            return float(data)
        else:
            return data
    
    def generate_full_report(self, output_format='json'):
        # Chargement des données
        df = self.load_data_from_db()
        if df is None:
            print("Impossible de charger les données depuis la base de données.")
            return None
        
        report = {
            'date_generation': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_ventes': self.calculate_total_sales(df),
            'ventes_par_magasin': self.sales_by_store(df),
            'ventes_par_produit': self.sales_by_product(df),
            'tendance_mensuelle': self.sales_trend(df, period='M'),
            'produits_populaires': self.best_selling_products(df)
        }
        
        report = self.convert_decimal_values(report)
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.dirname(script_dir)
        
        if output_format == 'json':
            report_path = os.path.join(project_dir, 'rapport_ventes.json')
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, cls=DecimalEncoder, ensure_ascii=False, indent=4)
            print(f"Rapport JSON généré: {report_path}")
        
        elif output_format == 'csv':
            for section, data in report.items():
                if isinstance(data, list) and data:
                    keys = data[0].keys()
                    report_path = os.path.join(project_dir, f'rapport_{section}.csv')
                    with open(report_path, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.DictWriter(f, fieldnames=keys)
                        writer.writeheader()
                        writer.writerows(data)
            print("Rapports CSV générés dans le dossier du projet.")
        
        return report
    
    def export_data_for_dashboard(self):
        if not self.db.connection or not self.db.connection.is_connected():
            self.db.connect()
        
        try:
            dashboard_data = self.db.get_sales_data_for_dashboard()
            
            dashboard_data = self.convert_decimal_values(dashboard_data)
            
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_dir = os.path.dirname(script_dir)
            js_dir = os.path.join(project_dir, 'frontend', 'js')
            
            if not os.path.exists(js_dir):
                os.makedirs(js_dir)
                
            js_file = os.path.join(js_dir, 'dashboard_data.js')
            
            with open(js_file, 'w', encoding='utf-8') as f:
                f.write(f"const dashboardData = {json.dumps(dashboard_data, cls=DecimalEncoder, ensure_ascii=False, indent=2)};")
            
            print(f"Données exportées pour le tableau de bord: {js_file}")
            return dashboard_data
            
        except Exception as e:
            print(f"Erreur lors de l'exportation des données pour le tableau de bord: {e}")
            return None

if __name__ == "__main__":
    analyzer = SalesAnalyzer()
    report = analyzer.generate_full_report(output_format='json')
    analyzer.export_data_for_dashboard()
    
    analyzer.db.disconnect()