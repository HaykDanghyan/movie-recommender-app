from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app.recommender import recommender
from app.schemas import SearchBundleResponse, TFIDFRecItem, TMDBMovieCard, TMDBMovieDetails
from app.tmdb import (
    attach_tmdb_card_by_title,
    tmdb_cards_from_results,
    tmdb_get,
    tmdb_movie_details,
    tmdb_search_first,
    tmdb_search_movies,
)


app = FastAPI(title="Movie Recommender API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def load_recommender() -> None:
    recommender.load()


@app.get("/")
def root():
    return {"message": "Movie Recommender API is running"}


@app.get("/health")
def health():
    return {"status": "ok", "recommender_loaded": recommender.is_loaded()}


@app.get("/movies")
def movies():
    try:
        return {"movies": recommender.get_titles()}
    except RuntimeError as error:
        raise HTTPException(status_code=500, detail=str(error)) from error


@app.get("/home", response_model=list[TMDBMovieCard])
async def home(
    category: str = Query("popular"),
    limit: int = Query(24, ge=1, le=50),
):
    if category == "trending":
        data = await tmdb_get("/trending/movie/day", {"language": "en-US"})
        return tmdb_cards_from_results(data.get("results", []), limit=limit)

    if category not in {"popular", "top_rated", "upcoming", "now_playing"}:
        raise HTTPException(status_code=400, detail="Invalid category")

    data = await tmdb_get(f"/movie/{category}", {"language": "en-US", "page": 1})
    return tmdb_cards_from_results(data.get("results", []), limit=limit)


@app.get("/tmdb/search")
async def tmdb_search(
    query: str = Query(..., min_length=1),
    page: int = Query(1, ge=1, le=10),
):
    return await tmdb_search_movies(query=query, page=page)


@app.get("/movie/id/{tmdb_id}", response_model=TMDBMovieDetails)
async def movie_details_route(tmdb_id: int):
    return await tmdb_movie_details(tmdb_id)


@app.get("/recommend/genre", response_model=list[TMDBMovieCard])
async def recommend_genre(
    tmdb_id: int = Query(...),
    limit: int = Query(18, ge=1, le=50),
):
    details = await tmdb_movie_details(tmdb_id)

    if not details.genres:
        return []

    genre_id = details.genres[0].id
    data = await tmdb_get(
        "/discover/movie",
        {
            "with_genres": genre_id,
            "language": "en-US",
            "sort_by": "popularity.desc",
            "page": 1,
        },
    )
    cards = tmdb_cards_from_results(data.get("results", []), limit=limit)
    return [card for card in cards if card.tmdb_id != tmdb_id]


@app.get("/recommend/tfidf")
def recommend_tfidf(
    title: str = Query(..., min_length=1),
    top_n: int = Query(10, ge=1, le=50),
):
    try:
        recommendations = recommender.recommend_titles(title, top_n=top_n)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except RuntimeError as error:
        raise HTTPException(status_code=500, detail=str(error)) from error

    return [{"title": title, "score": score} for title, score in recommendations]


@app.get("/movie/search", response_model=SearchBundleResponse)
async def search_bundle(
    query: str = Query(..., min_length=1),
    tfidf_top_n: int = Query(12, ge=1, le=30),
    genre_limit: int = Query(12, ge=1, le=30),
):
    best_match = await tmdb_search_first(query)

    if not best_match:
        raise HTTPException(
            status_code=404,
            detail=f"No TMDB movie found for query: {query}",
        )

    details = await tmdb_movie_details(int(best_match["id"]))

    tfidf_items: list[TFIDFRecItem] = []
    recommendations: list[tuple[str, float]] = []

    for title_candidate in (details.title, query):
        try:
            recommendations = recommender.recommend_titles(
                title_candidate,
                top_n=tfidf_top_n,
            )
            break
        except Exception:
            recommendations = []

    for title, score in recommendations:
        tmdb_card = await attach_tmdb_card_by_title(title)
        tfidf_items.append(TFIDFRecItem(title=title, score=score, tmdb=tmdb_card))

    genre_recommendations: list[TMDBMovieCard] = []
    if details.genres:
        data = await tmdb_get(
            "/discover/movie",
            {
                "with_genres": details.genres[0].id,
                "language": "en-US",
                "sort_by": "popularity.desc",
                "page": 1,
            },
        )
        cards = tmdb_cards_from_results(data.get("results", []), limit=genre_limit)
        genre_recommendations = [
            card for card in cards if card.tmdb_id != details.tmdb_id
        ]

    return SearchBundleResponse(
        query=query,
        movie_details=details,
        tfidf_recommendations=tfidf_items,
        genre_recommendations=genre_recommendations,
    )
