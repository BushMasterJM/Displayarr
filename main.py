from flask import Flask, jsonify, render_template, send_file
import requests
from threading import Thread
import time
import os
import random
from urllib.request import urlretrieve
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============================
# Flask App Setup for Radarr and Sonarr
# ============================

# Flask app setup
app1 = Flask(__name__, template_folder="html") # Radarr Count
app2 = Flask(__name__, template_folder="html") # Sonarr Count
app3 = Flask(__name__, template_folder="html") # Radarr Poster

# Radarr Poster Location
poster_file_path = "assets/poster.jpg"
current_poster = None  # Initialize global variable for poster URL

# Radarr and Sonarr API details loaded from environment variables
RADARR_API_KEY = os.getenv("RADARR_API_KEY")
SONARR_API_KEY = os.getenv("SONARR_API_KEY")
RADARR_URL = os.getenv("RADARR_URL")
SONARR_URL = os.getenv("SONARR_URL")

# Radarr and Sonarr API Endpoints
RADARR_ENDPOINT = f"{RADARR_URL}/api/v3/movie"
SONARR_ENDPOINT = f"{SONARR_URL}/api/v3/series"

# API Headers
RADARR_HEADER = {"X-Api-Key": RADARR_API_KEY}
SONARR_HEADER = {"x-Api-Key": SONARR_API_KEY}

# Global variables to store counts
movie_count = 0
episode_count = 0

# ============================
# Function to Update Movie and Episode Counts
# ============================

def update_counts():
    global movie_count, episode_count
    while True:
        # Update movie count
        try:
            response = requests.get(RADARR_ENDPOINT, headers=RADARR_HEADER)  # Fetch movie data
            response.raise_for_status()  # Check for errors
            movies = response.json()
            movies_with_files = [movie for movie in movies if movie.get("hasFile", False)]  # Filter movies with files
            movie_count = len(movies_with_files)  # Update global movie count
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Movies: {e}")

        # Update episode count
        try:
            series_response = requests.get(SONARR_ENDPOINT, headers=SONARR_HEADER)  # Fetch series data
            series_response.raise_for_status()
            series_list = series_response.json()

            total_episodes = 0
            for series in series_list:
                series_id = series['id']  # Get the series ID
                episodes_response = requests.get(f"{SONARR_URL}/api/v3/episode?seriesId={series_id}", headers=SONARR_HEADER)
                episodes_response.raise_for_status()
                episodes = episodes_response.json()  # Get the list of episodes
                episodes_with_files = [episode for episode in episodes if episode.get("hasFile", False)]  # Filter episodes with files
                total_episodes += len(episodes_with_files)  # Add to total

            episode_count = total_episodes  # Update global episode count
        except requests.exceptions.RequestException as e:
            print(f"Error fetching TV episodes: {e}")

        time.sleep(60)  # Update every minute


# ============================
# Function to Fetch and Update Posters
# ============================

def fetch_and_update_poster():
    global current_poster

    while True:
        try:
            # Fetch movie data from Radarr
            response = requests.get(RADARR_ENDPOINT, headers=RADARR_HEADER)
            response.raise_for_status()
            movies = response.json()

            # Select a random movie with a poster
            posters = []
            for movie in movies:
                for image in movie.get("images", []):
                    if image.get("coverType") == "poster":
                        posters.append({"title": movie["title"], "url": f"{RADARR_URL}{image['url']}"})

            if posters:
                random_poster = random.choice(posters)  # Select a random poster
                current_poster = random_poster["url"]

                # Download the poster
                urlretrieve(random_poster["url"], poster_file_path)
                print(f"Updated poster: {random_poster['title']}")

                time.sleep(60)  # Wait for 1 minute before updating again
        except requests.exceptions.RequestException as e:
            print(f"Error fetching movies: {e}")
            time.sleep(60)  # Retry after 1 minute


# ============================
# Flask Routes for Displaying Counts and Poster
# ============================

@app1.route("/")  # Radarr movie count route
def display_movie_count():
    if movie_count is None:
        return "Error fetching movie count", 500
    return render_template("movie_count.html", count=movie_count)

@app2.route("/")  # Sonarr episode count route
def display_episode_count():
    if episode_count is None:
        return "Error fetching episode count", 500
    return render_template("episode_count.html", count=episode_count)

@app3.route("/")  # Radarr poster display route
def display_poster():
    if os.path.exists(poster_file_path):
        return render_template("poster_widget.html", poster_url="/assets/poster.jpg")
    else:
        return "No poster available.", 404

@app3.route("/assets/poster.jpg")  # Serve poster image
def serve_poster():
    if os.path.exists(poster_file_path):
        return send_file(poster_file_path, mimetype="image/jpeg")
    else:
        return "No poster available.", 404

# ============================
# Main Program Execution
# ============================

if __name__ == "__main__":
    # Start the background thread for updating counts
    Thread(target=update_counts, daemon=True).start()

    # Start the background thread for fetching and updating posters
    Thread(target=fetch_and_update_poster, daemon=True).start()

    # Run Flask apps for Radarr and Sonarr counts
    Thread(target=lambda: app1.run(host="0.0.0.0", port=5020)).start()
    Thread(target=lambda: app2.run(host="0.0.0.0", port=5021)).start()

    # Run Flask app for poster display
    app3.run(host="0.0.0.0", port=5022)
