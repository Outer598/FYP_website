from flask import render_template, Blueprint, jsonify, request
import requests
import os


home_route = Blueprint("home", __name__)


@home_route.route("/")
def home():
    api_url = os.getenv('API_LINK')
    response = requests.get(api_url, headers={'X-Api-Key': os.getenv('API_KEY')})
    quote = {}
    if response.status_code == requests.codes.ok:
        try:
            quote = response.json()
            print(f"Quote data: {quote[0]}")  # For debugging
        except:
            print("Failed to parse JSON response")
            print(f"Response text: {response.text}")
    return render_template("home.html", quote = quote[0],)