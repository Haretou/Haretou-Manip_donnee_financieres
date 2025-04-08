/**
 * Fichier JavaScript pour gérer les graphiques du tableau de bord
 * Dépend de Chart.js
 */

const COLORS = {
    primary: '#3498db',
    secondary: '#2ecc71',
    accent: '#f39c12',
    danger: '#e74c3c',
    light: '#ecf0f1',
    dark: '#2c3e50',
    success: '#2ecc71',
    warning: '#f39c12',
    info: '#3498db',
    background: 'rgba(52, 152, 219, 0.2)',
    border: 'rgba(52, 152, 219, 1)'
};

const COLOR_PALETTE = [
    'rgba(52, 152, 219, 0.7)', // Bleu
    'rgba(46, 204, 113, 0.7)', // Vert
    'rgba(243, 156, 18, 0.7)', // Jaune
    'rgba(231, 76, 60, 0.7)', // Rouge
    'rgba(155, 89, 182, 0.7)', // Violet
    'rgba(52, 73, 94, 0.7)', // Bleu foncé
    'rgba(22, 160, 133, 0.7)', // Turquoise
    'rgba(230, 126, 34, 0.7)', // Orange
    'rgba(149, 165, 166, 0.7)', // Gris
    'rgba(241, 196, 15, 0.7)' // Jaune vif
];

const BORDER_COLOR_PALETTE = COLOR_PALETTE.map(color => color.replace('0.7', '1'));

function formatEuro(value) {
    return new Intl.NumberFormat('fr-FR', {
        style: 'currency',
        currency: 'EUR'
    }).format(value);
}

function formatNumber(value) {
    return new Intl.NumberFormat('fr-FR').format(value);
}

function initializeCharts(data) {
    if (!data) {
        console.error("Pas de données disponibles pour les graphiques");
        return;
    }

    // Initialisation des graphiques
    initSalesTrendChart(data);
    initStoresComparisonChart(data);
    initProductsPerformanceChart(data);
    initMonthlyComparisonChart(data);

    setupChartEvents(data);
}

function initSalesTrendChart(data) {
    if (!data.monthly_sales || data.monthly_sales.length === 0) {
        console.warn("Pas de données mensuelles disponibles");
        return;
    }

    const sortedSales = [...data.monthly_sales].sort((a, b) => a.periode.localeCompare(b.periode));
    const labels = sortedSales.map(item => {
        const [year, month] = item.periode.split('-');
        return `${month}/${year}`;
    });
    const values = sortedSales.map(item => item.total_ventes);

    const ctx = document.getElementById('salesTrendChart').getContext('2d');
    if (!ctx) {
        console.error("Canvas 'salesTrendChart' non trouvé");
        return;
    }

    window.salesTrendChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Ventes mensuelles',
                data: values,
                backgroundColor: COLORS.background,
                borderColor: COLORS.border,
                borderWidth: 2,
                tension: 0.4,
                pointBackgroundColor: COLORS.primary,
                pointBorderColor: '#fff',
                pointRadius: 4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: function(context) {
                            return formatEuro(context.raw);
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return formatEuro(value);
                        }
                    }
                }
            }
        }
    });
}

function initStoresComparisonChart(data) {
    if (!data.sales_by_store || data.sales_by_store.length === 0) {
        console.warn("Pas de données de ventes par magasin disponibles");
        return;
    }

    const sortedStores = [...data.sales_by_store].sort((a, b) => b.total_ventes - a.total_ventes);
    const topStores = sortedStores.slice(0, Math.min(10, sortedStores.length));
    const labels = topStores.map(item => item.magasin);
    const values = topStores.map(item => item.total_ventes);

    const ctx = document.getElementById('storesComparisonChart').getContext('2d');
    if (!ctx) {
        console.error("Canvas 'storesComparisonChart' non trouvé");
        return;
    }

    window.storesComparisonChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Ventes par magasin',
                data: values,
                backgroundColor: COLOR_PALETTE.slice(0, topStores.length),
                borderColor: BORDER_COLOR_PALETTE.slice(0, topStores.length),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return formatEuro(context.raw);
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return formatEuro(value);
                        }
                    }
                }
            }
        }
    });
}

function initProductsPerformanceChart(data) {
    if (!data.sales_by_product || data.sales_by_product.length === 0) {
        console.warn("Pas de données de ventes par produit disponibles");
        return;
    }

    const sortedProducts = [...data.sales_by_product].sort((a, b) => b.total_ventes - a.total_ventes);
    const topProducts = sortedProducts.slice(0, Math.min(5, sortedProducts.length));
    const labels = topProducts.map(item => item.produit);
    const values = topProducts.map(item => item.total_ventes);

    const ctx = document.getElementById('productsPerformanceChart').getContext('2d');
    if (!ctx) {
        console.error("Canvas 'productsPerformanceChart' non trouvé");
        return;
    }

    window.productsPerformanceChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                label: 'Ventes par produit',
                data: values,
                backgroundColor: COLOR_PALETTE.slice(0, topProducts.length),
                borderColor: BORDER_COLOR_PALETTE.slice(0, topProducts.length),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        boxWidth: 12,
                        padding: 15
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const value = formatEuro(context.raw);
                            const total = context.dataset.data.reduce((acc, val) => acc + val, 0);
                            const percentage = Math.round((context.raw / total) * 100);
                            return `${context.label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

function initMonthlyComparisonChart(data) {
    if (!data.monthly_sales || data.monthly_sales.length === 0) {
        console.warn("Pas de données mensuelles disponibles");
        return;
    }

    const monthLabels = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Août', 'Sep', 'Oct', 'Nov', 'Déc'];
    let monthlyValues = Array(12).fill(0);

    data.monthly_sales.forEach(item => {
        const month = parseInt(item.periode.split('-')[1]) - 1; // 0-indexed
        if (month >= 0 && month < 12) {
            monthlyValues[month] += item.total_ventes;
        }
    });

    const ctx = document.getElementById('monthlyComparisonChart').getContext('2d');
    if (!ctx) {
        console.error("Canvas 'monthlyComparisonChart' non trouvé");
        return;
    }

    window.monthlyComparisonChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: monthLabels,
            datasets: [{
                label: 'Ventes mensuelles',
                data: monthlyValues,
                backgroundColor: COLORS.background,
                borderColor: COLORS.border,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return formatEuro(context.raw);
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return formatEuro(value);
                        }
                    }
                }
            }
        }
    });
}

function setupChartEvents(data) {
    const salesTrendPeriod = document.getElementById('salesTrendPeriod');
    if (salesTrendPeriod) {
        salesTrendPeriod.addEventListener('change', function() {
            updateSalesTrendChart(this.value, data);
        });
    }

    const storesChartType = document.getElementById('storesChartType');
    if (storesChartType) {
        storesChartType.addEventListener('change', function() {
            updateStoresChartType(this.value, data);
        });
    }

    const productMetric = document.getElementById('productMetric');
    if (productMetric) {
        productMetric.addEventListener('change', function() {
            updateProductMetric(this.value, data);
        });
    }

    const comparisonYear = document.getElementById('comparisonYear');
    if (comparisonYear) {
        comparisonYear.addEventListener('change', function() {
            updateMonthlyComparisonYear(this.value, data);
        });
    }

    const productLimit = document.getElementById('productLimit');
    if (productLimit) {
        productLimit.addEventListener('change', function() {
            updateProductsTable(this.value, data);
        });
    }

    const storeSort = document.getElementById('storeSort');
    if (storeSort) {
        storeSort.addEventListener('change', function() {
            sortStoresTable(this.value, data);
        });
    }

    const storeSearch = document.getElementById('storeSearch');
    if (storeSearch) {
        storeSearch.addEventListener('input', function() {
            searchStoresTable(this.value);
        });
    }

    const productSearch = document.getElementById('productSearch');
    if (productSearch) {
        productSearch.addEventListener('input', function() {
            searchProductsTable(this.value);
        });
    }

    const refreshBtn = document.getElementById('refreshData');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', function() {
            window.location.reload();
        });
    }
}

function updateSalesTrendChart(periodType, data) {
    if (!window.salesTrendChart || !data.monthly_sales) return;

    let periodData = {};

    data.monthly_sales.forEach(item => {
        const [year, month] = item.periode.split('-');
        let key;

        if (periodType === 'weekly') {
            for (let week = 1; week <= 4; week++) {
                key = `${year}-${month}-W${week}`;
                periodData[key] = (periodData[key] || 0) + (item.total_ventes / 4);
            }
        } else if (periodType === 'yearly') {
            key = year;
            periodData[key] = (periodData[key] || 0) + item.total_ventes;
        } else {
            key = item.periode;
            periodData[key] = (periodData[key] || 0) + item.total_ventes;
        }
    });

    const sortedPeriods = Object.keys(periodData).sort();
    const labels = sortedPeriods.map(period => {
        if (periodType === 'weekly') {
            const [year, month, week] = period.split('-');
            return `${month}/${year} ${week}`;
        } else if (periodType === 'yearly') {
            return period;
        } else {
            const [year, month] = period.split('-');
            return `${month}/${year}`;
        }
    });

    const values = sortedPeriods.map(period => periodData[period]);

    window.salesTrendChart.data.labels = labels;
    window.salesTrendChart.data.datasets[0].data = values;
    window.salesTrendChart.update();
}

function updateStoresChartType(chartType, data) {
    if (!data.sales_by_store) return;

    const canvas = document.getElementById('storesComparisonChart');
    if (!canvas) return;

    if (window.storesComparisonChart) {
        window.storesComparisonChart.destroy();
    }

    const sortedStores = [...data.sales_by_store].sort((a, b) => b.total_ventes - a.total_ventes);
    const topStores = sortedStores.slice(0, Math.min(10, sortedStores.length));
    const labels = topStores.map(item => item.magasin);
    const values = topStores.map(item => item.total_ventes);

    const options = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: chartType === 'pie',
                position: 'right',
                labels: {
                    boxWidth: 12,
                    padding: 15
                }
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        return formatEuro(context.raw);
                    }
                }
            }
        }
    };

    if (chartType !== 'pie') {
        options.scales = {
            y: {
                beginAtZero: true,
                ticks: {
                    callback: function(value) {
                        return formatEuro(value);
                    }
                }
            }
        };
    }

    const ctx = canvas.getContext('2d');
    window.storesComparisonChart = new Chart(ctx, {
        type: chartType,
        data: {
            labels: labels,
            datasets: [{
                label: 'Ventes par magasin',
                data: values,
                backgroundColor: chartType === 'bar' ? COLORS.background : COLOR_PALETTE.slice(0, topStores.length),
                borderColor: chartType === 'bar' ? COLORS.border : BORDER_COLOR_PALETTE.slice(0, topStores.length),
                borderWidth: 1
            }]
        },
        options: options
    });
}

function updateProductMetric(metricType, data) {
    if (!window.productsPerformanceChart || !data.sales_by_product) return;

    const sortedProducts = [...data.sales_by_product].sort((a, b) => {
        if (metricType === 'quantity') {
            return b.quantite_totale - a.quantite_totale;
        } else {
            return b.total_ventes - a.total_ventes;
        }
    });

    const topProducts = sortedProducts.slice(0, Math.min(5, sortedProducts.length));
    const labels = topProducts.map(item => item.produit);
    const values = topProducts.map(item =>
        metricType === 'quantity' ? item.quantite_totale : item.total_ventes
    );

    window.productsPerformanceChart.data.labels = labels;
    window.productsPerformanceChart.data.datasets[0].data = values;
    window.productsPerformanceChart.options.plugins.tooltip.callbacks.label = function(context) {
        if (metricType === 'quantity') {
            const value = formatNumber(context.raw);
            const total = context.dataset.data.reduce((acc, val) => acc + val, 0);
            const percentage = Math.round((context.raw / total) * 100);
            return `${context.label}: ${value} unités (${percentage}%)`;
        } else {
            const value = formatEuro(context.raw);
            const total = context.dataset.data.reduce((acc, val) => acc + val, 0);
            const percentage = Math.round((context.raw / total) * 100);
            return `${context.label}: ${value} (${percentage}%)`;
        }
    };

    window.productsPerformanceChart.update();
}

function updateMonthlyComparisonYear(year, data) {
    if (!window.monthlyComparisonChart || !data.monthly_sales) return;

    let monthlyValues = Array(12).fill(0);

    data.monthly_sales.forEach(item => {
        const [itemYear, itemMonth] = item.periode.split('-');
        const month = parseInt(itemMonth) - 1; // 0-indexed

        if ((year === 'all' || itemYear === year) && month >= 0 && month < 12) {
            monthlyValues[month] += item.total_ventes;
        }
    });

    window.monthlyComparisonChart.data.datasets[0].data = monthlyValues;
    window.monthlyComparisonChart.update();
}

function updateProductsTable(limit, data) {
    if (!data.sales_by_product) return;

    const productsTable = document.getElementById('productsTable');
    if (!productsTable) return;

    const tbody = productsTable.querySelector('tbody');
    if (!tbody) return;

    tbody.innerHTML = '';

    const sortedProducts = [...data.sales_by_product].sort((a, b) => b.total_ventes - a.total_ventes);

    const limitNumber = limit === 'all' ? sortedProducts.length : parseInt(limit);
    const productsToShow = sortedProducts.slice(0, limitNumber);

    const totalSales = data.total_sales || 1;

    productsToShow.forEach(product => {
        const percentage = (product.total_ventes / totalSales) * 100;
        const avgPrice = product.total_ventes / (product.quantite_totale || 1);

        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${product.produit}</td>
            <td>${formatNumber(product.quantite_totale || 0)}</td>
            <td>${formatEuro(product.total_ventes || 0)}</td>
            <td>${formatEuro(avgPrice)}</td>
            <td>${percentage.toFixed(2)}%</td>
        `;
        tbody.appendChild(row);
    });
}

function sortStoresTable(sortOption, data) {
    if (!data.sales_by_store) return;

    const storesTable = document.getElementById('storesTable');
    if (!storesTable) return;

    const tbody = storesTable.querySelector('tbody');
    if (!tbody) return;

    tbody.innerHTML = '';

    const sortedStores = [...data.sales_by_store].sort((a, b) => {
        if (sortOption === 'sales-desc') {
            return b.total_ventes - a.total_ventes;
        } else if (sortOption === 'sales-asc') {
            return a.total_ventes - b.total_ventes;
        } else if (sortOption === 'name-asc') {
            return a.magasin.localeCompare(b.magasin);
        } else { // name-desc
            return b.magasin.localeCompare(a.magasin);
        }
    });

    const totalSales = data.total_sales || 1;

    sortedStores.forEach(store => {
        const percentage = (store.total_ventes / totalSales) * 100;

        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${store.magasin}</td>
            <td>${formatEuro(store.total_ventes || 0)}</td>
            <td>${formatNumber(store.quantite_totale || 0)}</td>
            <td>${percentage.toFixed(2)}%</td>
            <td>N/A</td>
        `;
        tbody.appendChild(row);
    });
}

function searchStoresTable(searchText) {
    const storesTable = document.getElementById('storesTable');
    if (!storesTable) return;

    const rows = storesTable.querySelectorAll('tbody tr');
    const searchLower = searchText.toLowerCase();

    rows.forEach(row => {
        const storeName = row.querySelector('td:first-child').textContent.toLowerCase();
        row.style.display = storeName.includes(searchLower) ? '' : 'none';
    });
}

function searchProductsTable(searchText) {
    const productsTable = document.getElementById('productsTable');
    if (!productsTable) return;

    const rows = productsTable.querySelectorAll('tbody tr');
    const searchLower = searchText.toLowerCase();

    rows.forEach(row => {
        const productName = row.querySelector('td:first-child').textContent.toLowerCase();
        row.style.display = productName.includes(searchLower) ? '' : 'none';
    });
}