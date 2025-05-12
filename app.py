from flask import Flask, jsonify
from firestore_client import fetch_movies
import os

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({"message": "Cinemood backend is running!"})

@app.route("/movies", methods=["GET"])
def get_movies():
    try:
        movies = fetch_movies()
        return jsonify({"movies": movies})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
