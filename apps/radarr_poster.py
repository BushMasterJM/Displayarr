from flask import Blueprint, render_template, send_file
import requests
import os
import random
import time
import threading
from urllib.request import urlretrieve
from config import RADARR_ENDPOINT, RADARR_HEADER, RADARR_URL

# Ensure correct file paths and static folder usage
radarr_poster = Blueprint("radarr_poster", __name__, template_folder="html")

# Define the path where posters will be stored
poster_file_path = os.path.join("static", "poster.jpg")
current_poster = None  # Store the current poster URL globally

def fetch_and_update_poster():
    global current_poster

    while True:
        try:
            response = requests.get(RADARR_ENDPOINT, headers=RADARR_HEADER)
            response.raise_for_status()
            movies = response.json()

            posters = [
                {"title": movie["title"], "url": f"{RADARR_URL}{image['url']}"}
                for movie in movies for image in movie.get("images", [])
                if image.get("coverType") == "poster"
            ]

            if posters:
                random_poster = random.choice(posters)
                current_poster = random_poster["url"]

                # Download the poster to the static folder
                urlretrieve(random_poster["url"], poster_file_path)
                print(f"Updated poster: {random_poster['title']}")

        except requests.exceptions.RequestException as e:
            print(f"Error fetching movies: {e}")

        time.sleep(60)  # Refresh every 1 minute

@radarr_poster.route("/")
def display_poster():
    # Use static folder for serving poster.jpg
    if os.path.exists(poster_file_path):
        return render_template("radarr_poster.html", poster_url="/static/poster.jpg")
    else:
        return "No poster available.", 404

@radarr_poster.route("/static/poster.jpg")
def serve_poster():
    # Serve the poster from the static folder
    if os.path.exists(poster_file_path):
        return send_file(poster_file_path, mimetype="image/jpeg")
    else:
        return "No poster available.", 404

# Start background thread to fetch and update poster
threading.Thread(target=fetch_and_update_poster, daemon=True).start()
