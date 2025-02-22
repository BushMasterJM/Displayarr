from flask import Flask
from apps.radarr_count import radarr_count
from apps.sonarr_count import sonarr_count
from apps.radarr_poster import radarr_poster

app = Flask(__name__)

# Register Blueprints
app.register_blueprint(radarr_count, url_prefix="/radarr_count")
app.register_blueprint(sonarr_count, url_prefix="/sonarr_count")
app.register_blueprint(radarr_poster, url_prefix="/radarr_poster")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
