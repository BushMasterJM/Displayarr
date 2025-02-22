from flask import Blueprint, render_template
import requests
import time
import threading
from config import SONARR_ENDPOINT, SONARR_HEADER, SONARR_URL

sonarr_count = Blueprint("sonarr_count", __name__, template_folder="templates")

episode_count = 0  # Store episode count globally

def update_episode_count():
    global episode_count
    while True:
        try:
            response = requests.get(SONARR_ENDPOINT, headers=SONARR_HEADER)
            response.raise_for_status()
            series_list = response.json()

            total_episodes = 0
            for series in series_list:
                series_id = series["id"]
                episodes_response = requests.get(f"{SONARR_URL}/api/v3/episode?seriesId={series_id}", headers=SONARR_HEADER)
                episodes_response.raise_for_status()
                episodes = episodes_response.json()
                total_episodes += len([ep for ep in episodes if ep.get("hasFile", False)])

            episode_count = total_episodes
        except requests.exceptions.RequestException as e:
            print(f"Error fetching TV episodes: {e}")

        time.sleep(60)  # Update every minute

@sonarr_count.route("/")
def display_episode_count():
    return render_template("episode_count.html", count=episode_count)

# Start background thread
threading.Thread(target=update_episode_count, daemon=True).start()
