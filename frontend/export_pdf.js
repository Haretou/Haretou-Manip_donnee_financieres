/**
 * Fonction pour gérer l'exportation du tableau de bord en PDF
 * Utilise la bibliothèque html2pdf.js
 */

// Fonction principale d'exportation en PDF
function exportDashboardToPDF(options = {}) {
    // Configuration par défaut
    const defaultOptions = {
        filename: 'tableau_de_bord_ventes.pdf',
        includeCharts: true,
        includeHeader: true,
        includeTables: true,
        orientation: 'portrait',
        pageSize: 'a4',
        margin: [15, 15, 15, 15], // [top, right, bottom, left] en mm
        title: 'Tableau de Bord des Ventes'
    };

    // Fusion des options par défaut avec celles fournies
    const settings = {...defaultOptions, ...options };

    // Afficher un indicateur de chargement
    showLoadingIndicator();

    // Créer un élément conteneur pour le PDF
    const pdfContainer = document.createElement('div');
    pdfContainer.className = 'pdf-export-container';
    pdfContainer.style.width = '210mm'; // Largeur A4
    pdfContainer.style.padding = '10mm';
    pdfContainer.style.backgroundColor = 'white';
    pdfContainer.style.position = 'absolute';
    pdfContainer.style.left = '-9999px'; // Cacher le conteneur hors de l'écran
    document.body.appendChild(pdfContainer);

    // Ajouter un titre au PDF
    const titleElement = document.createElement('div');
    titleElement.innerHTML = `
        <h1 style="text-align: center; color: #3498db; margin-bottom: 10mm; font-size: 24px;">${settings.title}</h1>
        <p style="text-align: center; margin-bottom: 5mm;">Date d'exportation: ${new Date().toLocaleDateString('fr-FR')} ${new Date().toLocaleTimeString('fr-FR')}</p>
        <hr style="margin-bottom: 10mm; border-color: #3498db;">
    `;
    pdfContainer.appendChild(titleElement);

    // Cloner et ajouter les métriques principales
    if (settings.includeHeader) {
        const metricsRow = document.querySelector('.metrics-row').cloneNode(true);
        metricsRow.style.display = 'flex';
        metricsRow.style.flexWrap = 'wrap';
        metricsRow.style.justifyContent = 'space-between';
        metricsRow.style.marginBottom = '10mm';

        // Ajuster le style des métriques pour le PDF
        const metricCards = metricsRow.querySelectorAll('.metric-card');
        metricCards.forEach(card => {
            card.style.width = '48%';
            card.style.marginBottom = '5mm';
            card.style.border = '1px solid #ddd';
            card.style.borderRadius = '5px';
            card.style.padding = '5mm';
        });

        pdfContainer.appendChild(metricsRow);
    }

    // Ajouter un saut de page après les métriques
    const pageBreak = document.createElement('div');
    pageBreak.style.pageBreakAfter = 'always';
    pageBreak.style.marginBottom = '10mm';
    pdfContainer.appendChild(pageBreak);

    // Si l'option includeCharts est activée, convertir les graphiques en images
    if (settings.includeCharts) {
        const chartsTitle = document.createElement('h2');
        chartsTitle.textContent = 'Graphiques d\'analyse';
        chartsTitle.style.marginBottom = '5mm';
        chartsTitle.style.color = '#2c3e50';
        pdfContainer.appendChild(chartsTitle);

        // Fonction pour convertir un canvas en image et l'ajouter au conteneur PDF
        const addChartToPDF = (chartId, title) => {
            const chartContainer = document.createElement('div');
            chartContainer.style.marginBottom = '10mm';

            const chartTitle = document.createElement('h3');
            chartTitle.textContent = title;
            chartTitle.style.marginBottom = '3mm';
            chartTitle.style.color = '#3498db';
            chartContainer.appendChild(chartTitle);

            const canvas = document.getElementById(chartId);
            if (canvas) {
                const chartImg = document.createElement('img');
                chartImg.src = canvas.toDataURL('image/png');
                chartImg.style.width = '100%';
                chartImg.style.height = 'auto';
                chartImg.style.maxHeight = '80mm';
                chartImg.style.border = '1px solid #ddd';
                chartImg.style.borderRadius = '5px';
                chartImg.style.padding = '2mm';
                chartContainer.appendChild(chartImg);
                pdfContainer.appendChild(chartContainer);
            }
        };

        // Ajouter les graphiques principaux
        addChartToPDF('salesTrendChart', 'Évolution des ventes');
        addChartToPDF('storesComparisonChart', 'Ventes par magasin');

        // Ajouter un saut de page
        const pageBreak2 = document.createElement('div');
        pageBreak2.style.pageBreakAfter = 'always';
        pdfContainer.appendChild(pageBreak2);

        // Continuer avec les autres graphiques
        addChartToPDF('productsPerformanceChart', 'Performance des produits');
        addChartToPDF('monthlyComparisonChart', 'Comparaison mensuelle');
    }

    // Si l'option includeTables est activée, ajouter les tableaux
    if (settings.includeTables) {
        const tablesTitle = document.createElement('h2');
        tablesTitle.textContent = 'Tableaux de données';
        tablesTitle.style.marginBottom = '5mm';
        tablesTitle.style.color = '#2c3e50';
        pdfContainer.appendChild(tablesTitle);

        // Fonction pour cloner et ajouter un tableau au conteneur PDF
        const addTableToPDF = (tableId, title) => {
            const tableSection = document.createElement('div');
            tableSection.style.marginBottom = '10mm';

            const tableTitle = document.createElement('h3');
            tableTitle.textContent = title;
            tableTitle.style.marginBottom = '3mm';
            tableTitle.style.color = '#3498db';
            tableSection.appendChild(tableTitle);

            const originalTable = document.getElementById(tableId);
            if (originalTable) {
                const table = originalTable.cloneNode(true);
                // Ajuster les styles du tableau pour le PDF
                table.style.width = '100%';
                table.style.borderCollapse = 'collapse';
                table.style.marginBottom = '5mm';

                const cells = table.querySelectorAll('th, td');
                cells.forEach(cell => {
                    cell.style.border = '1px solid #ddd';
                    cell.style.padding = '2mm';
                    cell.style.textAlign = 'left';
                });

                const headers = table.querySelectorAll('th');
                headers.forEach(header => {
                    header.style.backgroundColor = '#f8f9fa';
                    header.style.fontWeight = 'bold';
                });

                tableSection.appendChild(table);
                pdfContainer.appendChild(tableSection);
            }
        };

        // Ajouter les tableaux principaux
        addTableToPDF('storesTable', 'Détail des ventes par magasin');
        addTableToPDF('productsTable', 'Top produits');
    }

    // Configuration des options pour html2pdf
    const pdfOptions = {
        filename: settings.filename,
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2, useCORS: true, logging: false },
        jsPDF: {
            unit: 'mm',
            format: settings.pageSize,
            orientation: settings.orientation,
            compress: true
        },
        margin: settings.margin
    };

    // Générer le PDF
    html2pdf()
        .set(pdfOptions)
        .from(pdfContainer)
        .save()
        .then(() => {
            // Nettoyer: supprimer le conteneur temporaire
            document.body.removeChild(pdfContainer);
            hideLoadingIndicator();
        })
        .catch(error => {
            console.error('Erreur lors de la génération du PDF:', error);
            hideLoadingIndicator();
            showErrorMessage('Une erreur est survenue lors de la génération du PDF. Veuillez réessayer.');
        });
}

// Fonctions d'aide
function showLoadingIndicator() {
    // Créer un élément de chargement si nécessaire
    if (!document.getElementById('pdf-loading-indicator')) {
        const loadingDiv = document.createElement('div');
        loadingDiv.id = 'pdf-loading-indicator';
        loadingDiv.innerHTML = `
            <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 9999; display: flex; justify-content: center; align-items: center;">
                <div style="background: white; padding: 20px; border-radius: 8px; text-align: center;">
                    <div class="spinner" style="border: 4px solid #f3f3f3; border-top: 4px solid #3498db; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 0 auto 10px;"></div>
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
        document.body.appendChild(loadingDiv);
    } else {
        document.getElementById('pdf-loading-indicator').style.display = 'block';
    }
}

function hideLoadingIndicator() {
    const loadingDiv = document.getElementById('pdf-loading-indicator');
    if (loadingDiv) {
        loadingDiv.style.display = 'none';
    }
}

function showErrorMessage(message) {
    alert(message);
}

// Configuration des événements pour l'exportation en PDF
function setupPDFExportEvents() {
    // Bouton d'exportation principal
    const exportBtn = document.getElementById('exportBtn');
    if (exportBtn) {
        exportBtn.addEventListener('click', function(e) {
            e.preventDefault();
            const exportFormat = document.getElementById('exportFormat');
            if (exportFormat) {
                exportFormat.value = 'pdf';
            }
            document.getElementById('exportModal').style.display = 'block';
        });
    }

    // Bouton d'exportation dans le pied de page
    const footerExportBtn = document.getElementById('footerExportBtn');
    if (footerExportBtn) {
        footerExportBtn.addEventListener('click', function(e) {
            e.preventDefault();
            const exportFormat = document.getElementById('exportFormat');
            if (exportFormat) {
                exportFormat.value = 'pdf';
            }
            document.getElementById('exportModal').style.display = 'block';
        });
    }

    // Bouton d'exportation dans la barre latérale
    const exportDataBtn = document.getElementById('exportData');
    if (exportDataBtn) {
        exportDataBtn.addEventListener('click', function(e) {
            e.preventDefault();
            const exportFormat = document.getElementById('exportFormat');
            if (exportFormat) {
                exportFormat.value = 'pdf';
            }
            document.getElementById('exportModal').style.display = 'block';
        });
    }

    // Soumission du formulaire d'exportation
    const exportForm = document.getElementById('exportForm');
    if (exportForm) {
        exportForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const format = document.getElementById('exportFormat').value;

            if (format === 'pdf') {
                // Fermer la modale
                document.getElementById('exportModal').style.display = 'none';

                // Récupérer les options d'exportation
                const dateRange = document.getElementById('dateRange').value;
                const orientation = document.getElementById('exportOrientation') ?
                    document.getElementById('exportOrientation').value : 'portrait';

                let customDateRange = {};
                if (dateRange === 'custom') {
                    customDateRange = {
                        startDate: document.getElementById('exportStartDate').value,
                        endDate: document.getElementById('exportEndDate').value
                    };
                }

                // Options d'exportation
                const exportOptions = {
                    orientation: orientation,
                    dateRange: dateRange,
                    customDateRange: customDateRange,
                    filename: `tableau_de_bord_ventes_${dateRange}.pdf`
                };

                // Exporter le tableau de bord en PDF
                exportDashboardToPDF(exportOptions);
            }
        });
    }
}

// Initialiser les événements une fois que le DOM est chargé
document.addEventListener('DOMContentLoaded', function() {
    setupPDFExportEvents();
});