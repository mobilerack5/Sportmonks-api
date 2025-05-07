import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
import logging
from datetime import datetime, timedelta
from models import Game, Team, Prediction
from app import db

# Create a basic prediction model
def create_prediction_model():
    """
    Create and return a trained prediction model using historical game data.
    In a real application, this would be more sophisticated and would use
    more features and possibly a more complex model.
    """
    try:
        # Get historical game data
        games = Game.query.filter(Game.home_score.isnot(None)).all()
        
        # If we don't have enough historical data, use a simple model
        if len(games) < 10:
            logging.warning("Not enough historical data for robust model. Using simplified predictions.")
            return None
            
        # Prepare data for modeling
        X = []  # Features
        y_home = []  # Target: home team score
        y_away = []  # Target: away team score
        
        for game in games:
            # Get the teams
            home_team = Team.query.get(game.home_team_id)
            away_team = Team.query.get(game.away_team_id)
            
            # Calculate team stats (oversimplified for demo)
            home_avg_score = get_team_average_score(home_team.id)
            away_avg_score = get_team_average_score(away_team.id)
            
            # Create feature vector
            # [home_avg_score, away_avg_score, is_home_game]
            X.append([home_avg_score, away_avg_score, 1])  # 1 indicates home game
            
            # Append target values
            y_home.append(game.home_score)
            y_away.append(game.away_score)
            
        # Convert to numpy arrays
        X = np.array(X)
        y_home = np.array(y_home)
        y_away = np.array(y_away)
        
        # Train models
        home_model = RandomForestRegressor(n_estimators=100, random_state=42)
        away_model = RandomForestRegressor(n_estimators=100, random_state=42)
        
        home_model.fit(X, y_home)
        away_model.fit(X, y_away)
        
        return {'home_model': home_model, 'away_model': away_model}
        
    except Exception as e:
        logging.error(f"Error creating prediction model: {str(e)}")
        return None

def get_team_average_score(team_id, last_n_games=5):
    """Calculate the average score for a team based on recent games."""
    # Get recent games where the team played
    recent_home_games = Game.query.filter(
        Game.home_team_id == team_id,
        Game.home_score.isnot(None)
    ).order_by(Game.date.desc()).limit(last_n_games).all()
    
    recent_away_games = Game.query.filter(
        Game.away_team_id == team_id,
        Game.away_score.isnot(None)
    ).order_by(Game.date.desc()).limit(last_n_games).all()
    
    # Calculate average scores
    home_scores = [game.home_score for game in recent_home_games]
    away_scores = [game.away_score for game in recent_away_games]
    
    all_scores = home_scores + away_scores
    
    if all_scores:
        return sum(all_scores) / len(all_scores)
    else:
        # Default value if no historical data
        return 2.5  # Reasonable default for a sports game

def predict_game(home_team, away_team, venue=None):
    """
    Generate a prediction for a game between two teams.
    
    Args:
        home_team: The home team object
        away_team: The away team object
        venue: Optional venue information
        
    Returns:
        Dictionary with prediction results
    """
    try:
        # Create or load prediction model
        model = create_prediction_model()
        
        # Get team statistics
        home_avg_score = get_team_average_score(home_team.id)
        away_avg_score = get_team_average_score(away_team.id)
        
        # Home field advantage factor (simplified)
        home_advantage = 0.2
        
        if model:
            # Use trained model for prediction
            features = np.array([[home_avg_score, away_avg_score, 1]])  # 1 indicates home game
            predicted_home_score = float(model['home_model'].predict(features)[0])
            predicted_away_score = float(model['away_model'].predict(features)[0])
        else:
            # Simplified prediction if we don't have enough data
            predicted_home_score = home_avg_score * (1 + home_advantage)
            predicted_away_score = away_avg_score * (1 - home_advantage)
        
        # Ensure predictions are reasonable
        predicted_home_score = max(0, predicted_home_score)
        predicted_away_score = max(0, predicted_away_score)
        
        # Calculate win probabilities using Poisson distribution (simplified)
        home_win_prob = 0.5 + (predicted_home_score - predicted_away_score) * 0.1
        away_win_prob = 0.5 + (predicted_away_score - predicted_home_score) * 0.1
        
        # Adjust to ensure they're valid probabilities
        if home_win_prob + away_win_prob > 1:
            total = home_win_prob + away_win_prob
            home_win_prob = home_win_prob / total
            away_win_prob = away_win_prob / total
        
        draw_prob = 1 - (home_win_prob + away_win_prob)
        
        # Ensure probabilities are between 0 and 1
        home_win_prob = max(0, min(1, home_win_prob))
        away_win_prob = max(0, min(1, away_win_prob))
        draw_prob = max(0, min(1, draw_prob))
        
        # Round predicted scores for display
        rounded_home_score = round(predicted_home_score, 1)
        rounded_away_score = round(predicted_away_score, 1)
        
        return {
            'home_score': rounded_home_score,
            'away_score': rounded_away_score,
            'home_win_probability': home_win_prob,
            'away_win_probability': away_win_prob,
            'draw_probability': draw_prob,
            'confidence': calculate_confidence_score(home_team.id, away_team.id)
        }
        
    except Exception as e:
        logging.error(f"Error in game prediction: {str(e)}")
        # Return default prediction in case of error
        return {
            'home_score': 1.0,
            'away_score': 1.0,
            'home_win_probability': 0.4,
            'away_win_probability': 0.4,
            'draw_probability': 0.2,
            'confidence': 0.5
        }

def calculate_confidence_score(home_team_id, away_team_id):
    """
    Calculate a confidence score for the prediction based on available data.
    Higher score means more confidence in the prediction.
    """
    # Count how many games we have for each team
    home_games_count = Game.query.filter(
        (Game.home_team_id == home_team_id) | (Game.away_team_id == home_team_id),
        Game.home_score.isnot(None)
    ).count()
    
    away_games_count = Game.query.filter(
        (Game.home_team_id == away_team_id) | (Game.away_team_id == away_team_id),
        Game.home_score.isnot(None)
    ).count()
    
    # Count direct matchups between these teams
    matchups_count = Game.query.filter(
        ((Game.home_team_id == home_team_id) & (Game.away_team_id == away_team_id)) |
        ((Game.home_team_id == away_team_id) & (Game.away_team_id == home_team_id)),
        Game.home_score.isnot(None)
    ).count()
    
    # More games and matchups = higher confidence
    # Calculate a confidence score between 0 and 1
    base_confidence = 0.5
    games_factor = min(1, (home_games_count + away_games_count) / 20) * 0.3
    matchup_factor = min(1, matchups_count / 5) * 0.2
    
    confidence = base_confidence + games_factor + matchup_factor
    
    return min(1, confidence)
