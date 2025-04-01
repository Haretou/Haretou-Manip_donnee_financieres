"""
Opérations de base de données pour l'application de vente
"""
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import pandas as pd
from config import DB_CONFIG

class DatabaseManager:
    def __init__(self):
        """Initialise le gestionnaire de base de données"""
        self.connection = None
        self.connect()
    
    def connect(self):
        """Établit une connexion à la base de données"""
        try:
            self.connection = mysql.connector.connect(
                host=DB_CONFIG['host'],
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password'],
                database=DB_CONFIG['database'],
                port=DB_CONFIG['port']
            )
            print("Connexion à la base de données établie avec succès")
        except Error as e:
            print(f"Erreur lors de la connexion à la base de données: {e}")
    
    def disconnect(self):
        """Ferme la connexion à la base de données"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Connexion à la base de données fermée")
    
    def execute_query(self, query, params=None):
        """Exécute une requête SQL"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if query.strip().upper().startswith(("INSERT", "UPDATE", "DELETE")):
                self.connection.commit()
                return cursor.lastrowid
            else:
                return cursor.fetchall()
        except Error as e:
            print(f"Erreur lors de l'exécution de la requête: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
    
    def import_csv_to_db(self, csv_file):
        """Importe les données d'un fichier CSV dans la base de données"""
        try:
            # Lire le fichier CSV
            df = pd.read_csv(csv_file)
            
            # Insérer les magasins uniques
            magasins = df['Magasin'].unique()
            magasin_id_map = {}
            for magasin in magasins:
                # Vérifier si le magasin existe déjà
                result = self.execute_query("SELECT id FROM magasins WHERE nom = %s", (magasin,))
                if result:
                    magasin_id_map[magasin] = result[0]['id']
                else:
                    # Insérer le nouveau magasin
                    magasin_id = self.execute_query("INSERT INTO magasins (nom) VALUES (%s)", (magasin,))
                    magasin_id_map[magasin] = magasin_id
            
            # Insérer les produits uniques
            produits = df['Produit'].unique()
            produit_id_map = {}
            for produit in produits:
                # Vérifier si le produit existe déjà
                result = self.execute_query("SELECT id FROM produits WHERE nom = %s", (produit,))
                if result:
                    produit_id_map[produit] = result[0]['id']
                else:
                    # Insérer le nouveau produit
                    produit_id = self.execute_query("INSERT INTO produits (nom) VALUES (%s)", (produit,))
                    produit_id_map[produit] = produit_id
            
            # Insérer les ventes
            for _, row in df.iterrows():
                date_str = row['Date']
                # Convertir la date au format YYYY-MM-DD
                try:
                    # Si c'est déjà une date formatée
                    if "." in date_str:  # Format avec millisecondes
                        date_obj = datetime.strptime(date_str.split('.')[0], "%Y-%m-%d %H:%M:%S")
                    else:
                        date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    # Tenter un autre format courant
                    try:
                        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                    except ValueError:
                        print(f"Format de date non reconnu: {date_str}")
                        continue
                
                date_formatted = date_obj.strftime("%Y-%m-%d")
                magasin_id = magasin_id_map[row['Magasin']]
                produit_id = produit_id_map[row['Produit']]
                quantite = row['Quantité vendue']
                prix_unitaire = row['Prix unitaire']
                
                # Vérifier si cette vente existe déjà (même magasin, produit et date)
                result = self.execute_query(
                    "SELECT id FROM ventes WHERE date = %s AND magasin_id = %s AND produit_id = %s",
                    (date_formatted, magasin_id, produit_id)
                )
                
                if not result:
                    # Insérer la nouvelle vente
                    self.execute_query(
                        "INSERT INTO ventes (date, magasin_id, produit_id, quantite, prix_unitaire) VALUES (%s, %s, %s, %s, %s)",
                        (date_formatted, magasin_id, produit_id, quantite, prix_unitaire)
                    )
            
            print(f"Importation réussie: {len(df)} enregistrements traités")
            return True
        except Exception as e:
            print(f"Erreur lors de l'importation des données: {e}")
            return False
    
    # -------------------- Requêtes pour l'analyse des ventes --------------------
    
    def get_total_sales_by_store(self):
        """Récupère le total des ventes par magasin"""
        query = """
        SELECT m.nom as magasin, SUM(v.quantite * v.prix_unitaire) as total_ventes
        FROM ventes v
        JOIN magasins m ON v.magasin_id = m.id
        GROUP BY m.nom
        ORDER BY total_ventes DESC
        """
        return self.execute_query(query)
    
    def get_total_sales_by_product(self):
        """Récupère le total des ventes par produit"""
        query = """
        SELECT p.nom as produit, SUM(v.quantite * v.prix_unitaire) as total_ventes,
               SUM(v.quantite) as quantite_totale
        FROM ventes v
        JOIN produits p ON v.produit_id = p.id
        GROUP BY p.nom
        ORDER BY total_ventes DESC
        """
        return self.execute_query(query)
    
    def get_monthly_sales(self):
        """Récupère les ventes mensuelles"""
        query = """
        SELECT DATE_FORMAT(date, '%Y-%m') as mois, 
               SUM(quantite * prix_unitaire) as total_ventes
        FROM ventes
        GROUP BY DATE_FORMAT(date, '%Y-%m')
        ORDER BY mois
        """
        return self.execute_query(query)
    
    def get_product_performance_by_store(self, product_id=None):
        """Récupère la performance d'un produit par magasin"""
        if product_id:
            query = """
            SELECT m.nom as magasin, p.nom as produit,
                   SUM(v.quantite) as quantite_totale,
                   SUM(v.quantite * v.prix_unitaire) as total_ventes
            FROM ventes v
            JOIN magasins m ON v.magasin_id = m.id
            JOIN produits p ON v.produit_id = p.id
            WHERE v.produit_id = %s
            GROUP BY m.nom, p.nom
            ORDER BY total_ventes DESC
            """
            return self.execute_query(query, (product_id,))
        else:
            query = """
            SELECT m.nom as magasin, p.nom as produit,
                   SUM(v.quantite) as quantite_totale,
                   SUM(v.quantite * v.prix_unitaire) as total_ventes
            FROM ventes v
            JOIN magasins m ON v.magasin_id = m.id
            JOIN produits p ON v.produit_id = p.id
            GROUP BY m.nom, p.nom
            ORDER BY m.nom, total_ventes DESC
            """
            return self.execute_query(query)
    
    def get_all_products(self):
        """Récupère tous les produits"""
        query = "SELECT id, nom FROM produits ORDER BY nom"
        return self.execute_query(query)
    
    def get_all_stores(self):
        """Récupère tous les magasins"""
        query = "SELECT id, nom FROM magasins ORDER BY nom"
        return self.execute_query(query)
    
    def get_sales_data_for_dashboard(self, start_date=None, end_date=None):
        """Récupère les données de ventes pour le tableau de bord"""
        if start_date and end_date:
            query = """
            SELECT v.date, m.nom as magasin, p.nom as produit, 
                   v.quantite, v.prix_unitaire, (v.quantite * v.prix_unitaire) as total
            FROM ventes v
            JOIN magasins m ON v.magasin_id = m.id
            JOIN produits p ON v.produit_id = p.id
            WHERE v.date BETWEEN %s AND %s
            ORDER BY v.date DESC
            LIMIT 1000
            """
            return self.execute_query(query, (start_date, end_date))
        else:
            query = """
            SELECT v.date, m.nom as magasin, p.nom as produit, 
                   v.quantite, v.prix_unitaire, (v.quantite * v.prix_unitaire) as total
            FROM ventes v
            JOIN magasins m ON v.magasin_id = m.id
            JOIN produits p ON v.produit_id = p.id
            ORDER BY v.date DESC
            LIMIT 1000
            """
            return self.execute_query(query)
    
    def get_product_sales_over_time(self, product_id):
        """Récupère les ventes d'un produit au fil du temps"""
        query = """
        SELECT DATE_FORMAT(v.date, '%Y-%m') as mois, 
               SUM(v.quantite) as quantite_totale,
               SUM(v.quantite * v.prix_unitaire) as total_ventes
        FROM ventes v
        WHERE v.produit_id = %s
        GROUP BY DATE_FORMAT(v.date, '%Y-%m')
        ORDER BY mois
        """
        return self.execute_query(query, (product_id,))
    
    def get_store_sales_over_time(self, store_id):
        """Récupère les ventes d'un magasin au fil du temps"""
        query = """
        SELECT DATE_FORMAT(v.date, '%Y-%m') as mois, 
               SUM(v.quantite * v.prix_unitaire) as total_ventes
        FROM ventes v
        WHERE v.magasin_id = %s
        GROUP BY DATE_FORMAT(v.date, '%Y-%m')
        ORDER BY mois
        """
        return self.execute_query(query, (store_id,))