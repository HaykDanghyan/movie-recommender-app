# 🎬 CineMatch — Movie Recommender

> AI-powered movie recommendation engine built with FastAPI + TF-IDF, with a cinematic Streamlit UI. Combines content-based filtering and live TMDB metadata to surface similar films, genre picks, and trending titles in real time.

---

## Features

- **Content-based recommendations** — TF-IDF similarity matching across your movie dataset
- **TMDB integration** — live poster images, ratings, overviews, genres, and runtime
- **Search bundle** — one query returns movie details + TF-IDF picks + genre recommendations
- **Home feed** — browse Popular, Top Rated, Trending, Upcoming, and Now Playing
- **Genre discovery** — find films from the same genre as any TMDB movie
- **Cinematic Streamlit UI** — dark-themed, four-page frontend wired to every API endpoint
- **REST API** — clean FastAPI backend, fully documented via `/docs`

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI, Python 3.11 |
| Recommender | scikit-learn (TF-IDF + cosine similarity) |
| Movie data | TMDB API |
| Frontend | Streamlit |
| HTTP client | httpx (async) |

---

## Project Structure

```
├── app/
│   ├── .env.example         # Example env file
│   ├── config.py            # App configuration
│   ├── main.py              # FastAPI routes
│   ├── recommender.py       # TF-IDF engine
│   ├── schemas.py           # Pydantic models
│   └── tmdb.py              # TMDB API client
├── data/
│   └── movie_data.csv       # Movie dataset
├── frontend/
│   └── streamlit_app.py     # Streamlit UI
├── models/
│   ├── df_model.pkl         # Dataframe model
│   ├── indices.pkl          # Title-to-index mapping
│   ├── tfidf_matrix.pkl     # Precomputed TF-IDF matrix
│   └── tfidf.pkl            # Fitted TF-IDF vectorizer
├── .gitignore
├── Movies.ipynb             # Data exploration & model training notebook
├── README.md
└── requirements.txt
```

## Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/your-username/cinematch.git
cd cinematch
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set environment variables

Create a `.env` file in the project root:

```env
TMDB_API_KEY=your_tmdb_api_key_here
```

Get a free API key at [themoviedb.org](https://www.themoviedb.org/settings/api).

### 4. Run the FastAPI backend

```bash
uvicorn app.main:app --reload
```

API runs at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

### 5. Run the Streamlit frontend

```bash
streamlit run streamlit_app.py
```

UI runs at `http://localhost:8501`.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Health check |
| `GET` | `/health` | Recommender load status |
| `GET` | `/movies` | All titles in the dataset |
| `GET` | `/home` | Browse by category (popular, trending, etc.) |
| `GET` | `/tmdb/search` | Search TMDB for movies |
| `GET` | `/movie/id/{tmdb_id}` | Full movie details |
| `GET` | `/movie/search` | Full search bundle (details + TF-IDF + genre recs) |
| `GET` | `/recommend/tfidf` | TF-IDF recommendations by title |
| `GET` | `/recommend/genre` | Genre-based recommendations by TMDB ID |

---

## Streamlit Pages

| Page | What it does |
|---|---|
| 🏠 Home | Browse curated feeds with a category switcher |
| 🔍 Search & Recommend | Full search — movie detail panel, TF-IDF picks, genre recs |
| 🎭 Genre Picks | Enter a TMDB ID to get genre-based recommendations |
| 📋 Browse Titles | Filterable, paginated list of every title in the dataset |

---

## Screenshots

![Screenshot](image.png)
![Image](image-1.png)

## License

MIT License. See [LICENSE](LICENSE) for details.

---

## Acknowledgements

- [TMDB](https://www.themoviedb.org/) for the movie metadata API
- [FastAPI](https://fastapi.tiangolo.com/) for the backend framework
- [Streamlit](https://streamlit.io/) for the frontend framework