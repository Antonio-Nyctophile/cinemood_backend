import firebase_admin
from firebase_admin import credentials, firestore
import base64
import os

# Decode the base64 Firebase key into a temp file
firebase_key_b64 = os.environ["FIREBASE_KEY_B64"]
key_bytes = base64.b64decode(firebase_key_b64)

with open("temp_firebase_key.json", "wb") as f:
    f.write(key_bytes)

cred = credentials.Certificate("temp_firebase_key.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

def fetch_movies():
    movies_ref = db.collection("movies")
    return [doc.to_dict() | {"id": doc.id} for doc in movies_ref.stream()]
