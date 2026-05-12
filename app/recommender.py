from typing import Any

import joblib
import numpy as np
import pandas as pd

from app.config import DF_PATH, INDICES_PATH, TFIDF_MATRIX_PATH, TFIDF_PATH


def normalize_title(title: str) -> str:
    return str(title).strip().lower()


class MovieRecommender:
    def __init__(self) -> None:
        self.df: pd.DataFrame | None = None
        self.indices: Any = None
        self.tfidf_matrix: Any = None
        self.tfidf: Any = None
        self.title_to_idx: dict[str, int] = {}

    def load(self) -> None:
        self.df = joblib.load(DF_PATH)
        self.indices = joblib.load(INDICES_PATH)
        self.tfidf_matrix = joblib.load(TFIDF_MATRIX_PATH)
        self.tfidf = joblib.load(TFIDF_PATH)
        self.title_to_idx = self._build_title_to_idx_map(self.indices)

        if "title" not in self.df.columns:
            raise RuntimeError("df_model.pkl must contain a DataFrame with a 'title' column")

    def is_loaded(self) -> bool:
        return (
            self.df is not None
            and self.tfidf_matrix is not None
            and bool(self.title_to_idx)
        )

    def get_titles(self) -> list[str]:
        self._require_loaded()
        return self.df["title"].dropna().sort_values().tolist()

    def get_local_idx_by_title(self, title: str) -> int:
        self._require_loaded()
        key = normalize_title(title)

        if key not in self.title_to_idx:
            raise KeyError(f"Title not found in local dataset: '{title}'")

        return int(self.title_to_idx[key])

    def recommend_titles(self, query_title: str, top_n: int = 10) -> list[tuple[str, float]]:
        self._require_loaded()
        idx = self.get_local_idx_by_title(query_title)

        query_vector = self.tfidf_matrix[idx]
        scores = (self.tfidf_matrix @ query_vector.T).toarray().ravel()
        order = np.argsort(-scores)

        recommendations: list[tuple[str, float]] = []
        for row_idx in order:
            row_idx = int(row_idx)

            if row_idx == idx:
                continue

            try:
                title = str(self.df.iloc[row_idx]["title"])
            except Exception:
                continue

            recommendations.append((title, float(scores[row_idx])))

            if len(recommendations) >= top_n:
                break

        return recommendations

    def _require_loaded(self) -> None:
        if not self.is_loaded():
            raise RuntimeError("Movie recommender resources are not loaded")

    @staticmethod
    def _build_title_to_idx_map(indices: Any) -> dict[str, int]:
        try:
            return {normalize_title(title): int(index) for title, index in indices.items()}
        except AttributeError as error:
            raise RuntimeError(
                "indices.pkl must be dict-like or pandas Series-like with .items()"
            ) from error


recommender = MovieRecommender()
