from flask import Blueprint, render_template
import requests
import time
import threading
from config import RADARR_ENDPOINT, RADARR_HEADER


radarr_count = Blueprint("radarr_count", __name__, template_folder="html")

movie_count = 0  # Store movie count globally

def update_movie_count():
    global movie_count
    while True:
        try:
            response = requests.get(RADARR_ENDPOINT, headers=RADARR_HEADER)
            response.raise_for_status()
            movies = response.json()
            movie_count = len([movie for movie in movies if movie.get("hasFile", False)])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching movies: {e}")

        time.sleep(60)  # Update every minute

@radarr_count.route("/")
def display_movie_count():
    return render_template("movie_count.html", count=movie_count)

# Start background thread
threading.Thread(target=update_movie_count, daemon=True).start()
