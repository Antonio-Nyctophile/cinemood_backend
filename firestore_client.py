import firebase_admin
from firebase_admin import credentials, firestore

# Load Firebase Admin SDK
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

def fetch_movies():
    movies_ref = db.collection('movies')
    docs = movies_ref.stream()

    movie_list = []
    for doc in docs:
        movie = doc.to_dict()
        movie['id'] = doc.id
        movie_list.append(movie)
    return movie_list
