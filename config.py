import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Radarr Configuration
RADARR_URL = os.getenv("RADARR_URL")
RADARR_API_KEY = os.getenv("RADARR_API_KEY")
RADARR_HEADER = {"X-Api-Key": RADARR_API_KEY}
RADARR_ENDPOINT = f"{RADARR_URL}/api/v3/movie"

# Sonarr Configuration
SONARR_URL = os.getenv("SONARR_URL")
SONARR_API_KEY = os.getenv("SONARR_API_KEY")
SONARR_HEADER = {"X-Api-Key": SONARR_API_KEY}
SONARR_ENDPOINT = f"{SONARR_URL}/api/v3/series"
