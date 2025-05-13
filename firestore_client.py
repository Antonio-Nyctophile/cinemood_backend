import firebase_admin
from firebase_admin import credentials, firestore
import base64
import os

# Decode the base64 Firebase service account key from environment variable
firebase_key_b64 = os.environ["FIREBASE_KEY_B64"]
key_bytes = base64.b64decode(firebase_key_b64)

# Write to a temporary JSON file
with open("temp_firebase_key.json", "wb") as f:
    f.write(key_bytes)

# Initialize Firebase Admin SDK
cred = credentials.Certificate("temp_firebase_key.json")
firebase_admin.initialize_app(cred)

# Firestore client
db = firestore.client()

# Default image if none is provided in Firestore
DEFAULT_IMAGE = "https://via.placeholder.com/150x220.png?text=No+Image"

def fetch_movies():
    movies_ref = db.collection("movies")
    movie_list = []

    for doc in movies_ref.stream():
        data = doc.to_dict()
        movie = {
            "id": doc.id,
            "title": data.get("title", "Untitled"),
            "genre": data.get("genre", "Unknown"),
            "emotion": data.get("emotion", "neutral"),
            "image": data.get("image", DEFAULT_IMAGE)
        }
        movie_list.append(movie)

    return movie_list
