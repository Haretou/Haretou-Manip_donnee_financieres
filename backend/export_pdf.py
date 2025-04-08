"""
Module pour gérer l'exportation des données en format PDF
Ce module servira dans le cas où l'on souhaite générer les PDF côté serveur
"""

import os
import sys
import json
from datetime import datetime

# Assurez-vous que les imports peuvent fonctionner même si le script est exécuté depuis un autre dossier
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from database import DatabaseManager

class PDFExporter:
    def __init__(self, db_manager=None):
        self.db = db_manager or DatabaseManager()
        if not self.db.connection or not self.db.connection.is_connected():
            self.db.connect()
    
    def generate_sales_report_data(self, date_range=None, store_filter=None, product_filter=None):
        """
        Prépare les données pour un rapport de ventes en PDF
        
        Args:
            date_range (dict, optional): Période de dates à considérer {'start': '2022-01-01', 'end': '2022-12-31'}
            store_filter (list, optional): Liste des magasins à inclure
            product_filter (list, optional): Liste des produits à inclure
            
        Returns:
            dict: Données formatées pour le rapport
        """
        try:
            # Construire la condition WHERE pour la requête SQL
            where_clauses = []
            params = []
            
            if date_range and 'start' in date_range and 'end' in date_range:
                where_clauses.append("date BETWEEN %s AND %s")
                params.extend([date_range['start'], date_range['end']])
            
            if store_filter and isinstance(store_filter, list) and len(store_filter) > 0:
                placeholders = ', '.join(['%s'] * len(store_filter))
                where_clauses.append(f"magasin IN ({placeholders})")
                params.extend(store_filter)
            
            if product_filter and isinstance(product_filter, list) and len(product_filter) > 0:
                placeholders = ', '.join(['%s'] * len(product_filter))
                where_clauses.append(f"produit IN ({placeholders})")
                params.extend(product_filter)
            
            # Construire la requête
            query = "SELECT * FROM ventes"
            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)
            
            # Exécuter la requête
            results = self.db.fetch_all(query, params)
            
            if not results:
                return {"error": "Aucune donnée trouvée pour les critères spécifiés."}
            
            # Organiser les données
            total_sales = 0
            sales_by_store = {}
            sales_by_product = {}
            sales_by_date = {}
            
            for sale in results:
                # Calculer le montant total
                amount = float(sale['quantite']) * float(sale['prix_unitaire'])
                total_sales += amount
                
                # Ventes par magasin
                store = sale['magasin']
                if store not in sales_by_store:
                    sales_by_store[store] = {'quantity': 0, 'amount': 0}
                sales_by_store[store]['quantity'] += int(sale['quantite'])
                sales_by_store[store]['amount'] += amount
                
                # Ventes par produit
                product = sale['produit']
                if product not in sales_by_product:
                    sales_by_product[product] = {'quantity': 0, 'amount': 0}
                sales_by_product[product]['quantity'] += int(sale['quantite'])
                sales_by_product[product]['amount'] += amount
                
                # Ventes par date
                date_str = sale['date'].strftime('%Y-%m')
                if date_str not in sales_by_date:
                    sales_by_date[date_str] = 0
                sales_by_date[date_str] += amount
            
            # Convertir les dictionnaires en listes pour faciliter le tri
            stores_list = [{'name': k, **v} for k, v in sales_by_store.items()]
            products_list = [{'name': k, **v} for k, v in sales_by_product.items()]
            
            # Trier par montant décroissant
            stores_list.sort(key=lambda x: x['amount'], reverse=True)
            products_list.sort(key=lambda x: x['amount'], reverse=True)
            
            # Préparer les données de tendance mensuelle
            trend_data = [{'period': k, 'amount': v} for k, v in sales_by_date.items()]
            trend_data.sort(key=lambda x: x['period'])
            
            # Assembler les données du rapport
            report_data = {
                'date_generated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'total_sales': total_sales,
                'sales_by_store': stores_list,
                'sales_by_product': products_list,
                'monthly_trend': trend_data
            }
            
            return report_data
            
        except Exception as e:
            print(f"Erreur lors de la génération des données du rapport: {e}")
            return {"error": str(e)}
    
    def export_pdf(self, output_path, data=None, options=None):
        """
        Génère un fichier PDF à partir des données
        
        Cette méthode est un placeholder pour l'intégration future d'une bibliothèque
        de génération de PDF côté serveur comme ReportLab
        
        Args:
            output_path (str): Chemin où sauvegarder le PDF
            data (dict, optional): Données à inclure dans le PDF
            options (dict, optional): Options de mise en page
            
        Returns:
            str: Chemin du fichier généré ou message d'erreur
        """
        try:
            # Si aucune donnée n'est fournie, générer des données par défaut
            if not data:
                data = self.generate_sales_report_data()
            
            # Écrire les données en JSON comme solution temporaire
            # Dans une implémentation réelle, nous utiliserions ReportLab ou WeasyPrint
            json_path = output_path.replace('.pdf', '.json')
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            
            return {
                "status": "success",
                "message": "Les données ont été exportées en JSON. L'exportation en PDF n'est pas encore implémentée côté serveur.",
                "json_path": json_path
            }
        
        except Exception as e:
            print(f"Erreur lors de l'exportation en PDF: {e}")
            return {
                "status": "error",
                "message": f"Erreur lors de l'exportation: {str(e)}"
            }

if __name__ == "__main__":
    # Exemple d'utilisation
    exporter = PDFExporter()
    
    # Exemple avec filtres
    date_range = {'start': '2022-01-01', 'end': '2023-12-31'}
    store_filter = ['Magasin_1', 'Magasin_2']
    
    # Générer les données
    report_data = exporter.generate_sales_report_data(
        date_range=date_range,
        store_filter=store_filter
    )
    
    # Chemin pour le fichier de sortie
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.dirname(script_dir)
    output_path = os.path.join(output_dir, 'rapport_ventes.pdf')
    
    # Exporter les données
    result = exporter.export_pdf(output_path, report_data)
    print(result)
    
    # Fermer la connexion à la base de données
    exporter.db.disconnect()