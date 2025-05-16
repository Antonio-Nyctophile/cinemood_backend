from flask import Flask, request, jsonify
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import pandas as pd
import ast
import requests
from urllib.parse import quote
import random
import numpy as np
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# --- Initialize Movie Data ---
# Load movie data
try:
    movies = pd.read_csv('cleaned_dataset.csv')
    # Convert string representation of lists to actual lists
    movies['genres'] = movies['genres'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
    
    # Normalize ratings to 0-5 scale if needed
    if 'Ratings' in movies.columns:
        movies['rating_5'] = movies['Ratings'] / 2  # Convert 0-10 scale to 0-5
    else:
        movies['rating_5'] = np.random.uniform(2.5, 5, len(movies))  # Mock ratings if none exist
    
    data_loaded = True
except Exception as e:
    print(f"Error loading movie data: {e}")
    data_loaded = False

# --- Emotion Model Setup ---
try:
    model_name = "nateraw/bert-base-uncased-emotion"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    label_list = [label for _, label in sorted(model.config.id2label.items())]
    model_loaded = True
except Exception as e:
    print(f"Error loading emotion model: {e}")
    model_loaded = False

# --- Data Preparation ---
# Build emotion-to-genre map
emotion_genre_map = {
    'joy': ['Comedy', 'Animation', 'Adventure', 'Family', 'Fantasy'],
    'sadness': ['Drama', 'Romance', 'War', 'Music'],
    'anger': ['Action', 'Crime', 'Thriller', 'War'],
    'fear': ['Horror', 'Thriller', 'Mystery', 'Science Fiction'],
    'surprise': ['Mystery', 'Science Fiction', 'Fantasy', 'Adventure'],
    'love': ['Romance', 'Drama', 'Comedy'],
}

# Build genre-to-movies map with ratings
genre_movies = {}

if data_loaded:
    for _, row in movies.iterrows():
        for genre in row['genres']:
            genre_lower = genre.lower()
            if genre_lower not in genre_movies:
                genre_movies[genre_lower] = []
            
            movie_info = {
                'title': row['movie_name'],
                'rating': row.get('rating_5', 3.0),
                'raw_rating': row.get('Ratings', None)
            }
            genre_movies[genre_lower].append(movie_info)

# --- Helper Functions ---
def predict_emotion(text):
    if not model_loaded:
        return "unknown"
    
    model.eval()
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        predicted_class_id = torch.argmax(logits, dim=1).item()
        return label_list[predicted_class_id]

def get_movie_poster(movie_title):
    try:
        url = f"http://www.omdbapi.com/?t={quote(movie_title)}&apikey=60b53830"
        response = requests.get(url).json()
        return response.get("Poster") if response.get("Poster") != "N/A" else None
    except:
        return None

def get_recommendations(genre, n=5, sort_by_rating=False):
    """Get recommendations with sorting option"""
    movies_in_genre = genre_movies.get(genre.lower(), [])
    
    if sort_by_rating:
        movies_in_genre = sorted(movies_in_genre, key=lambda x: x['rating'], reverse=True)[:n]
    else:
        if len(movies_in_genre) > n:
            movies_in_genre = random.sample(movies_in_genre, n)
    
    return movies_in_genre[:n]

# --- API Routes ---
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'ok',
        'model_loaded': model_loaded,
        'data_loaded': data_loaded,
        'genres_available': list(genre_movies.keys()) if data_loaded else []
    })

@app.route('/api/emotion', methods=['POST'])
def detect_emotion():
    data = request.json
    if not data or 'text' not in data:
        return jsonify({'error': 'Missing text field'}), 400
    
    emotion = predict_emotion(data['text'])
    suggested_genres = emotion_genre_map.get(emotion, ["drama"])
    
    return jsonify({
        'emotion': emotion,
        'suggested_genres': suggested_genres
    })

@app.route('/api/genres', methods=['GET'])
def get_genres():
    return jsonify({
        'genres': sorted(list(genre_movies.keys()))
    })

@app.route('/api/recommend', methods=['GET'])
def recommend_movies():
    genre = request.args.get('genre', '').lower()
    count = int(request.args.get('count', 5))
    sort = request.args.get('sort', 'false').lower() == 'true'
    
    if not genre:
        return jsonify({'error': 'Missing genre parameter'}), 400
    
    if genre not in genre_movies:
        return jsonify({
            'error': f'Genre "{genre}" not found',
            'available_genres': sorted(list(genre_movies.keys()))
        }), 404
    
    recommendations = get_recommendations(genre, n=count, sort_by_rating=sort)
    
    # Enhance recommendations with posters
    enhanced_recommendations = []
    for movie in recommendations:
        poster_url = get_movie_poster(movie['title'])
        enhanced_recommendations.append({
            'title': movie['title'],
            'rating': float(movie['rating']),
            'poster_url': poster_url,
            'tmdb_link': f"https://www.themoviedb.org/search?query={quote(movie['title'])}"
        })
    
    return jsonify({
        'genre': genre,
        'sorted_by_rating': sort,
        'recommendations': enhanced_recommendations
    })

@app.route('/recommendy', methods=['POST'])
def recommendy():
    data = request.json
    text = data.get('text', '')
    
    # Emotion prediction
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    emotion = label_list[torch.argmax(outputs.logits).item()]
    
    # Get suggested genres
    suggested_genres = emotion_genre_map.get(emotion, ['drama'])
    
    # Get recommendations
    selected_genre = data.get('genre', '').lower()
    movies_in_genre = genre_movies.get(selected_genre, [])
    
    if not selected_genre:  # If no genre selected, pick first suggested
        selected_genre = suggested_genres[0]
        movies_in_genre = genre_movies.get(selected_genre, [])
    
    recommendations = random.sample(movies_in_genre, min(5, len(movies_in_genre))) if movies_in_genre else []
    
    return jsonify({
        'emotion': emotion,
        'suggested_genres': suggested_genres,
        'selected_genre': selected_genre,
        'movies': [{
            'title': m['title'],
            'rating': m['rating'],
            'tmdb_link': f"https://www.themoviedb.org/search?query={quote(m['title'])}"
        } for m in recommendations]
    })
if __name__ == '__main__':
    app.run(debug=True)
