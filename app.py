from flask import Flask, request, jsonify
from firestore_client import fetch_movies
from model_loader import predict_emotion  # Optional
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return jsonify({"message": "Cinemood backend is live!"})

@app.route("/movies", methods=["GET"])
def get_movies():
    try:
        return jsonify({"movies": fetch_movies()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/emotion", methods=["POST"])
def get_emotion():
    try:
        data = request.get_json()
        text = data.get("text")
        if not text:
            return jsonify({"error": "Missing 'text'"}), 400
        emotion = predict_emotion(text)
        return jsonify({"emotion": emotion})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/recommend", methods=["POST"])
def recommend_movies():
    try:
        data = request.get_json()
        text = data.get("text")
        emotion = predict_emotion(text)
        all_movies = fetch_movies()
        top = [m for m in all_movies if m.get("emotion", "").lower() == emotion.lower()][:5]
        return jsonify({"emotion": emotion, "recommendations": top})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
