from datetime import datetime
from app import db

class Team(db.Model):
    """Team model representing a sports team."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    abbreviation = db.Column(db.String(10), unique=True, nullable=False)
    division = db.Column(db.String(50))
    conference = db.Column(db.String(50))
    
    # Relationships
    home_games = db.relationship('Game', foreign_keys='Game.home_team_id', backref='home_team', lazy='dynamic')
    away_games = db.relationship('Game', foreign_keys='Game.away_team_id', backref='away_team', lazy='dynamic')
    
    def __repr__(self):
        return f'<Team {self.name}>'

class Game(db.Model):
    """Game model representing a match between two teams."""
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    home_team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    away_team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    venue = db.Column(db.String(100))
    
    # Actual game results (to be filled after the game)
    home_score = db.Column(db.Integer)
    away_score = db.Column(db.Integer)
    
    # Relationship to predictions
    predictions = db.relationship('Prediction', backref='game', lazy='dynamic')
    
    def __repr__(self):
        return f'<Game {self.home_team_id} vs {self.away_team_id} on {self.date}>'

class Prediction(db.Model):
    """Prediction model for game outcomes."""
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Predicted scores
    predicted_home_score = db.Column(db.Float, nullable=False)
    predicted_away_score = db.Column(db.Float, nullable=False)
    
    # Confidence scores (percentage)
    home_win_probability = db.Column(db.Float, nullable=False)
    away_win_probability = db.Column(db.Float, nullable=False)
    draw_probability = db.Column(db.Float)
    
    # Accuracy metrics (filled after the game)
    error_margin = db.Column(db.Float)  # Difference between predicted and actual
    was_correct = db.Column(db.Boolean)  # Whether the winner prediction was correct
    
    def __repr__(self):
        return f'<Prediction for Game {self.game_id}>'

    @property
    def prediction_accuracy(self):
        """Calculate prediction accuracy if actual results are available."""
        if not self.game.home_score or not self.game.away_score:
            return None
            
        # Calculate absolute error in score prediction
        home_error = abs(self.predicted_home_score - self.game.home_score)
        away_error = abs(self.predicted_away_score - self.game.away_score)
        
        # Return average error (lower is better)
        return (home_error + away_error) / 2
