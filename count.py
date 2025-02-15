from flask import Flask, jsonify, render_template
import requests
from threading import Thread
import time

# Flask app setup
app1 = Flask(__name__, template_folder="radarr_html")
app2 = Flask(__name__, template_folder="sonarr_html")

# Replace with your Radarr/Sonarr details
RADARR_API_KEY = "45aa6b76296641f098c980154795831a"
SONARR_API_KEY = "79474f19da6a47aba840267d54656235"
RADARR_URL = "http://192.168.1.78:7878"
SONARR_URL = "http://192.168.1.78:8989"

# Endpoints
RADARR_ENDPOINT = f"{RADARR_URL}/api/v3/movie"
SONARR_ENDPOINT = f"{SONARR_URL}/api/v3/series"

# API Key Headers
RADARR_HEADER = {
    "X-Api-Key": RADARR_API_KEY
}
SONARR_HEADER = {
    "x-Api-Key": SONARR_API_KEY
}

# Global variables to store counts
movie_count = 0
episode_count = 0

def update_counts():
    global movie_count, episode_count
    while True:
        # Update movie count
        try:
            response = requests.get(RADARR_ENDPOINT, headers=RADARR_HEADER)  # Endpoint for Radarr
            response.raise_for_status()  # Checks for error
            movies = response.json()  # Puts response in a variable
            movies_with_files = [movie for movie in movies if movie.get("hasFile", False)]  # Filter movies with files
            movie_count = len(movies_with_files)  # Updates global count
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Movies: {e}")

        # Update episode count
        try:
            series_response = requests.get(SONARR_ENDPOINT, headers=SONARR_HEADER)
            series_response.raise_for_status()
            series_list = series_response.json()  # List of all series

            total_episodes = 0
            for series in series_list:
                series_id = series['id']  # Get the series ID
                episodes_response = requests.get(f"{SONARR_URL}/api/v3/episode?seriesId={series_id}", headers=SONARR_HEADER)
                episodes_response.raise_for_status()
                episodes = episodes_response.json()  # List of episodes for the series
                episodes_with_files = [episode for episode in episodes if episode.get("hasFile", False)]  # Filter episodes with files
                total_episodes += len(episodes_with_files)  # Add to total

            episode_count = total_episodes  # Updates global count
        except requests.exceptions.RequestException as e:
            print(f"Error fetching TV episodes: {e}")

        time.sleep(60)  # Wait for 1 minute before updating again

@app1.route("/")
def display_movie_count():
    if movie_count is None:
        return "Error fetching movie count", 500
    return render_template("movie_count.html", count=movie_count)

@app2.route("/")
def display_episode_count():
    if episode_count is None:
        return "Error fetching episode count", 500
    return render_template("episode_count.html", count=episode_count)

def run_app1():
    app1.run(host="0.0.0.0", port=5020)

def run_app2():
    app2.run(host="0.0.0.0", port=5021)

if __name__ == "__main__":
    # Start the background thread for periodic updates
    Thread(target=update_counts, daemon=True).start()

    # Run Flask apps
    Thread(target=run_app1).start()
    Thread(target=run_app2).start()
