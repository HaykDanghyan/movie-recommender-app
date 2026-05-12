import os
from dotenv import load_dotenv
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv()

TMDB_API_KEY = os.getenv('TMDB_API_KEY')
TMDB_BASE = 'https://api.themoviedb.org/3'
TMDB_IMG_500 = 'https://image.tmdb.org/t/p/w500'
API_BASE = "http://localhost:8000"

MODEL_DIR = BASE_DIR / 'models'
DF_PATH = MODEL_DIR / 'df_model.pkl'
INDICES_PATH = MODEL_DIR / 'indices.pkl'
TFIDF_MATRIX_PATH = MODEL_DIR / 'tfidf_matrix.pkl'
TFIDF_PATH = MODEL_DIR / 'tfidf.pkl'

