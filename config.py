import os

# Sportmonks API Configuration
SPORTMONKS_API_TOKEN = os.environ.get('SPORTMONKS_API_TOKEN')
SPORTMONKS_API_URL = 'https://api.sportmonks.com/v3/football'

# Default leagues to fetch data for
DEFAULT_LEAGUES = [
    8,    # Premier League (England)
    72,   # Eredivisie (Netherlands)
    82,   # Bundesliga (Germany)
    564,  # La Liga (Spain)
    384,  # Serie A (Italy)
    301,  # Ligue 1 (France)
    207,  # Champions League (Europe)
    5,    # Europa League (Europe)
]

# Application configuration
DEBUG = True
CACHE_TIMEOUT = 3600  # 1 hour