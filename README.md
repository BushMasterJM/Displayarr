# Displayarr

A set of Flask-based applications for displaying Radarr and Sonarr data, including movie and episode counts, and fetching random movie posters from Radarr. This is primary for use with Homarr but could be edited to work with whatever setup you have.

## Features

- Displays movie counts from Radarr.
- Displays episode counts from Sonarr.
- Displays a random movie poster from Radarr.


## Installation

### Clone the repository

1. Clone the repository to your local machine:

2. In the project root, create a docker-compose.yml file with the following content:

```
version: '3.8'

services:
  flask-app:
    image: python:3.10-slim
    container_name: flask-app
    working_dir: /app
    volumes:
      - /PATH/TO/YOUR/APP:/app
    ports:
      - "5000:5000"
    command: >
      bash -c "pip install -r requirements.txt &&
               python main.py"
```
## Environment Configuration
3. Edit the .env file with your api keys and urls
```
RADARR_API_KEY=your-radarr-api-key
SONARR_API_KEY=your-sonarr-api-key
RADARR_URL=http://192.168.1.0:7878
SONARR_URL=http://192.168.1.0:8989
```
## Running the App with Docker
Build and start the app with Docker Compose:
`docker-compose up --build`

The Flask app will be accessible on the following sub domains:
```
"/radarr_count": Radarr movie count
"/sonarr_count": Sonarr episode count
"/radarr_poster": Radarr poster display
```
## Configuration

Since this is just a python script and some HTML, you can edit the HTML to your liking so that it works for whatever setup you have.

## Disclaimer: 
This script was mainly written by ChatGPT and then edited by me because I couldn't be bothered to write it myself.
