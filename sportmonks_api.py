import requests
import logging
import time
from config import SPORTMONKS_API_TOKEN, SPORTMONKS_API_URL, DEFAULT_LEAGUES

# Logger beállítása
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SportmonksAPI:
    """Az osztály a Sportmonks API-val való kommunikációhoz."""
    
    def __init__(self, api_token=None):
        """
        Inicializálja a Sportmonks API klienst.
        
        Args:
            api_token: Sportmonks API token. Ha nincs megadva, a konfigurációs fájlból olvassa ki.
        """
        self.api_token = api_token or SPORTMONKS_API_TOKEN
        self.base_url = SPORTMONKS_API_URL
        self.headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Accept': 'application/json',
        }
        
    def make_request(self, endpoint, params=None):
        """
        API kérés végrehajtása.
        
        Args:
            endpoint: Az API végpont elérési útja.
            params: Opcionális paraméterek a kéréshez.
            
        Returns:
            dict: A válasz adatok.
        """
        if not self.api_token:
            logger.error("Sportmonks API token nincs beállítva.")
            return None
        
        url = f"{self.base_url}/{endpoint}"
        default_params = {'include': ''}
        
        if params:
            default_params.update(params)
            
        try:
            response = requests.get(url, headers=self.headers, params=default_params)
            response.raise_for_status()
            return response.json()['data']
        except requests.exceptions.RequestException as e:
            logger.error(f"API kérés hiba: {e}")
            return None
        except (KeyError, ValueError) as e:
            logger.error(f"Válasz feldolgozási hiba: {e}")
            return None
    
    def get_leagues(self, params=None):
        """
        Bajnokságok adatainak lekérése.
        
        Returns:
            list: Bajnokságok adatai.
        """
        return self.make_request('leagues', params)
    
    def get_teams(self, params=None):
        """
        Csapatok adatainak lekérése.
        
        Returns:
            list: Csapatok adatai.
        """
        return self.make_request('teams', params)
    
    def get_team_by_id(self, team_id):
        """
        Csapat adatainak lekérése azonosító alapján.
        
        Args:
            team_id: A csapat azonosítója.
            
        Returns:
            dict: A csapat adatai.
        """
        teams = self.make_request(f'teams/{team_id}')
        return teams[0] if teams else None
    
    def get_players(self, params=None):
        """
        Játékosok adatainak lekérése.
        
        Returns:
            list: Játékosok adatai.
        """
        return self.make_request('players', params)
    
    def get_coaches(self, params=None):
        """
        Edzők adatainak lekérése.
        
        Returns:
            list: Edzők adatai.
        """
        return self.make_request('coaches', params)
    
    def get_season_statistics(self, participant, season_id, params=None):
        """
        Szezon statisztikák lekérése.
        
        Args:
            participant: Résztvevő típusa (pl. "team").
            season_id: A szezon azonosítója.
            
        Returns:
            dict: A szezon statisztikák.
        """
        return self.make_request(f'statistics/seasons/{participant}/{season_id}', params)
    
    def get_topscorers(self, season_id, params=None):
        """
        Góllövőlista lekérése egy szezonra.
        
        Args:
            season_id: A szezon azonosítója.
            
        Returns:
            list: A góllövőlista.
        """
        return self.make_request(f'topscorers/seasons/{season_id}', params)
    
    def fetch_teams_for_prediction(self, league_ids=None):
        """
        Csapatok lekérése a predikciós modellhez.
        
        Args:
            league_ids: A ligák azonosítói. Ha nincs megadva, az alapértelmezett ligákat használja.
            
        Returns:
            list: Feldolgozott csapat adatok.
        """
        if league_ids is None:
            league_ids = DEFAULT_LEAGUES
            
        all_teams = []
        
        for league_id in league_ids:
            params = {'filters': f'league_id:{league_id}'}
            teams = self.get_teams(params)
            
            if teams:
                for team in teams:
                    # Feldolgozás a prediction modell számára
                    team_data = {
                        'id': team.get('id'),
                        'name': team.get('name'),
                        'abbreviation': team.get('short_code', ''),
                        'division': team.get('league', {}).get('name', ''),
                        'conference': team.get('country', {}).get('name', ''),
                    }
                    all_teams.append(team_data)
            
            # Kis szünet a kérések között, hogy ne lépjük túl a rate limitet
            time.sleep(0.5)
            
        return all_teams

# Egyszerű tesztfunkció
def test_api_connection():
    """
    Teszteli az API kapcsolatot.
    """
    api = SportmonksAPI()
    leagues = api.get_leagues({'limit': 5})
    
    if leagues:
        logger.info("API kapcsolat sikeres!")
        logger.info(f"Példa liga adat: {leagues[0]['name']}")
        return True
    else:
        logger.error("Nem sikerült csatlakozni a Sportmonks API-hoz.")
        return False
        
if __name__ == "__main__":
    test_api_connection()