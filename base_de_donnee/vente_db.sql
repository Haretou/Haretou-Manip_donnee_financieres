-- Script SQL pour créer la base de données et les tables du projet de ventes
-- À importer dans phpMyAdmin

-- Création de la base de données
CREATE DATABASE IF NOT EXISTS ventes_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE ventes_db;

-- Création de la table principale des ventes
CREATE TABLE IF NOT EXISTS ventes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE NOT NULL,
    magasin VARCHAR(100) NOT NULL,
    produit VARCHAR(200) NOT NULL,
    quantite INT NOT NULL,
    prix_unitaire DECIMAL(10, 2) NOT NULL,
    -- Indices pour améliorer les performances des requêtes
    INDEX idx_date (date),
    INDEX idx_magasin (magasin),
    INDEX idx_produit (produit)
) ENGINE=InnoDB;

-- Table pour les magasins (pour référence future)
CREATE TABLE IF NOT EXISTS magasins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) NOT NULL UNIQUE,
    adresse VARCHAR(255),
    telephone VARCHAR(20),
    email VARCHAR(100),
    responsable VARCHAR(100),
    date_creation DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Table pour les produits (pour référence future)
CREATE TABLE IF NOT EXISTS produits (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(200) NOT NULL UNIQUE,
    categorie VARCHAR(100),
    description TEXT,
    prix_standard DECIMAL(10, 2),
    unite VARCHAR(20),
    stock_initial INT DEFAULT 0,
    date_creation DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Vues pour faciliter l'analyse des données

-- Vue des ventes par jour
CREATE OR REPLACE VIEW ventes_quotidiennes AS
SELECT 
    DATE(date) AS jour,
    SUM(quantite * prix_unitaire) AS total_ventes,
    COUNT(DISTINCT magasin) AS nb_magasins_actifs,
    COUNT(*) AS nb_transactions
FROM ventes
GROUP BY jour
ORDER BY jour;

-- Vue des ventes par magasin
CREATE OR REPLACE VIEW ventes_par_magasin AS
SELECT 
    magasin,
    COUNT(*) AS nb_transactions,
    SUM(quantite) AS quantite_totale,
    SUM(quantite * prix_unitaire) AS total_ventes,
    AVG(prix_unitaire) AS prix_moyen,
    MIN(date) AS premiere_vente,
    MAX(date) AS derniere_vente
FROM ventes
GROUP BY magasin
ORDER BY total_ventes DESC;

-- Vue des ventes par produit
CREATE OR REPLACE VIEW ventes_par_produit AS
SELECT 
    produit,
    COUNT(*) AS nb_transactions,
    SUM(quantite) AS quantite_totale,
    SUM(quantite * prix_unitaire) AS total_ventes,
    AVG(prix_unitaire) AS prix_moyen,
    COUNT(DISTINCT magasin) AS nb_magasins
FROM ventes
GROUP BY produit
ORDER BY quantite_totale DESC;

-- Vue des meilleures combinaisons magasin-produit
CREATE OR REPLACE VIEW meilleures_combinaisons AS
SELECT 
    magasin,
    produit,
    SUM(quantite) AS quantite_totale,
    SUM(quantite * prix_unitaire) AS total_ventes
FROM ventes
GROUP BY magasin, produit
ORDER BY quantite_totale DESC;

-- Procédure stockée pour générer un rapport mensuel
DELIMITER //
CREATE PROCEDURE rapport_mensuel(IN annee INT, IN mois INT)
BEGIN
    -- Validation des paramètres
    IF annee < 2000 OR annee > 2100 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Année invalide';
    END IF;
    
    IF mois < 1 OR mois > 12 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Mois invalide';
    END IF;
    
    -- Générer le rapport
    SELECT 
        magasin,
        SUM(quantite) AS quantite_totale,
        SUM(quantite * prix_unitaire) AS total_ventes,
        COUNT(DISTINCT date) AS jours_actifs,
        COUNT(DISTINCT produit) AS nb_produits_vendus
    FROM ventes
    WHERE YEAR(date) = annee AND MONTH(date) = mois
    GROUP BY magasin
    ORDER BY total_ventes DESC;
END //
DELIMITER ;

-- Trigger pour vérification de données
DELIMITER //
CREATE TRIGGER verif_ventes_before_insert
BEFORE INSERT ON ventes
FOR EACH ROW
BEGIN
    -- Vérification des valeurs négatives
    IF NEW.quantite <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La quantité doit être positive';
    END IF;
    
    IF NEW.prix_unitaire <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Le prix unitaire doit être positif';
    END IF;
    
    -- Date future
    IF NEW.date > CURDATE() THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La date ne peut pas être dans le futur';
    END IF;
END //
DELIMITER ;

-- Insertion de quelques données de test (à commenter pour la production)
/*
INSERT INTO ventes (date, magasin, produit, quantite, prix_unitaire) VALUES
('2023-01-15', 'Magasin Paris', 'Ordinateur portable', 5, 899.99),
('2023-01-15', 'Magasin Lyon', 'Smartphone', 10, 599.99),
('2023-01-16', 'Magasin Paris', 'Tablette', 8, 349.99),
('2023-01-16', 'Magasin Marseille', 'Écran 4K', 3, 299.99),
('2023-01-17', 'Magasin Lyon', 'Casque audio', 15, 79.99),
('2023-01-17', 'Magasin Paris', 'Smartphone', 7, 649.99),
('2023-01-18', 'Magasin Marseille', 'Ordinateur portable', 4, 1099.99)
*/