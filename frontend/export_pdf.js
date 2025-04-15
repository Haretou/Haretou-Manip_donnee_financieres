/**
 * Script pour exporter le tableau de bord en PDF
 * Utilise la bibliothèque html2pdf.js
 */

// Fonction principale d'exportation PDF
function exportDashboardToPDF(options = {}) {
    // Options par défaut
    const defaultOptions = {
        filename: 'tableau_de_bord_ventes.pdf',
        includeHeader: true,
        includeCharts: true,
        includeTables: true,
        orientation: 'portrait',
        pageSize: 'a4'
    };

    // Fusion avec les options fournies
    const settings = {...defaultOptions, ...options };

    // Créer un indicateur de chargement
    showLoadingIndicator();

    try {
        // Vérifier que html2pdf est disponible
        if (typeof html2pdf === 'undefined') {
            throw new Error("La bibliothèque html2pdf.js n'est pas disponible");
        }

        // Créer un conteneur pour le PDF
        const container = document.createElement('div');
        container.className = 'pdf-container';
        container.style.position = 'absolute';
        container.style.left = '-9999px';
        container.style.top = '0';
        container.style.backgroundColor = 'white';
        container.style.padding = '20px';
        container.style.width = '210mm'; // Largeur A4
        document.body.appendChild(container);

        // Ajouter l'en-tête
        const header = document.createElement('div');
        header.innerHTML = `
            <h1 style="text-align:center; color:#3498db">Tableau de Bord des Ventes</h1>
            <p style="text-align:center; color:#666">Exporté le ${new Date().toLocaleDateString('fr-FR')} à ${new Date().toLocaleTimeString('fr-FR')}</p>
            <hr style="border:1px solid #3498db; margin-bottom:20px">
        `;
        container.appendChild(header);

        // Ajouter les métriques si demandé
        if (settings.includeHeader) {
            addMetricsToContainer(container);
            addBreakLine(container);
        }

        // Ajouter les graphiques si demandé
        if (settings.includeCharts) {
            addChartsToContainer(container);
            addBreakLine(container);
        }

        // Ajouter les tableaux si demandé
        if (settings.includeTables) {
            addTablesToContainer(container);
        }

        // Créer les options pour html2pdf
        const pdfOptions = {
            margin: [10, 10, 10, 10],
            filename: settings.filename,
            image: { type: 'jpeg', quality: 0.98 },
            html2canvas: { scale: 2, useCORS: true, logging: true },
            jsPDF: { unit: 'mm', format: settings.pageSize, orientation: settings.orientation }
        };

        // Utiliser un timeout pour s'assurer que le DOM est correctement rendu
        setTimeout(() => {
            // Générer le PDF
            html2pdf()
                .set(pdfOptions)
                .from(container)
                .save()
                .then(() => {
                    console.log("PDF généré avec succès");
                    // Nettoyage
                    document.body.removeChild(container);
                    hideLoadingIndicator();
                })
                .catch(err => {
                    console.error("Erreur lors de la génération du PDF:", err);
                    alert("Erreur lors de la génération du PDF.");
                    // Nettoyage même en cas d'erreur
                    document.body.removeChild(container);
                    hideLoadingIndicator();
                });
        }, 500);

    } catch (error) {
        console.error("Erreur:", error);
        alert("Une erreur est survenue: " + error.message);
        hideLoadingIndicator();
    }
}

// Fonction pour ajouter les métriques au conteneur
function addMetricsToContainer(container) {
    const section = document.createElement('div');
    section.innerHTML = '<h2 style="color:#2c3e50; margin-bottom:15px">Métriques principales</h2>';

    // Cloner les métriques du tableau de bord
    const metricsRow = document.querySelector('.metrics-row');
    if (metricsRow) {
        const metricsClone = metricsRow.cloneNode(true);

        // Appliquer des styles spécifiques pour le PDF
        metricsClone.style.display = 'flex';
        metricsClone.style.flexWrap = 'wrap';
        metricsClone.style.justifyContent = 'space-between';

        // Ajuster le style des cartes de métriques
        const cards = metricsClone.querySelectorAll('.metric-card');
        cards.forEach(card => {
            card.style.width = '48%';
            card.style.marginBottom = '10px';
            card.style.padding = '10px';
            card.style.border = '1px solid #ddd';
            card.style.borderRadius = '5px';
        });

        section.appendChild(metricsClone);
    } else {
        section.innerHTML += '<p style="color:red">Impossible de récupérer les métriques</p>';
    }

    container.appendChild(section);
}

// Fonction pour ajouter les graphiques au conteneur
function addChartsToContainer(container) {
    const section = document.createElement('div');
    section.innerHTML = '<h2 style="color:#2c3e50; margin-bottom:15px">Graphiques d\'analyse</h2>';

    // Liste des graphiques à exporter
    const charts = [
        { id: 'salesTrendChart', title: 'Évolution des ventes' },
        { id: 'storesComparisonChart', title: 'Ventes par magasin' },
        { id: 'productsPerformanceChart', title: 'Performance des produits' },
        { id: 'monthlyComparisonChart', title: 'Comparaison mensuelle' }
    ];

    charts.forEach(chart => {
        const canvas = document.getElementById(chart.id);
        if (canvas) {
            // Créer un conteneur pour le graphique
            const chartDiv = document.createElement('div');
            chartDiv.style.marginBottom = '20px';

            // Ajouter un titre
            const title = document.createElement('h3');
            title.textContent = chart.title;
            title.style.color = '#3498db';
            title.style.marginBottom = '10px';
            chartDiv.appendChild(title);

            try {
                // Convertir le canvas en image
                const img = document.createElement('img');
                img.src = canvas.toDataURL('image/png');
                img.style.width = '100%';
                img.style.maxHeight = '200px';
                img.style.border = '1px solid #ddd';
                img.style.borderRadius = '5px';
                chartDiv.appendChild(img);
            } catch (e) {
                console.error(`Erreur lors de la conversion du graphique ${chart.id}:`, e);
                const errorMsg = document.createElement('p');
                errorMsg.textContent = `Impossible d'exporter ce graphique`;
                errorMsg.style.color = 'red';
                chartDiv.appendChild(errorMsg);
            }

            section.appendChild(chartDiv);
        }
    });

    container.appendChild(section);
}

// Fonction pour ajouter les tableaux au conteneur
function addTablesToContainer(container) {
    const section = document.createElement('div');
    section.innerHTML = '<h2 style="color:#2c3e50; margin-bottom:15px">Tableaux de données</h2>';

    // Liste des tableaux à exporter
    const tables = [
        { id: 'storesTable', title: 'Détail des ventes par magasin' },
        { id: 'productsTable', title: 'Top produits' }
    ];

    tables.forEach(tableInfo => {
        const tableElement = document.getElementById(tableInfo.id);
        if (tableElement) {
            // Créer un conteneur pour le tableau
            const tableDiv = document.createElement('div');
            tableDiv.style.marginBottom = '20px';

            // Ajouter un titre
            const title = document.createElement('h3');
            title.textContent = tableInfo.title;
            title.style.color = '#3498db';
            title.style.marginBottom = '10px';
            tableDiv.appendChild(title);

            // Cloner le tableau et ajuster son style
            const tableClone = tableElement.cloneNode(true);
            tableClone.style.width = '100%';
            tableClone.style.borderCollapse = 'collapse';

            // Styliser les cellules
            const cells = tableClone.querySelectorAll('th, td');
            cells.forEach(cell => {
                cell.style.border = '1px solid #ddd';
                cell.style.padding = '5px';
                cell.style.textAlign = 'left';
            });

            // Styliser les en-têtes
            const headers = tableClone.querySelectorAll('th');
            headers.forEach(header => {
                header.style.backgroundColor = '#f2f2f2';
                header.style.fontWeight = 'bold';
            });

            tableDiv.appendChild(tableClone);
            section.appendChild(tableDiv);
        }
    });

    container.appendChild(section);
}

function addBreakLine(container) {
    const breakLine = document.createElement('div');
    breakLine.style.pageBreakAfter = 'always';
    breakLine.style.marginBottom = '20px';
    container.appendChild(breakLine);
}

function showLoadingIndicator() {
    const indicator = document.createElement('div');
    indicator.id = 'pdf-loading-indicator';
    indicator.innerHTML = `
        <div style="position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.5); z-index:9999; display:flex; justify-content:center; align-items:center;">
            <div style="background:white; padding:20px; border-radius:5px; text-align:center;">
                <div style="border:4px solid #f3f3f3; border-top:4px solid #3498db; border-radius:50%; width:40px; height:40px; animation:spin 1s linear infinite; margin:0 auto 10px;"></div>
                <p>Génération du PDF en cours...</p>
            </div>
        </div>
        <style>
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        </style>
    `;
    document.body.appendChild(indicator);
}

// Cacher l'indicateur de chargement
function hideLoadingIndicator() {
    const indicator = document.getElementById('pdf-loading-indicator');
    if (indicator) {
        document.body.removeChild(indicator);
    }
}

// Configuration des événements
document.addEventListener('DOMContentLoaded', function() {
    // Vérifier que html2pdf est disponible
    if (typeof html2pdf === 'undefined') {
        console.error("La bibliothèque html2pdf.js n'est pas chargée!");
    }

    // Gestionnaire pour le formulaire d'exportation
    const exportForm = document.getElementById('exportForm');
    if (exportForm) {
        exportForm.addEventListener('submit', function(e) {
            e.preventDefault();

            // Fermer la modale
            document.getElementById('exportModal').style.display = 'none';

            // Récupérer les options
            const orientation = document.getElementById('exportOrientation');
            const includeHeader = document.getElementById('includeHeader');
            const includeCharts = document.getElementById('includeCharts');
            const includeTables = document.getElementById('includeTables');

            // Préparer les options
            const options = {
                orientation: orientation ? orientation.value : 'portrait',
                includeHeader: includeHeader ? includeHeader.checked : true,
                includeCharts: includeCharts ? includeCharts.checked : true,
                includeTables: includeTables ? includeTables.checked : true,
                filename: 'tableau_de_bord_ventes.pdf'
            };

            // Lancer l'export
            exportDashboardToPDF(options);
        });
    }

    // Configurer les boutons d'exportation
    ['exportBtn', 'footerExportBtn', 'exportData'].forEach(btnId => {
        const button = document.getElementById(btnId);
        if (button) {
            button.addEventListener('click', function() {
                document.getElementById('exportModal').style.display = 'block';
            });
        }
    });
});