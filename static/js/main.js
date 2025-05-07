/**
 * main.js - Main JavaScript for the sports prediction application
 * 
 * This file contains general utility functions and event handlers
 * for the application interface.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize date pickers
    initializeDatePickers();
    
    // Initialize form validation
    initializeFormValidation();
    
    // Initialize tooltips and popovers
    initializeTooltips();
    
    // Add event listeners
    addEventListeners();
});

/**
 * Initialize date picker inputs
 */
function initializeDatePickers() {
    // Set default date to today for game_date input
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(input => {
        // If it's a new prediction form, set default to today
        if (input.id === 'game_date' && !input.value) {
            const today = new Date().toISOString().split('T')[0];
            input.value = today;
            // Set min to today (can't predict past games)
            input.min = today;
        }
    });
}

/**
 * Initialize form validation
 */
function initializeFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            // Extra validation for team selection
            const homeTeam = form.querySelector('#home_team');
            const awayTeam = form.querySelector('#away_team');
            
            if (homeTeam && awayTeam && homeTeam.value === awayTeam.value) {
                event.preventDefault();
                
                // Show error message
                const errorMsg = document.createElement('div');
                errorMsg.className = 'alert alert-danger mt-2';
                errorMsg.textContent = 'Home and away teams must be different';
                
                // Remove any existing error messages
                const existingError = form.querySelector('.alert-danger');
                if (existingError) {
                    existingError.remove();
                }
                
                form.appendChild(errorMsg);
            }
            
            form.classList.add('was-validated');
        }, false);
    });
}

/**
 * Initialize Bootstrap tooltips and popovers
 */
function initializeTooltips() {
    // Initialize tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    
    // Initialize popovers
    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
    [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));
}

/**
 * Add event listeners for interactive elements
 */
function addEventListeners() {
    // Team selection change event
    const teamSelectors = document.querySelectorAll('.team-selector');
    teamSelectors.forEach(selector => {
        selector.addEventListener('change', handleTeamChange);
    });
    
    // Confidence explanation toggle
    const confidenceInfoElements = document.querySelectorAll('.confidence-info');
    confidenceInfoElements.forEach(element => {
        element.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('data-target'));
            if (target) {
                target.classList.toggle('d-none');
            }
        });
    });
    
    // Toggle prediction details
    const predictionToggleButtons = document.querySelectorAll('.prediction-toggle');
    predictionToggleButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetId = this.getAttribute('data-bs-target');
            const target = document.querySelector(targetId);
            
            if (target) {
                // Toggle the collapse state
                const bsCollapse = new bootstrap.Collapse(target);
                
                // Update button text based on current state
                if (target.classList.contains('show')) {
                    this.textContent = 'Show Details';
                } else {
                    this.textContent = 'Hide Details';
                }
            }
        });
    });
}

/**
 * Handle team selection change to prevent selecting the same team
 */
function handleTeamChange(event) {
    const currentSelect = event.target;
    const form = currentSelect.closest('form');
    
    if (!form) return;
    
    const homeSelect = form.querySelector('#home_team');
    const awaySelect = form.querySelector('#away_team');
    
    if (!homeSelect || !awaySelect) return;
    
    // Get current selections
    const homeTeamId = homeSelect.value;
    const awayTeamId = awaySelect.value;
    
    // Check if same team is selected for both
    if (homeTeamId && awayTeamId && homeTeamId === awayTeamId) {
        // Determine which one was just changed
        const otherSelect = currentSelect === homeSelect ? awaySelect : homeSelect;
        
        // Show warning
        const warningEl = document.getElementById('team-selection-warning');
        if (warningEl) {
            warningEl.classList.remove('d-none');
            
            // Hide warning after 3 seconds
            setTimeout(() => {
                warningEl.classList.add('d-none');
            }, 3000);
        }
    }
}

/**
 * Format probability as percentage
 * @param {number} probability - Probability value between 0 and 1
 * @param {number} decimals - Number of decimal places
 * @return {string} Formatted percentage string
 */
function formatProbability(probability, decimals = 1) {
    if (probability === null || probability === undefined) {
        return 'N/A';
    }
    
    return (probability * 100).toFixed(decimals) + '%';
}

/**
 * Update the win probability bars in the UI
 * @param {number} homeProb - Home win probability
 * @param {number} awayProb - Away win probability
 * @param {number} drawProb - Draw probability
 */
function updateProbabilityBars(homeProb, awayProb, drawProb = null) {
    // Update home probability bar
    const homeProbBar = document.getElementById('home-prob-bar');
    const homeProbValue = document.getElementById('home-prob-value');
    
    if (homeProbBar && homeProbValue) {
        homeProbBar.style.width = (homeProb * 100) + '%';
        homeProbValue.textContent = formatProbability(homeProb);
    }
    
    // Update away probability bar
    const awayProbBar = document.getElementById('away-prob-bar');
    const awayProbValue = document.getElementById('away-prob-value');
    
    if (awayProbBar && awayProbValue) {
        awayProbBar.style.width = (awayProb * 100) + '%';
        awayProbValue.textContent = formatProbability(awayProb);
    }
    
    // Update draw probability bar if applicable
    if (drawProb !== null) {
        const drawProbBar = document.getElementById('draw-prob-bar');
        const drawProbValue = document.getElementById('draw-prob-value');
        
        if (drawProbBar && drawProbValue) {
            drawProbBar.style.width = (drawProb * 100) + '%';
            drawProbValue.textContent = formatProbability(drawProb);
        }
    }
}

/**
 * Update confidence meter display
 * @param {number} confidence - Confidence value between 0 and 1
 */
function updateConfidenceMeter(confidence) {
    const confidenceMeter = document.getElementById('confidence-meter-fill');
    const confidenceValue = document.getElementById('confidence-value');
    
    if (confidenceMeter) {
        confidenceMeter.style.width = (confidence * 100) + '%';
    }
    
    if (confidenceValue) {
        confidenceValue.textContent = formatProbability(confidence, 0);
    }
}
