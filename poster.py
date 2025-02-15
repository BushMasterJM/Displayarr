from flask import Flask, render_template, send_file
import requests
from threading import Thread
import time
import os
import random
from urllib.request import urlretrieve

# Flask app setup
app = Flask(__name__, template_folder="radarr_html")

# Radarr API details
RADARR_URL = "http://192.168.1.78:7878"
RADARR_API_KEY = "45aa6b76296641f098c980154795831a"
RADARR_ENDPOINT = f"{RADARR_URL}/api/v3/movie"
RADARR_HEADER = {"X-Api-Key": RADARR_API_KEY}

# Global variables
current_poster = None
poster_file_path = "assets/poster.jpg"

def fetch_and_update_poster():
    global current_poster

    while True:
        try:
            # Fetch all movies
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
                random_poster = random.choice(posters)
                current_poster = random_poster["url"]

                # Download the poster
                urlretrieve(random_poster["url"], poster_file_path)
                print(f"Updated poster: {random_poster['title']}")

                # Wait for 1 minute before updating again
                time.sleep(60)

                # Delete the poster file
                if os.path.exists(poster_file_path):
                    os.remove(poster_file_path)
                    print("Poster file deleted.")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching movies: {e}")
            time.sleep(60)  # Retry after 1 minute

@app.route("/")
def display_poster():
    if os.path.exists(poster_file_path):
        # Render an HTML page that scales the poster for Homarr widgets
        return render_template(
            "poster_widget.html", 
            poster_url="/assets/poster.jpg"
        )
    else:
        return "No poster available.", 404

@app.route("/assets/poster.jpg")
def serve_poster():
    if os.path.exists(poster_file_path):
        return send_file(poster_file_path, mimetype="image/jpeg")
    else:
        return "No poster available.", 404

if __name__ == "__main__":
    # Start the background thread for updating posters
    Thread(target=fetch_and_update_poster, daemon=True).start()

    # Run the Flask app
    app.run(host="0.0.0.0", port=5022)
