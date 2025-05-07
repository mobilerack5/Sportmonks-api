from flask import render_template, request, jsonify, redirect, url_for, flash
from app import db
from models import Team, Game, Prediction
from prediction import predict_game
from datetime import datetime, timedelta
import pandas as pd
import os
import logging
from sportmonks_api import SportmonksAPI
from config import DEFAULT_LEAGUES

def init_routes(app):
    @app.route("/")
    def index():
        """Home page with prediction form."""
        # Get all teams for the dropdown selectors
        teams = Team.query.order_by(Team.name).all()
        
        # If no teams exist in the database, load from CSV
        if not teams:
            load_initial_data()
            teams = Team.query.order_by(Team.name).all()
        
        # Get recent predictions for the sidebar
        recent_predictions = Prediction.query.order_by(Prediction.created_at.desc()).limit(5).all()
            
        return render_template("index.html", teams=teams, recent_predictions=recent_predictions)

    @app.route("/predict", methods=["POST"])
    def predict():
        """Process the prediction form and generate prediction."""
        try:
            # Get form data
            home_team_id = int(request.form.get("home_team"))
            away_team_id = int(request.form.get("away_team"))
            venue = request.form.get("venue")
            
            # Parse date (format: YYYY-MM-DD)
            game_date_str = request.form.get("game_date")
            game_date = datetime.strptime(game_date_str, "%Y-%m-%d")
            
            # Validation
            if home_team_id == away_team_id:
                flash("Home and away teams must be different.", "danger")
                return redirect(url_for("index"))
                
            # Create or get existing game
            existing_game = Game.query.filter_by(
                home_team_id=home_team_id,
                away_team_id=away_team_id,
                date=game_date
            ).first()
            
            if existing_game:
                game = existing_game
            else:
                game = Game(
                    home_team_id=home_team_id,
                    away_team_id=away_team_id,
                    date=game_date,
                    venue=venue
                )
                db.session.add(game)
                db.session.flush()  # To get the game ID
            
            # Generate prediction
            home_team = Team.query.get(home_team_id)
            away_team = Team.query.get(away_team_id)
            
            prediction_results = predict_game(home_team, away_team, venue)
            
            # Save prediction
            prediction = Prediction(
                game_id=game.id,
                predicted_home_score=prediction_results["home_score"],
                predicted_away_score=prediction_results["away_score"],
                home_win_probability=prediction_results["home_win_probability"],
                away_win_probability=prediction_results["away_win_probability"],
                draw_probability=prediction_results["draw_probability"]
            )
            
            db.session.add(prediction)
            db.session.commit()
            
            # Redirect to prediction result page
            return redirect(url_for("prediction_detail", prediction_id=prediction.id))
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error in prediction: {str(e)}")
            flash(f"Error generating prediction: {str(e)}", "danger")
            return redirect(url_for("index"))

    @app.route("/prediction/<int:prediction_id>")
    def prediction_detail(prediction_id):
        """Display detailed prediction results."""
        prediction = Prediction.query.get_or_404(prediction_id)
        game = prediction.game
        home_team = Team.query.get(game.home_team_id)
        away_team = Team.query.get(game.away_team_id)
        
        # Get recent predictions for these teams
        recent_home_predictions = Prediction.query.join(Game).filter(
            (Game.home_team_id == home_team.id) | (Game.away_team_id == home_team.id)
        ).order_by(Prediction.created_at.desc()).limit(5).all()
        
        recent_away_predictions = Prediction.query.join(Game).filter(
            (Game.home_team_id == away_team.id) | (Game.away_team_id == away_team.id)
        ).order_by(Prediction.created_at.desc()).limit(5).all()
        
        return render_template(
            "predictions.html", 
            prediction=prediction,
            game=game,
            home_team=home_team,
            away_team=away_team,
            recent_home_predictions=recent_home_predictions,
            recent_away_predictions=recent_away_predictions
        )

    @app.route("/history")
    def history():
        """Show prediction history and accuracy metrics."""
        # Get all predictions with their games and teams
        predictions = Prediction.query.order_by(Prediction.created_at.desc()).all()
        
        # Calculate overall accuracy metrics
        total_predictions = len(predictions)
        correct_predictions = sum(1 for p in predictions if p.was_correct)
        
        if total_predictions > 0:
            accuracy_rate = (correct_predictions / total_predictions) * 100
        else:
            accuracy_rate = 0
            
        # Group predictions by date for charting
        prediction_dates = {}
        for p in predictions:
            date_str = p.created_at.strftime("%Y-%m-%d")
            if date_str not in prediction_dates:
                prediction_dates[date_str] = {"total": 0, "correct": 0}
            
            prediction_dates[date_str]["total"] += 1
            if p.was_correct:
                prediction_dates[date_str]["correct"] += 1
        
        # Convert to lists for charts.js
        chart_labels = list(prediction_dates.keys())
        chart_accuracy = [
            (prediction_dates[date]["correct"] / prediction_dates[date]["total"]) * 100 
            if prediction_dates[date]["total"] > 0 else 0
            for date in chart_labels
        ]
        
        return render_template(
            "history.html",
            predictions=predictions,
            total_predictions=total_predictions,
            correct_predictions=correct_predictions,
            accuracy_rate=accuracy_rate,
            chart_labels=chart_labels,
            chart_accuracy=chart_accuracy
        )

    @app.route("/about")
    def about():
        """About page with information about the prediction model."""
        return render_template("about.html")

    @app.route("/api/predictions", methods=["GET"])
    def api_predictions():
        """API endpoint to get prediction data for charts."""
        days = request.args.get("days", 30, type=int)
        
        # Get predictions from the last X days
        start_date = datetime.now() - timedelta(days=days)
        predictions = Prediction.query.filter(Prediction.created_at >= start_date).all()
        
        # Prepare data for front-end charts
        prediction_data = []
        for p in predictions:
            game = p.game
            home_team = Team.query.get(game.home_team_id)
            away_team = Team.query.get(game.away_team_id)
            
            prediction_data.append({
                "id": p.id,
                "date": p.created_at.strftime("%Y-%m-%d"),
                "match": f"{home_team.name} vs {away_team.name}",
                "predicted_home_score": p.predicted_home_score,
                "predicted_away_score": p.predicted_away_score,
                "actual_home_score": game.home_score,
                "actual_away_score": game.away_score,
                "home_win_probability": p.home_win_probability,
                "away_win_probability": p.away_win_probability,
                "draw_probability": p.draw_probability,
                "was_correct": p.was_correct
            })
            
        return jsonify(prediction_data)

    @app.route("/fetch-teams-api", methods=["GET"])
    def fetch_teams_api():
        """Frissíti a csapatokat a Sportmonks API-ból."""
        try:
            api = SportmonksAPI()
            teams_data = api.fetch_teams_for_prediction()
            
            if not teams_data:
                flash("Nem sikerült adatokat lekérni a Sportmonks API-ból. Ellenőrizd az API tokent.", "danger")
                return redirect(url_for("index"))
            
            # Mentjük az új csapatokat
            count_new = 0
            for team_data in teams_data:
                # Ellenőrizzük, hogy már létezik-e a csapat
                existing_team = Team.query.filter_by(name=team_data["name"]).first()
                
                if not existing_team:
                    team = Team(
                        name=team_data["name"],
                        abbreviation=team_data["abbreviation"],
                        division=team_data["division"],
                        conference=team_data["conference"]
                    )
                    db.session.add(team)
                    count_new += 1
            
            db.session.commit()
            flash(f"{count_new} új csapat sikeresen hozzáadva a Sportmonks API-ból!", "success")
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Hiba a Sportmonks API adatok betöltésekor: {str(e)}")
            flash(f"Hiba történt: {str(e)}", "danger")
            
        return redirect(url_for("index"))

    def load_initial_data():
        """Load initial team data from CSV files or API."""
        try:
            # Először próbáljuk meg betölteni az adatokat a Sportmonks API-ból
            api = SportmonksAPI()
            teams_data = api.fetch_teams_for_prediction()
            
            if teams_data:
                # API adatok sikeresen lekérve
                for team_data in teams_data:
                    team = Team(
                        name=team_data["name"],
                        abbreviation=team_data["abbreviation"],
                        division=team_data["division"],
                        conference=team_data["conference"]
                    )
                    db.session.add(team)
                
                logging.info("Csapatok sikeresen betöltve a Sportmonks API-ból")
            else:
                # Ha az API nem működik, betöltjük a helyi CSV-ből
                teams_path = os.path.join("data", "teams.csv")
                teams_df = pd.read_csv(teams_path)
                
                for _, row in teams_df.iterrows():
                    team = Team(
                        name=row["name"],
                        abbreviation=row["abbreviation"],
                        division=row.get("division", ""),
                        conference=row.get("conference", "")
                    )
                    db.session.add(team)
                
                logging.info("Csapatok sikeresen betöltve a helyi CSV fájlból")
            
            # Mentjük a csapatokat
            db.session.commit()
            
            # Opcionálisan betöltünk minta mérkőzés adatokat
            games_path = os.path.join("data", "sample_game_data.csv")
            if os.path.exists(games_path):
                games_df = pd.read_csv(games_path)
                
                for _, row in games_df.iterrows():
                    # Lekérjük a csapat azonosítókat
                    home_team = Team.query.filter_by(name=row["home_team"]).first()
                    away_team = Team.query.filter_by(name=row["away_team"]).first()
                    
                    if home_team and away_team:
                        # Létrehozzuk a mérkőzést
                        game_date = datetime.strptime(row["date"], "%Y-%m-%d")
                        game = Game(
                            date=game_date,
                            home_team_id=home_team.id,
                            away_team_id=away_team.id,
                            venue=row.get("venue", ""),
                            home_score=row.get("home_score"),
                            away_score=row.get("away_score")
                        )
                        db.session.add(game)
                
                db.session.commit()
                logging.info("Minta mérkőzés adatok sikeresen betöltve")
                
            logging.info("Kezdeti adatok sikeresen betöltve")
        except Exception as e:
            db.session.rollback()
            logging.error(f"Hiba a kezdeti adatok betöltésekor: {str(e)}")
