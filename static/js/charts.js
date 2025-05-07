/**
 * charts.js - Chart.js implementations for the sports prediction app
 * 
 * This file contains functions to create and update charts for visualizing
 * prediction data and accuracy metrics using Chart.js
 */

// Colors from our design system
const colors = {
    primary: '#2962FF',
    secondary: '#FF6B6B',
    accent: '#38B2AC',
    light: '#F8F9FA',
    dark: '#212529',
    gray: '#6C757D'
};

/**
 * Creates a line chart showing prediction accuracy over time
 * @param {string} canvasId - The ID of the canvas element
 * @param {Array} labels - Date labels for the x-axis
 * @param {Array} accuracyData - Accuracy percentage data for the y-axis
 */
function createAccuracyChart(canvasId, labels, accuracyData) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Prediction Accuracy (%)',
                data: accuracyData,
                borderColor: colors.primary,
                backgroundColor: 'rgba(41, 98, 255, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.2,
                pointBackgroundColor: colors.primary,
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Prediction Accuracy Over Time',
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: 'rgba(255, 255, 255, 0.9)',
                    titleColor: colors.dark,
                    bodyColor: colors.dark,
                    borderColor: 'rgba(0, 0, 0, 0.1)',
                    borderWidth: 1,
                    padding: 12,
                    displayColors: false,
                    callbacks: {
                        label: function(context) {
                            return `Accuracy: ${context.parsed.y.toFixed(1)}%`;
                        }
                    }
                },
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        font: {
                            family: "'IBM Plex Sans', sans-serif"
                        }
                    }
                },
                y: {
                    beginAtZero: true,
                    max: 100,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    },
                    ticks: {
                        font: {
                            family: "'IBM Plex Sans', sans-serif"
                        },
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                }
            }
        }
    });
    
    return chart;
}

/**
 * Creates a bar chart comparing predicted vs actual scores
 * @param {string} canvasId - The ID of the canvas element
 * @param {Array} labels - Team names for the x-axis
 * @param {Array} predictedScores - Predicted scores
 * @param {Array} actualScores - Actual scores (can be null if game hasn't happened)
 */
function createScoreComparisonChart(canvasId, labels, predictedScores, actualScores) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    const datasets = [{
        label: 'Predicted Score',
        data: predictedScores,
        backgroundColor: 'rgba(41, 98, 255, 0.7)',
        borderColor: colors.primary,
        borderWidth: 1
    }];
    
    // Only add actual scores if they exist
    if (actualScores.some(score => score !== null)) {
        datasets.push({
            label: 'Actual Score',
            data: actualScores,
            backgroundColor: 'rgba(255, 107, 107, 0.7)',
            borderColor: colors.secondary,
            borderWidth: 1
        });
    }
    
    const chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Predicted vs Actual Scores',
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    }
                },
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    },
                    ticks: {
                        precision: 0
                    }
                }
            }
        }
    });
    
    return chart;
}

/**
 * Creates a pie chart showing win probability distribution
 * @param {string} canvasId - The ID of the canvas element
 * @param {Array} probabilities - Array of probability values [home, away, draw]
 * @param {Array} teamNames - Array of team names [home, away]
 */
function createWinProbabilityChart(canvasId, probabilities, teamNames) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    // Format labels
    const labels = [
        `${teamNames[0]} Win`,
        `${teamNames[1]} Win`,
    ];
    
    // Add Draw probability if it exists
    if (probabilities.length > 2) {
        labels.push('Draw');
    }
    
    const chart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: probabilities,
                backgroundColor: [
                    colors.primary,
                    colors.secondary,
                    colors.accent
                ],
                borderColor: '#fff',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Win Probability',
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const value = context.parsed;
                            const percentage = (value * 100).toFixed(1) + '%';
                            return `${context.label}: ${percentage}`;
                        }
                    }
                },
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        font: {
                            family: "'IBM Plex Sans', sans-serif"
                        }
                    }
                }
            },
            cutout: '60%'
        }
    });
    
    return chart;
}

/**
 * Creates a horizontal bar chart for displaying team performance metrics
 * @param {string} canvasId - The ID of the canvas element
 * @param {Array} labels - Metric names
 * @param {Array} homeData - Home team metrics
 * @param {Array} awayData - Away team metrics
 * @param {Array} teamNames - Team names [home, away]
 */
function createTeamComparisonChart(canvasId, labels, homeData, awayData, teamNames) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    const chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: teamNames[0],
                    data: homeData,
                    backgroundColor: 'rgba(41, 98, 255, 0.7)',
                    borderColor: colors.primary,
                    borderWidth: 1
                },
                {
                    label: teamNames[1],
                    data: awayData,
                    backgroundColor: 'rgba(255, 107, 107, 0.7)',
                    borderColor: colors.secondary,
                    borderWidth: 1
                }
            ]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Team Comparison',
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                },
                legend: {
                    position: 'bottom'
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                y: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
    
    return chart;
}

/**
 * Fetches prediction data from the API and updates charts
 * @param {number} days - Number of days of history to fetch
 */
function fetchPredictionData(days = 30) {
    fetch(`/api/predictions?days=${days}`)
        .then(response => response.json())
        .then(data => {
            // Process data for charts
            updateChartsWithData(data);
        })
        .catch(error => {
            console.error('Error fetching prediction data:', error);
        });
}

/**
 * Updates all charts with new data
 * @param {Array} data - Prediction data from API
 */
function updateChartsWithData(data) {
    // Process data for accuracy chart
    const dateMap = new Map();
    
    // Group predictions by date
    data.forEach(prediction => {
        const date = prediction.date;
        if (!dateMap.has(date)) {
            dateMap.set(date, {
                total: 0,
                correct: 0
            });
        }
        
        const dateStats = dateMap.get(date);
        dateStats.total += 1;
        
        if (prediction.was_correct) {
            dateStats.correct += 1;
        }
    });
    
    // Convert map to sorted arrays for chart
    const sortedDates = Array.from(dateMap.keys()).sort();
    const accuracyData = sortedDates.map(date => {
        const stats = dateMap.get(date);
        return stats.total > 0 ? (stats.correct / stats.total) * 100 : 0;
    });
    
    // Update accuracy chart if it exists on the page
    const accuracyChartElement = document.getElementById('accuracy-chart');
    if (accuracyChartElement) {
        if (window.accuracyChart) {
            window.accuracyChart.destroy();
        }
        window.accuracyChart = createAccuracyChart('accuracy-chart', sortedDates, accuracyData);
    }
    
    // Update other charts as needed...
    // This would be expanded based on what charts are displayed on which pages
}

// Initialize charts when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize charts that are present on the page
    initializePageCharts();
    
    // Add event listeners for any chart controls
    addChartEventListeners();
});

/**
 * Initialize charts specific to the current page
 */
function initializePageCharts() {
    // Check page and initialize appropriate charts
    
    // Example: History page with accuracy chart
    const accuracyChartElement = document.getElementById('accuracy-chart');
    if (accuracyChartElement) {
        // Get chart data from data attributes or fetch from API
        const labels = accuracyChartElement.dataset.labels;
        const accuracyData = accuracyChartElement.dataset.values;
        
        if (labels && accuracyData) {
            // Data is provided in element attributes
            const parsedLabels = JSON.parse(labels);
            const parsedValues = JSON.parse(accuracyData);
            window.accuracyChart = createAccuracyChart('accuracy-chart', parsedLabels, parsedValues);
        } else {
            // Fetch data from API
            fetchPredictionData();
        }
    }
    
    // Prediction detail page with win probability chart
    const probabilityChartElement = document.getElementById('probability-chart');
    if (probabilityChartElement) {
        const homeProb = parseFloat(probabilityChartElement.dataset.homeProb);
        const awayProb = parseFloat(probabilityChartElement.dataset.awayProb);
        const drawProb = parseFloat(probabilityChartElement.dataset.drawProb);
        const homeTeam = probabilityChartElement.dataset.homeTeam;
        const awayTeam = probabilityChartElement.dataset.awayTeam;
        
        const probabilities = drawProb ? [homeProb, awayProb, drawProb] : [homeProb, awayProb];
        window.probabilityChart = createWinProbabilityChart(
            'probability-chart', 
            probabilities, 
            [homeTeam, awayTeam]
        );
    }
    
    // Score comparison chart
    const scoreChartElement = document.getElementById('score-chart');
    if (scoreChartElement) {
        const homeTeam = scoreChartElement.dataset.homeTeam;
        const awayTeam = scoreChartElement.dataset.awayTeam;
        const predictedHome = parseFloat(scoreChartElement.dataset.predictedHome);
        const predictedAway = parseFloat(scoreChartElement.dataset.predictedAway);
        const actualHome = scoreChartElement.dataset.actualHome ? parseFloat(scoreChartElement.dataset.actualHome) : null;
        const actualAway = scoreChartElement.dataset.actualAway ? parseFloat(scoreChartElement.dataset.actualAway) : null;
        
        const labels = [homeTeam, awayTeam];
        const predictedScores = [predictedHome, predictedAway];
        const actualScores = [actualHome, actualAway];
        
        window.scoreChart = createScoreComparisonChart(
            'score-chart',
            labels,
            predictedScores, 
            actualScores
        );
    }
}

/**
 * Add event listeners for chart controls
 */
function addChartEventListeners() {
    // Range selector for history timeframe
    const timeframeSelector = document.getElementById('timeframe-selector');
    if (timeframeSelector) {
        timeframeSelector.addEventListener('change', function() {
            const days = parseInt(this.value);
            fetchPredictionData(days);
        });
    }
}
