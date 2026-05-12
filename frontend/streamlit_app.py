import streamlit as st
import requests
from typing import Optional

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
API_BASE = "http://localhost:8000"   
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"

st.set_page_config(
    page_title="🎬 CineMatch",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# GLOBAL STYLES
# ─────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Sans:wght@300;400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
        background-color: #0d0d0f;
        color: #e8e4dc;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #111115;
        border-right: 1px solid #1f1f28;
    }
    section[data-testid="stSidebar"] * { color: #e8e4dc !important; }

    /* Page title */
    .cinematic-title {
        font-family: 'Playfair Display', serif;
        font-size: 3.2rem;
        font-weight: 900;
        letter-spacing: -1px;
        background: linear-gradient(120deg, #f5c842 0%, #e8834a 60%, #c94040 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
        line-height: 1.1;
    }
    .cinematic-sub {
        color: #7a7a8a;
        font-size: 0.95rem;
        font-weight: 300;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-top: 4px;
        margin-bottom: 24px;
    }

    /* Section headers */
    .section-label {
        font-family: 'DM Sans', sans-serif;
        font-size: 0.72rem;
        font-weight: 500;
        letter-spacing: 3px;
        text-transform: uppercase;
        color: #f5c842;
        margin-bottom: 12px;
        padding-bottom: 6px;
        border-bottom: 1px solid #1f1f28;
    }

    /* Movie card */
    .movie-card {
        background: #141418;
        border: 1px solid #1f1f28;
        border-radius: 10px;
        overflow: hidden;
        transition: transform 0.2s ease, border-color 0.2s ease;
        height: 100%;
    }
    .movie-card:hover {
        transform: translateY(-4px);
        border-color: #f5c842;
    }
    .movie-card img {
        width: 100%;
        object-fit: cover;
        display: block;
    }
    .card-body {
        padding: 10px 12px 14px;
    }
    .card-title {
        font-family: 'Playfair Display', serif;
        font-size: 0.92rem;
        font-weight: 700;
        color: #e8e4dc;
        margin: 0 0 4px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .card-meta {
        font-size: 0.75rem;
        color: #7a7a8a;
    }
    .card-rating {
        display: inline-block;
        background: #1c1c22;
        border: 1px solid #f5c842;
        color: #f5c842;
        border-radius: 4px;
        padding: 1px 6px;
        font-size: 0.7rem;
        font-weight: 500;
        margin-right: 6px;
    }
    .score-badge {
        display: inline-block;
        background: #1a1a10;
        border: 1px solid #e8834a;
        color: #e8834a;
        border-radius: 4px;
        padding: 1px 6px;
        font-size: 0.7rem;
        font-weight: 500;
    }

    /* Detail panel */
    .detail-title {
        font-family: 'Playfair Display', serif;
        font-size: 2.2rem;
        font-weight: 900;
        color: #e8e4dc;
        line-height: 1.15;
        margin-bottom: 6px;
    }
    .genre-tag {
        display: inline-block;
        background: #1c1c22;
        border: 1px solid #333340;
        border-radius: 20px;
        padding: 3px 12px;
        font-size: 0.72rem;
        color: #a0a0b8;
        margin: 2px 3px;
        font-weight: 400;
    }
    .overview-text {
        font-size: 0.92rem;
        line-height: 1.7;
        color: #b0aaa0;
        margin-top: 12px;
    }

    /* Search bar tweak */
    div[data-testid="stTextInput"] input {
        background: #141418 !important;
        border: 1px solid #2a2a35 !important;
        color: #e8e4dc !important;
        border-radius: 8px !important;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: #f5c842 !important;
        box-shadow: 0 0 0 2px rgba(245,200,66,0.15) !important;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #f5c842, #e8834a) !important;
        color: #0d0d0f !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 8px 20px !important;
        font-family: 'DM Sans', sans-serif !important;
        letter-spacing: 0.5px;
    }
    .stButton > button:hover {
        opacity: 0.88;
        transform: translateY(-1px);
    }

    /* Divider */
    hr { border-color: #1f1f28; }

    /* Selectbox */
    div[data-testid="stSelectbox"] select,
    div[data-baseweb="select"] {
        background: #141418 !important;
        color: #e8e4dc !important;
        border-color: #2a2a35 !important;
    }

    /* Hide default Streamlit header decoration */
    header[data-testid="stHeader"] { background: transparent; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def api(path: str, params: dict = None):
    try:
        r = requests.get(f"{API_BASE}{path}", params=params, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"API error: {e}")
        return None


def poster_url(path_or_url: Optional[str]) -> str:
    if path_or_url and path_or_url.startswith("http"):
        return path_or_url

    if path_or_url:
        return f"{TMDB_IMAGE_BASE}{path_or_url}"

    return "https://via.placeholder.com/300x450/141418/7a7a8a?text=No+Image"


def render_movie_card(card: dict, score: Optional[float] = None):
    """Render one movie card as HTML."""
    title = card.get("title", "Unknown")
    poster = poster_url(card.get("poster_url") or card.get("poster_path"))
    rating = card.get("vote_average", 0)
    year = (card.get("release_date") or "")[:4]
    rating_html = f'<span class="card-rating">★ {rating:.1f}</span>' if rating else ""
    score_html = f'<span class="score-badge">sim {score:.2f}</span>' if score is not None else ""
    year_html = f'<span class="card-meta">{year}</span>' if year else ""

    return f"""
    <div class="movie-card">
        <img src="{poster}" alt="{title}" style="height:240px;" />
        <div class="card-body">
            <div class="card-title" title="{title}">{title}</div>
            <div style="margin-top:5px;">{rating_html}{score_html}{year_html}</div>
        </div>
    </div>
    """


def render_grid(items: list, score_key: bool = False, cols: int = 6):
    """Render a responsive card grid."""
    columns = st.columns(cols)
    for i, item in enumerate(items):
        card = item.get("tmdb") or item
        score = item.get("score") if score_key else None
        with columns[i % cols]:
            st.markdown(render_movie_card(card, score), unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="cinematic-title" style="font-size:1.8rem;">🎬 CineMatch</div>', unsafe_allow_html=True)
    st.markdown('<div class="cinematic-sub" style="font-size:0.7rem;">AI · Movie · Discovery</div>', unsafe_allow_html=True)
    st.markdown("---")

    page = st.radio(
        "Navigate",
        ["🏠 Home", "🔍 Search & Recommend", "🎭 Genre Picks", "📋 Browse Titles"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown('<div class="section-label">API Status</div>', unsafe_allow_html=True)
    health = api("/health")
    if health:
        loaded = health.get("recommender_loaded", False)
        status = "🟢 Recommender ready" if loaded else "🟡 Recommender loading…"
        st.caption(status)
    else:
        st.caption("🔴 API unreachable")

    st.markdown("---")
    st.caption("Powered by TMDB + TF-IDF")


# ─────────────────────────────────────────────
# PAGE: HOME
# ─────────────────────────────────────────────
if page == "🏠 Home":
    st.markdown('<div class="cinematic-title">Discover Cinema</div>', unsafe_allow_html=True)
    st.markdown('<div class="cinematic-sub">Curated picks for every mood</div>', unsafe_allow_html=True)

    category = st.selectbox(
        "Browse by",
        ["popular", "top_rated", "trending", "upcoming", "now_playing"],
        format_func=lambda x: x.replace("_", " ").title(),
    )

    data = api("/home", {"category": category, "limit": 24})
    if data:
        st.markdown(f'<div class="section-label">{category.replace("_", " ").upper()}</div>', unsafe_allow_html=True)
        render_grid(data, cols=6)


# ─────────────────────────────────────────────
# PAGE: SEARCH & RECOMMEND
# ─────────────────────────────────────────────
elif page == "🔍 Search & Recommend":
    st.markdown('<div class="cinematic-title">Search & Discover</div>', unsafe_allow_html=True)
    st.markdown('<div class="cinematic-sub">Find similar films instantly</div>', unsafe_allow_html=True)

    col_input, col_btn = st.columns([5, 1])
    with col_input:
        query = st.text_input("", placeholder="e.g. Inception, The Dark Knight, Parasite…", label_visibility="collapsed")
    with col_btn:
        st.markdown("<div style='margin-top:4px;'>", unsafe_allow_html=True)
        search = st.button("Search")
        st.markdown("</div>", unsafe_allow_html=True)

    if search and query:
        with st.spinner("Analysing…"):
            bundle = api("/movie/search", {"query": query, "tfidf_top_n": 12, "genre_limit": 12})

        if bundle:
            details = bundle.get("movie_details", {})
            poster = details.get("poster_url") or details.get("poster_path")
            title = details.get("title", "Unknown")
            overview = details.get("overview", "")
            release = (details.get("release_date") or "")[:4]
            rating = details.get("vote_average", 0)
            runtime = details.get("runtime")
            genres = details.get("genres", [])

            # ── Movie detail panel ──────────────────────────
            st.markdown("---")
            d_col1, d_col2 = st.columns([1, 3])
            with d_col1:
                st.image(poster_url(poster), use_container_width=True)
            with d_col2:
                st.markdown(f'<div class="detail-title">{title}</div>', unsafe_allow_html=True)
                meta_parts = []
                if release:
                    meta_parts.append(release)
                if runtime:
                    meta_parts.append(f"{runtime} min")
                if rating:
                    meta_parts.append(f"★ {rating:.1f}")
                st.markdown(f'<div class="card-meta">{" · ".join(meta_parts)}</div>', unsafe_allow_html=True)
                genre_tags = " ".join(f'<span class="genre-tag">{g["name"]}</span>' for g in genres)
                st.markdown(f'<div style="margin-top:10px;">{genre_tags}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="overview-text">{overview}</div>', unsafe_allow_html=True)

            # ── TF-IDF recommendations ──────────────────────
            tfidf = bundle.get("tfidf_recommendations", [])
            if tfidf:
                st.markdown("---")
                st.markdown('<div class="section-label">AI Similarity Picks · TF-IDF</div>', unsafe_allow_html=True)
                render_grid(tfidf, score_key=True, cols=6)

            # ── Genre recommendations ───────────────────────
            genre_recs = bundle.get("genre_recommendations", [])
            if genre_recs:
                st.markdown("---")
                st.markdown('<div class="section-label">More in This Genre</div>', unsafe_allow_html=True)
                render_grid(genre_recs, cols=6)


# ─────────────────────────────────────────────
# PAGE: GENRE PICKS
# ─────────────────────────────────────────────
elif page == "🎭 Genre Picks":
    st.markdown('<div class="cinematic-title">Genre Picks</div>', unsafe_allow_html=True)
    st.markdown('<div class="cinematic-sub">Explore by TMDB movie ID</div>', unsafe_allow_html=True)

    tmdb_id = st.number_input("Enter a TMDB Movie ID", min_value=1, value=550, step=1)
    limit = st.slider("Number of recommendations", 6, 30, 18, step=6)

    if st.button("Get Genre Recommendations"):
        with st.spinner("Fetching…"):
            recs = api("/recommend/genre", {"tmdb_id": tmdb_id, "limit": limit})
            movie = api(f"/movie/id/{tmdb_id}")

        if movie:
            st.markdown("---")
            st.markdown(
                f'<div class="detail-title" style="font-size:1.4rem;">'
                f'Because you like: {movie.get("title","")}'
                f'</div>',
                unsafe_allow_html=True,
            )

        if recs:
            st.markdown('<div class="section-label">Recommended · Same Genre</div>', unsafe_allow_html=True)
            render_grid(recs, cols=6)
        else:
            st.info("No genre recommendations found.")


# ─────────────────────────────────────────────
# PAGE: BROWSE TITLES
# ─────────────────────────────────────────────
elif page == "📋 Browse Titles":
    st.markdown('<div class="cinematic-title">All Titles</div>', unsafe_allow_html=True)
    st.markdown('<div class="cinematic-sub">Every movie in the recommender dataset</div>', unsafe_allow_html=True)

    data = api("/movies")
    if data:
        titles: list = data.get("movies", [])
        st.caption(f"{len(titles):,} titles loaded")

        search_term = st.text_input("Filter titles", placeholder="Start typing…")
        filtered = [t for t in titles if search_term.lower() in t.lower()] if search_term else titles

        # Show as paginated list
        PAGE_SIZE = 100
        total_pages = max(1, (len(filtered) - 1) // PAGE_SIZE + 1)
        page_num = st.number_input("Page", min_value=1, max_value=total_pages, value=1, step=1) if total_pages > 1 else 1
        start = (page_num - 1) * PAGE_SIZE
        page_titles = filtered[start : start + PAGE_SIZE]

        cols = st.columns(4)
        for i, t in enumerate(page_titles):
            cols[i % 4].markdown(
                f'<div style="padding:5px 0; font-size:0.82rem; color:#b0aaa0; '
                f'border-bottom:1px solid #1a1a22;">{t}</div>',
                unsafe_allow_html=True,
            )

        if total_pages > 1:
            st.caption(f"Showing {start+1}–{min(start+PAGE_SIZE, len(filtered))} of {len(filtered)}")
    else:
        st.info("Could not load titles from the API.")
