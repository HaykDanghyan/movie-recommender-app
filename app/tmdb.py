from typing import Any

import httpx
from fastapi import HTTPException

from app.config import TMDB_API_KEY, TMDB_BASE, TMDB_IMG_500
from app.schemas import TMDBMovieCard, TMDBMovieDetails


def make_img_url(path: str | None) -> str | None:
    if not path:
        return None
    return f"{TMDB_IMG_500}{path}"


async def tmdb_get(path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    if not TMDB_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="TMDB_API_KEY missing. Add it to your .env file.",
        )

    query_params = dict(params or {})
    query_params["api_key"] = TMDB_API_KEY

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(f"{TMDB_BASE}{path}", params=query_params)
    except httpx.RequestError as error:
        raise HTTPException(
            status_code=502,
            detail=f"TMDB request failed: {type(error).__name__}",
        ) from error

    if response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail=f"TMDB error {response.status_code}: {response.text}",
        )

    return response.json()


def tmdb_cards_from_results(
    results: list[dict[str, Any]], limit: int = 20
) -> list[TMDBMovieCard]:
    cards: list[TMDBMovieCard] = []

    for movie in (results or [])[:limit]:
        cards.append(
            TMDBMovieCard(
                tmdb_id=int(movie["id"]),
                title=movie.get("title") or movie.get("name") or "",
                poster_url=make_img_url(movie.get("poster_path")),
                release_date=movie.get("release_date"),
                vote_average=movie.get("vote_average"),
            )
        )

    return cards


async def tmdb_movie_details(movie_id: int) -> TMDBMovieDetails:
    data = await tmdb_get(f"/movie/{movie_id}", {"language": "en-US"})

    return TMDBMovieDetails(
        tmdb_id=int(data["id"]),
        title=data.get("title") or "",
        overview=data.get("overview"),
        release_date=data.get("release_date"),
        poster_url=make_img_url(data.get("poster_path")),
        backdrop_url=make_img_url(data.get("backdrop_path")),
        genres=data.get("genres", []) or [],
    )


async def tmdb_search_movies(query: str, page: int = 1) -> dict[str, Any]:
    return await tmdb_get(
        "/search/movie",
        {
            "query": query,
            "include_adult": "false",
            "language": "en-US",
            "page": page,
        },
    )


async def tmdb_search_first(query: str) -> dict[str, Any] | None:
    data = await tmdb_search_movies(query=query, page=1)
    results = data.get("results", [])
    return results[0] if results else None


async def attach_tmdb_card_by_title(title: str) -> TMDBMovieCard | None:
    try:
        movie = await tmdb_search_first(title)
    except Exception:
        return None

    if not movie:
        return None

    return TMDBMovieCard(
        tmdb_id=int(movie["id"]),
        title=movie.get("title") or title,
        poster_url=make_img_url(movie.get("poster_path")),
        release_date=movie.get("release_date"),
        vote_average=movie.get("vote_average"),
    )
