# Projet d'Analyse des Ventes

## Description
Ce projet est un système complet de gestion et d'analyse des données de ventes. Il permet d'importer des données CSV, de les stocker dans une base de données MySQL via phpMyAdmin, et de visualiser les informations clés à travers un tableau de bord interactif.

## Technologies utilisées
- **Python** : Pour le backend et le traitement des données
- **MySQL/phpMyAdmin** : Pour la gestion de la base de données
- **HTML/CSS** : Pour l'interface utilisateur
- **JavaScript** : Pour l'interactivité et les visualisations
- **Chart.js** : Pour les graphiques

## Configuration requise
- Python 3.6 ou supérieur
- Serveur MySQL (XAMPP, MAMP ou équivalent pour phpMyAdmin)
- Navigateur web moderne

### 1. Base de données
1. Lancez phpMyAdmin (via MAMP)
2. Créez une nouvelle base de données appelée `ventes_db`
3. Importez le fichier `base_de_donnees/ventes_db.sql`


## Utilisation
1. **Page d'accueil** : Présente un aperçu des fonctionnalités et quelques statistiques clés
2. **Tableau de bord** : Affiche des graphiques détaillés et des tableaux pour analyser les ventes
3. **Importation** : Permet d'importer de nouvelles données CSV
4. **Exportation** : Permet d'exporter les analyses dans différents formats

## Structure des données CSV
Le système attend un fichier CSV avec les colonnes suivantes :
- `Date` : Date de la vente (format JJ/MM/AAAA ou AAAA-MM-JJ)
- `Magasin` : Nom du magasin
- `Produit` : Nom du produit
- `Quantité vendue` : Nombre d'unités vendues
- `Prix unitaire` : Prix unitaire du produit

## Fonctionnalités
- Visualisation des ventes par magasin
- Visualisation des ventes par produit
- Évolution des ventes dans le temps
- Analyse des produits les plus vendus
- Filtrage et recherche des données
- Exportation des rapports

## Note de développement
Ce projet a été conçu pour fonctionner sur un Mac M2 avec Python, phpMyAdmin et les technologies web standards. Il est optimisé pour une utilisation locale et peut être adapté pour un déploiement en production avec des modifications appropriées.