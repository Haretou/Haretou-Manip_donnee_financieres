-- Création de la base de données
CREATE DATABASE IF NOT EXISTS ventes_db;
USE ventes_db;

-- Table des magasins
CREATE TABLE IF NOT EXISTS magasins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(50) NOT NULL UNIQUE
) ENGINE=InnoDB;

-- Table des produits
CREATE TABLE IF NOT EXISTS produits (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(50) NOT NULL UNIQUE
) ENGINE=InnoDB;

-- Table des ventes
CREATE TABLE IF NOT EXISTS ventes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE NOT NULL,
    magasin_id INT NOT NULL,
    produit_id INT NOT NULL,
    quantite INT NOT NULL,
    prix_unitaire DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (magasin_id) REFERENCES magasins(id),
    FOREIGN KEY (produit_id) REFERENCES produits(id)
) ENGINE=InnoDB;

-- Vue pour faciliter les requêtes
CREATE OR REPLACE VIEW vue_ventes AS
SELECT v.id, v.date, m.nom as magasin, p.nom as produit, 
       v.quantite, v.prix_unitaire, (v.quantite * v.prix_unitaire) as total
FROM ventes v
JOIN magasins m ON v.magasin_id = m.id
JOIN produits p ON v.produit_id = p.id;