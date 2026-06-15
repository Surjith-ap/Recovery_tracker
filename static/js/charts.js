/**
 * Charts.js — Chart initialization for Jaundice Recovery Tracker
 * Uses Chart.js v4
 */

// Shared chart styling
const chartColors = {
    purple: 'rgba(108, 92, 231, 1)',
    purpleLight: 'rgba(108, 92, 231, 0.15)',
    teal: 'rgba(0, 206, 201, 1)',
    tealLight: 'rgba(0, 206, 201, 0.15)',
    amber: 'rgba(253, 203, 110, 1)',
    rose: 'rgba(232, 67, 147, 1)',
    green: 'rgba(0, 184, 148, 1)',
    gridColor: 'rgba(108, 92, 231, 0.08)',
    textColor: '#64748b',
};

const defaultOptions = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
        intersect: false,
        mode: 'index',
    },
    plugins: {
        legend: {
            display: false,
            labels: {
                font: { family: 'Inter', size: 12, weight: '500' },
                color: chartColors.textColor,
                usePointStyle: true,
                padding: 20,
            },
        },
        tooltip: {
            backgroundColor: 'rgba(30, 30, 60, 0.92)',
            titleFont: { family: 'Inter', size: 13, weight: '600' },
            bodyFont: { family: 'Inter', size: 12 },
            padding: 12,
            cornerRadius: 10,
            displayColors: true,
            boxPadding: 4,
        },
    },
    scales: {
        x: {
            grid: { display: false },
            ticks: {
                font: { family: 'Inter', size: 11 },
                color: chartColors.textColor,
            },
        },
        y: {
            grid: { color: chartColors.gridColor },
            ticks: {
                font: { family: 'Inter', size: 11 },
                color: chartColors.textColor,
            },
            beginAtZero: true,
        },
    },
};


/**
 * Initialize the Bilirubin trend chart on the dashboard
 */
function initBilirubinChart(labels, values) {
    const ctx = document.getElementById('bilirubinChart');
    if (!ctx) return;

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Total Bilirubin (mg/dL)',
                data: values,
                borderColor: chartColors.purple,
                backgroundColor: chartColors.purpleLight,
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointRadius: 5,
                pointHoverRadius: 8,
                pointBackgroundColor: '#fff',
                pointBorderColor: chartColors.purple,
                pointBorderWidth: 2.5,
                pointHoverBackgroundColor: chartColors.purple,
                pointHoverBorderColor: '#fff',
            }],
        },
        options: {
            ...defaultOptions,
            plugins: {
                ...defaultOptions.plugins,
                legend: { display: false },
                annotation: {
                    annotations: {
                        normalLine: {
                            type: 'line',
                            yMin: 1.2,
                            yMax: 1.2,
                            borderColor: 'rgba(0, 184, 148, 0.5)',
                            borderWidth: 2,
                            borderDash: [6, 4],
                            label: {
                                display: true,
                                content: 'Normal (1.2)',
                                position: 'end',
                            },
                        },
                    },
                },
            },
        },
    });
}


/**
 * Initialize a lab trend chart (used on Lab Results page)
 */
function initLabTrendChart(canvasId, labels, values, testName) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: testName,
                data: values,
                borderColor: chartColors.teal,
                backgroundColor: chartColors.tealLight,
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointRadius: 5,
                pointHoverRadius: 8,
                pointBackgroundColor: '#fff',
                pointBorderColor: chartColors.teal,
                pointBorderWidth: 2.5,
                pointHoverBackgroundColor: chartColors.teal,
                pointHoverBorderColor: '#fff',
            }],
        },
        options: {
            ...defaultOptions,
            plugins: {
                ...defaultOptions.plugins,
                legend: {
                    display: true,
                    position: 'top',
                    align: 'end',
                },
            },
        },
    });
}
