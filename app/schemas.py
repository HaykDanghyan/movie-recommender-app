from pydantic import BaseModel, Field


class TMDBMovieCard(BaseModel):
    tmdb_id: int
    title: str
    poster_url: str | None = None
    release_date: str | None = None
    vote_average: float | None = None


class TMDBGenre(BaseModel):
    id: int
    name: str


class TMDBMovieDetails(BaseModel):
    tmdb_id: int
    title: str
    overview: str | None = None
    release_date: str | None = None
    poster_url: str | None = None
    backdrop_url: str | None = None
    genres: list[TMDBGenre] = Field(default_factory=list)


class TFIDFRecItem(BaseModel):
    title: str
    score: float
    tmdb: TMDBMovieCard | None = None


class SearchBundleResponse(BaseModel):
    query: str
    movie_details: TMDBMovieDetails
    tfidf_recommendations: list[TFIDFRecItem]
    genre_recommendations: list[TMDBMovieCard]
