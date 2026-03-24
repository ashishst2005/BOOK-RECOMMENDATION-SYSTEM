"""
app.py  (v2 — Enhanced Edition)
--------------------------------
Smart Book Recommendation System — Streamlit Frontend

New features added in v2:
  1.  Ratings & fake-review-count display
  2.  Richer card layout (cover initial, meta grid, badges)
  3.  Autocomplete (selectbox) search for Book Title
  4.  Visible Similarity Score bar
  5.  Top-N control  (5 / 10 / 15)
  6.  Smart "No Results" with genre suggestions
  7.  Short description + "Read More" expander
  8.  Dark Mode toggle (sidebar)
  9.  Save Recommendations as CSV download
  10. Recommendation History (session state sidebar)
"""

import io
import hashlib
import random
import streamlit as st
import pandas as pd

from data_loader import load_dataset
from recommender import recommend_by_genre_author, recommend_by_title

# ───────────────────────────────────────────────────────────────────────────
# Page config
# ───────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="📚 Smart Book Recommender",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ───────────────────────────────────────────────────────────────────────────
# Session-state initialisation
# ───────────────────────────────────────────────────────────────────────────
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False
if "history" not in st.session_state:
    st.session_state.history = []          # list of dicts: {query, type, results_df}
if "desc_expanded" not in st.session_state:
    st.session_state.desc_expanded = {}    # book-hash → bool

dark = st.session_state.dark_mode

# ───────────────────────────────────────────────────────────────────────────
# Colour palette (light / dark)
# ───────────────────────────────────────────────────────────────────────────
if dark:
    BG_GRAD   = "linear-gradient(-45deg, #0f172a, #1e1b4b, #1e293b, #0c1a2e)"
    CARD_BG   = "rgba(30,27,75,0.85)"
    CARD_BDR  = "#312e81"
    TITLE_CLR = "#c7d2fe"
    HDR_CLR   = "#818cf8"
    BODY_CLR  = "#cbd5e1"
    INFO_BG   = "rgba(49,46,129,0.5)"
    INFO_BDR  = "#4338ca"
    INFO_CLR  = "#a5b4fc"
    NR_BG     = "rgba(30,27,75,0.6)"
    NR_CLR    = "#94a3b8"
    BANNER_BG = "linear-gradient(135deg,#3730a3 0%,#5b21b6 100%)"
    SRC_BG    = "rgba(30,27,75,0.9)"
    SRC_BDR   = "#4338ca"
    INPUT_BG  = "#1e293b"
    INPUT_CLR = "#e2e8f0"
    INPUT_BDR = "#4338ca"
    SUB_CLR   = "#64748b"
    TAB_BG    = "rgba(30,27,75,0.55)"
    TAB_ACT   = "#1e1b4b"
    HISTORY_BG= "rgba(30,27,75,0.7)"
else:
    BG_GRAD   = "linear-gradient(-45deg,#e3f2fd,#e8eaf6,#ede7f6,#e1f5fe)"
    CARD_BG   = "rgba(255,255,255,0.85)"
    CARD_BDR  = "#e0e7ff"
    TITLE_CLR = "#1e3a8a"
    HDR_CLR   = "#1d4ed8"
    BODY_CLR  = "#334155"
    INFO_BG   = "rgba(224,231,255,0.6)"
    INFO_BDR  = "#c7d2fe"
    INFO_CLR  = "#3730a3"
    NR_BG     = "rgba(255,255,255,0.7)"
    NR_CLR    = "#64748b"
    BANNER_BG = "linear-gradient(135deg,#4f46e5 0%,#7c3aed 100%)"
    SRC_BG    = "rgba(238,242,255,0.9)"
    SRC_BDR   = "#a5b4fc"
    INPUT_BG  = "#ffffff"
    INPUT_CLR = "#334155"
    INPUT_BDR = "#cbd5e1"
    SUB_CLR   = "#475569"
    TAB_BG    = "rgba(255,255,255,0.55)"
    TAB_ACT   = "#ffffff"
    HISTORY_BG= "rgba(255,255,255,0.7)"

# ───────────────────────────────────────────────────────────────────────────
# CSS injection
# ───────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

@keyframes gradientMove {{
    0%   {{background-position:0% 50%;}}
    50%  {{background-position:100% 50%;}}
    100% {{background-position:0% 50%;}}
}}

html,body,[data-testid="stAppViewContainer"] {{
    font-family:'Inter',sans-serif;
    background:{BG_GRAD};
    background-size:400% 400%;
    animation:gradientMove 12s ease infinite;
    min-height:100vh;
}}
[data-testid="stHeader"]{{background:transparent!important;}}

.block-container{{max-width:1100px;padding-top:1.5rem;padding-bottom:3rem;}}

/* ── Sidebar ── */
[data-testid="stSidebar"]{{
    background:{"rgba(15,23,42,0.92)" if dark else "rgba(255,255,255,0.88)"}!important;
    border-right:1.5px solid {CARD_BDR};
}}
[data-testid="stSidebar"] * {{color:{BODY_CLR}!important;}}

/* ── Title ── */
.main-title{{
    text-align:center;font-size:2.8rem;font-weight:700;
    color:{TITLE_CLR};letter-spacing:-0.5px;
    margin-bottom:0.2rem;text-shadow:0 2px 8px rgba(30,58,138,.10);
}}
.subtitle{{
    text-align:center;font-size:1.05rem;color:{SUB_CLR};
    margin-bottom:2rem;font-weight:400;
}}

/* ── Section headers ── */
.section-header{{
    font-size:1.2rem;font-weight:600;color:{HDR_CLR};
    margin-bottom:0.9rem;border-left:4px solid #6366f1;padding-left:.75rem;
}}

/* ── Inputs (text) ── */
label,[data-testid="stTextInput"] label{{color:{BODY_CLR}!important;font-weight:500;font-size:.95rem;}}
.stTextInput>div>div>input{{
    background-color:{INPUT_BG}!important;color:{INPUT_CLR}!important;
    border:1.5px solid {INPUT_BDR}!important;border-radius:10px!important;
    padding:0.6rem 1rem!important;font-size:.97rem;transition:border-color .2s;
}}
.stTextInput>div>div>input:focus{{
    border-color:#6366f1!important;
    box-shadow:0 0 0 3px rgba(99,102,241,.15)!important;
    outline:none!important;
}}

/* ── Selectbox ── */
[data-testid="stSelectbox"] label{{color:{BODY_CLR}!important;font-weight:500;font-size:.95rem;}}
[data-testid="stSelectbox"] div[data-baseweb="select"] > div{{
    background:{INPUT_BG}!important;color:{INPUT_CLR}!important;
    border:1.5px solid {INPUT_BDR}!important;border-radius:10px!important;
}}

/* ── Buttons ── */
.stButton>button{{
    background:linear-gradient(135deg,#4f46e5,#6366f1)!important;
    color:#e0e7ff!important;border:none!important;border-radius:10px!important;
    padding:.65rem 2rem!important;font-size:1rem!important;font-weight:600!important;
    cursor:pointer!important;transition:all .25s ease!important;
    box-shadow:0 4px 14px rgba(79,70,229,.3)!important;letter-spacing:0.3px;
}}
.stButton>button:hover{{
    transform:translateY(-2px)!important;
    box-shadow:0 6px 20px rgba(79,70,229,.45)!important;
    background:linear-gradient(135deg,#4338ca,#4f46e5)!important;
}}
.stButton>button:active{{transform:translateY(0px)!important;}}

/* ── Tabs ── */
[data-baseweb="tab-list"]{{
    gap:.5rem;background-color:transparent!important;
    border-bottom:2px solid #c7d2fe;padding-bottom:0;
}}
[data-baseweb="tab"]{{
    background-color:{TAB_BG}!important;border-radius:10px 10px 0 0!important;
    border:1.5px solid #c7d2fe!important;border-bottom:none!important;
    color:{SUB_CLR}!important;font-weight:500!important;
    padding:.55rem 1.4rem!important;transition:all .2s;
}}
[aria-selected="true"][data-baseweb="tab"]{{
    background-color:{TAB_ACT}!important;color:#4f46e5!important;
    font-weight:700!important;border-color:#6366f1!important;
    border-bottom:2px solid {TAB_ACT}!important;
}}

/* ── Cards ── */
.book-card{{
    background:{CARD_BG};border:1.5px solid {CARD_BDR};
    border-radius:14px;padding:1.1rem 1.4rem 1rem;margin-bottom:1rem;
    box-shadow:0 2px 12px rgba(99,102,241,.08);
    transition:box-shadow .2s,transform .2s;
}}
.book-card:hover{{
    box-shadow:0 6px 24px rgba(99,102,241,.18);
    transform:translateY(-2px);
}}

.book-cover{{
    width:52px;height:72px;border-radius:8px;
    background:linear-gradient(135deg,#6366f1,#7c3aed);
    display:flex;align-items:center;justify-content:center;
    font-size:1.5rem;font-weight:700;color:#fff;
    flex-shrink:0;box-shadow:0 2px 8px rgba(99,102,241,.3);
}}
.card-grid{{display:flex;gap:1rem;align-items:flex-start;}}
.card-body{{flex:1;min-width:0;}}

.book-title{{font-size:1.1rem;font-weight:700;color:{TITLE_CLR};margin-bottom:.2rem;}}
.book-meta{{font-size:.87rem;color:{BODY_CLR};margin-bottom:.45rem;opacity:.9;}}
.book-desc-short{{font-size:.88rem;color:{BODY_CLR};line-height:1.5;margin-top:.4rem;}}

/* ── Badges ── */
.rating-badge{{
    display:inline-block;
    background:linear-gradient(135deg,#fbbf24,#f59e0b);
    color:#fff;font-size:.78rem;font-weight:700;
    border-radius:20px;padding:.14rem .6rem;margin-right:.4rem;
}}
.reviews-badge{{
    display:inline-block;background:#f0fdf4;color:#166534;
    font-size:.78rem;font-weight:600;border-radius:20px;
    padding:.14rem .6rem;margin-right:.4rem;
    border:1px solid #bbf7d0;
}}
.genre-badge{{
    display:inline-block;background:#ede9fe;color:#5b21b6;
    font-size:.78rem;font-weight:600;border-radius:20px;
    padding:.14rem .6rem;margin-right:.4rem;
}}
.score-badge{{
    display:inline-block;
    background:linear-gradient(135deg,#6366f1,#818cf8);
    color:#fff;font-size:.78rem;font-weight:700;
    border-radius:20px;padding:.14rem .6rem;
}}

/* ── Score bar wrapper ── */
.score-bar-wrap{{margin-top:.35rem;}}
.score-bar-bg{{
    background:{"#1e293b" if dark else "#e0e7ff"};
    border-radius:99px;height:6px;overflow:hidden;
}}
.score-bar-fill{{
    height:6px;border-radius:99px;
    background:linear-gradient(90deg,#6366f1,#7c3aed);
    transition:width .6s ease;
}}
.score-label{{
    font-size:.75rem;color:{HDR_CLR};font-weight:600;margin-bottom:.15rem;
}}

/* ── Top banner ── */
.top-rec-banner{{
    background:{BANNER_BG};border-radius:16px;
    padding:1.6rem 2rem;margin-bottom:1.5rem;
    box-shadow:0 4px 20px rgba(79,70,229,.25);
}}
.top-rec-label{{
    font-size:.75rem;font-weight:600;letter-spacing:1px;
    text-transform:uppercase;color:#c7d2fe;margin-bottom:.4rem;
}}
.top-rec-title{{font-size:1.5rem;font-weight:700;color:#ffffff;margin-bottom:.25rem;}}
.top-rec-meta{{font-size:.88rem;color:#c7d2fe;margin-bottom:.65rem;line-height:1.6;}}
.top-rec-desc{{font-size:.9rem;color:#e0e7ff;line-height:1.55;}}

/* ── Info box ── */
.info-box{{
    background:{INFO_BG};border:1.5px solid {INFO_BDR};
    border-radius:10px;padding:.75rem 1.1rem;
    color:{INFO_CLR};font-size:.9rem;margin-bottom:1.3rem;
}}

/* ── No results ── */
.no-results{{
    text-align:center;padding:2rem;
    background:{NR_BG};border-radius:14px;
    color:{NR_CLR};font-size:1rem;
}}
.no-results ul{{list-style:none;padding:0;margin:.75rem 0 0;}}
.no-results li{{
    display:inline-block;margin:.25rem;
    background:{"rgba(99,102,241,.2)" if dark else "#e0e7ff"};
    color:{"#a5b4fc" if dark else "#4338ca"};
    border-radius:20px;padding:.25rem .9rem;font-size:.88rem;
    font-weight:600;cursor:default;
}}

/* ── History item ── */
.hist-item{{
    background:{HISTORY_BG};border:1px solid {CARD_BDR};
    border-radius:10px;padding:.5rem .75rem;
    font-size:.84rem;color:{BODY_CLR};margin-bottom:.5rem;
}}

/* ── Slider label ── */
[data-testid="stSlider"] label{{color:{BODY_CLR}!important;font-weight:500;}}

/* ── Download button ── */
[data-testid="stDownloadButton"]>button{{
    background:linear-gradient(135deg,#059669,#10b981)!important;
    color:#ecfdf5!important;border-radius:10px!important;
    border:none!important;font-weight:600!important;
    box-shadow:0 4px 12px rgba(5,150,105,.3)!important;
}}

</style>
""", unsafe_allow_html=True)


# ───────────────────────────────────────────────────────────────────────────
# Dataset (cached)
# ───────────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def get_data() -> pd.DataFrame:
    return load_dataset()

with st.spinner("📚 Loading book dataset…"):
    df = get_data()

# Pre-build sorted title list for autocomplete
ALL_TITLES: list[str] = sorted(df["Title"].dropna().unique().tolist())


# ───────────────────────────────────────────────────────────────────────────
# Utilities
# ───────────────────────────────────────────────────────────────────────────

def _book_hash(title: str) -> str:
    return hashlib.md5(title.encode()).hexdigest()[:8]


def _fake_reviews(rating: float) -> int:
    """Generate a deterministic plausible review count from rating (for demo)."""
    seed = int(rating * 100) if isinstance(rating, float) else 400
    rng = random.Random(seed)
    return rng.randint(1_000, 50_000)


def _cover_initial(title: str) -> str:
    return title[0].upper() if title else "📚"


def _score_bar(score: float, label: str = "Similarity Score") -> str:
    pct = int(score * 100)
    return f"""
    <div class="score-bar-wrap">
        <div class="score-label">{label}: {pct}%</div>
        <div class="score-bar-bg">
            <div class="score-bar-fill" style="width:{pct}%"></div>
        </div>
    </div>"""


# ───────────────────────────────────────────────────────────────────────────
# Render helpers
# ───────────────────────────────────────────────────────────────────────────

def render_top_book(book: dict) -> None:
    """Highlighted banner for the #1 recommendation."""
    rating = book.get("Rating", None)
    reviews = _fake_reviews(rating) if isinstance(rating, (int, float)) else 0
    rating_str = f"{rating:.2f} ⭐  |  📝 {reviews:,} reviews" if isinstance(rating, (int, float)) else "N/A"
    score = book.get("Score", 0)
    pct = int(score * 100)
    desc = book.get("Description", "No description available.")
    st.markdown(f"""
    <div class="top-rec-banner">
        <div class="top-rec-label">🏆 Top Recommendation</div>
        <div class="top-rec-title">{book.get('Title','Unknown Title')}</div>
        <div class="top-rec-meta">
            ✍️ {book.get('Author','Unknown')} &nbsp;|&nbsp;
            📖 {book.get('Genre','—')} &nbsp;|&nbsp;
            {rating_str}
        </div>
        <div style="margin-bottom:.65rem;">
            <div class="score-label">Similarity Score: {pct}%</div>
            <div class="score-bar-bg" style="max-width:320px;">
                <div class="score-bar-fill" style="width:{pct}%"></div>
            </div>
        </div>
        <div class="top-rec-desc">{desc[:280]}{"…" if len(desc)>280 else ""}</div>
    </div>
    """, unsafe_allow_html=True)


def render_book_card(book: dict, idx: int = 0, show_score: bool = True) -> None:
    """Rich card with cover initial, score bar, and Read More expander."""
    title   = book.get("Title", "Unknown Title")
    author  = book.get("Author", "Unknown Author")
    genre   = book.get("Genre", "")
    rating  = book.get("Rating", None)
    score   = book.get("Score", 0)
    desc    = book.get("Description", "No description available.")
    initial = _cover_initial(title)
    bh      = _book_hash(title)

    reviews    = _fake_reviews(rating) if isinstance(rating, (int, float)) else 0
    rating_html  = f'<span class="rating-badge">⭐ {rating:.2f}</span>' if isinstance(rating, (int, float)) else ""
    reviews_html = f'<span class="reviews-badge">📝 {reviews:,} reviews</span>' if reviews else ""
    genre_html   = f'<span class="genre-badge">📖 {genre}</span>' if genre else ""
    score_html   = f'<span class="score-badge">🎯 {int(score*100)}%</span>' if show_score else ""
    bar_html     = _score_bar(score) if show_score else ""

    short_desc   = desc[:150] + ("…" if len(desc) > 150 else "")

    st.markdown(f"""
    <div class="book-card">
        <div class="card-grid">
            <div class="book-cover">{initial}</div>
            <div class="card-body">
                <div class="book-title">{title}</div>
                <div class="book-meta">✍️ {author}</div>
                <div style="margin-bottom:.4rem">{rating_html}{reviews_html}{genre_html}{score_html}</div>
                {bar_html}
                <div class="book-desc-short">{short_desc}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Read More expander (avoids clutter)
    if len(desc) > 150:
        with st.expander("📖 Read More", expanded=False):
            st.markdown(f'<span style="color:{BODY_CLR};font-size:.9rem;line-height:1.6">{desc}</span>',
                        unsafe_allow_html=True)


def render_source_card(book: dict) -> None:
    """Source/matched book card."""
    title   = book.get("Title", "Unknown Title")
    author  = book.get("Author", "Unknown Author")
    genre   = book.get("Genre", "")
    rating  = book.get("Rating", None)
    desc    = book.get("Description", "No description available.")
    initial = _cover_initial(title)
    reviews = _fake_reviews(rating) if isinstance(rating, (int, float)) else 0

    rating_html  = f'<span class="rating-badge">⭐ {rating:.2f}</span>' if isinstance(rating, (int, float)) else ""
    reviews_html = f'<span class="reviews-badge">📝 {reviews:,} reviews</span>' if reviews else ""
    genre_html   = f'<span class="genre-badge">📖 {genre}</span>' if genre else ""

    st.markdown(f"""
    <div class="book-card" style="border-color:{SRC_BDR};background:{SRC_BG};">
        <div style="font-size:.72rem;font-weight:600;letter-spacing:1px;text-transform:uppercase;
                    color:#6366f1;margin-bottom:.35rem;">🔍 Matched Source Book</div>
        <div class="card-grid">
            <div class="book-cover" style="background:linear-gradient(135deg,#6366f1,#4338ca)">{initial}</div>
            <div class="card-body">
                <div class="book-title">{title}</div>
                <div class="book-meta">✍️ {author}</div>
                <div style="margin-bottom:.4rem">{rating_html}{reviews_html}{genre_html}</div>
                <div class="book-desc-short">{desc[:150]}{"…" if len(desc)>150 else ""}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if len(desc) > 150:
        with st.expander("📖 Read More", expanded=False):
            st.markdown(f'<span style="color:{BODY_CLR};font-size:.9rem;line-height:1.6">{desc}</span>',
                        unsafe_allow_html=True)


def render_no_results(query: str = "") -> None:
    popular_genres = ["Fantasy", "Fiction", "Science Fiction", "Mystery",
                      "Thriller", "Romance", "Horror", "Dystopian", "Non-Fiction"]
    pills = "".join(f"<li>{g}</li>" for g in popular_genres)
    msg = f'😔 No results for "<b>{query}</b>".' if query else "😔 No matching books found."
    st.markdown(f"""
    <div class="no-results">
        {msg}
        <br><span style="font-size:.88rem">Try one of these popular genres:</span>
        <ul>{pills}</ul>
    </div>
    """, unsafe_allow_html=True)


def df_to_csv_bytes(results_df: pd.DataFrame) -> bytes:
    buf = io.StringIO()
    results_df.to_csv(buf, index=False)
    return buf.getvalue().encode()


def add_to_history(query: str, qtype: str, results_df: pd.DataFrame) -> None:
    entry = {"query": query, "type": qtype, "results": results_df}
    # Avoid exact duplicate consecutive entries
    if st.session_state.history and st.session_state.history[-1]["query"] == query:
        return
    st.session_state.history.insert(0, entry)
    if len(st.session_state.history) > 10:
        st.session_state.history.pop()


# ───────────────────────────────────────────────────────────────────────────
# Sidebar — Dark Mode + History
# ───────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f'<div style="font-size:1.1rem;font-weight:700;color:{TITLE_CLR};margin-bottom:.5rem">⚙️ Controls</div>',
                unsafe_allow_html=True)

    # ── Dark Mode toggle ──
    toggled = st.toggle("🌙 Dark Mode", value=st.session_state.dark_mode, key="dm_toggle")
    if toggled != st.session_state.dark_mode:
        st.session_state.dark_mode = toggled
        st.rerun()

    st.markdown("---")

    # ── History ──
    st.markdown(f'<div style="font-size:1rem;font-weight:600;color:{HDR_CLR};margin-bottom:.5rem">🕑 Recent Searches</div>',
                unsafe_allow_html=True)

    if not st.session_state.history:
        st.markdown(f'<span style="font-size:.85rem;color:{SUB_CLR}">No searches yet.</span>',
                    unsafe_allow_html=True)
    else:
        for i, h in enumerate(st.session_state.history):
            icon = "🔍" if h["type"] == "genre_author" else "📖"
            st.markdown(f"""
            <div class="hist-item">
                {icon} <b>{h['query']}</b><br>
                <span style="font-size:.77rem;opacity:.7">{h['type'].replace('_',' ').title()} — {len(h['results'])} results</span>
            </div>""", unsafe_allow_html=True)

        if st.button("🗑 Clear History", key="clear_hist"):
            st.session_state.history = []
            st.rerun()


# ───────────────────────────────────────────────────────────────────────────
# Header
# ───────────────────────────────────────────────────────────────────────────
st.markdown(f'<div class="main-title">📚 Smart Book Recommendation System</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="subtitle">Powered by <b>Best-First Search</b> &amp; Heuristic AI &nbsp;·&nbsp; '
    f'Exploring <b>{len(df):,}</b> books</div>',
    unsafe_allow_html=True,
)

# ───────────────────────────────────────────────────────────────────────────
# Tabs
# ───────────────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["🔍  Recommend by Genre & Author", "📖  Recommend by Book Title"])


# ═══════════════════════════════════════════════════════════════════════════
# TAB 1 — Genre & Author
# ═══════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown(f'<div class="section-header">Search by Preferred Genre &amp; Favourite Author</div>',
                unsafe_allow_html=True)
    st.markdown(
        f'<div class="info-box">💡 Enter a genre (e.g. <i>Fantasy</i>, <i>Mystery</i>) and/or an author. '
        'Best-First Search with a weighted heuristic h(n) = 0.6×Genre + 0.4×Author will rank results.</div>',
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        genre_input = st.text_input("🎭 Preferred Genre",
                                    placeholder="e.g. Fantasy, Science Fiction…",
                                    key="genre_input")
    with col2:
        author_input = st.text_input("✍️ Favourite Author",
                                     placeholder="e.g. Rowling, Tolkien…",
                                     key="author_input")
    with col3:
        top_n_1 = st.select_slider("📊 Top N", options=[5, 10, 15], value=10, key="topn1")

    if st.button("🚀 Get Recommendations", key="btn_genre_author"):
        if not genre_input.strip() and not author_input.strip():
            st.warning("⚠️ Please enter at least a genre or an author name.")
        else:
            with st.spinner("🔍 Running Best-First Search…"):
                top_book, similar_df = recommend_by_genre_author(
                    df,
                    preferred_genre=genre_input,
                    preferred_author=author_input,
                    top_n=top_n_1,
                )

            if top_book is None:
                render_no_results(f"{genre_input} / {author_input}".strip(" /"))
            else:
                render_top_book(top_book)

                all_results = pd.DataFrame([top_book])
                if not similar_df.empty:
                    st.markdown(f'<div class="section-header" style="margin-top:1.3rem">📋 Similar Books You Might Enjoy</div>',
                                unsafe_allow_html=True)
                    for i, (_, row) in enumerate(similar_df.iterrows()):
                        render_book_card(row.to_dict(), idx=i)
                    all_results = pd.concat([all_results, similar_df], ignore_index=True)

                # Save button
                query_label = f"Genre:{genre_input} Author:{author_input}".strip()
                add_to_history(query_label, "genre_author", all_results)
                st.download_button(
                    label="💾 Save Recommendations as CSV",
                    data=df_to_csv_bytes(all_results),
                    file_name="book_recommendations.csv",
                    mime="text/csv",
                    key="dl1",
                )


# ═══════════════════════════════════════════════════════════════════════════
# TAB 2 — Book Title (with Autocomplete)
# ═══════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown(f'<div class="section-header">Search by Book Title</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="info-box">📖 Start typing a book title — the autocomplete will suggest matches '
        'from the dataset. The system extracts its genre &amp; author to drive Best-First Search.</div>',
        unsafe_allow_html=True,
    )

    col_t, col_n = st.columns([3, 1])
    with col_t:
        # Free-text filter → selectbox autocomplete
        title_filter = st.text_input("🔎 Filter titles…", placeholder="Type to search…", key="title_filter")
        if title_filter.strip():
            filtered_titles = [t for t in ALL_TITLES
                               if title_filter.strip().lower() in t.lower()][:60]
        else:
            filtered_titles = ALL_TITLES[:60]

        if not filtered_titles:
            st.warning("No matching titles — try a different keyword.")
            title_selected = ""
        else:
            title_selected = st.selectbox("📕 Select Book Title", options=filtered_titles,
                                          key="title_select")

    with col_n:
        top_n_2 = st.select_slider("📊 Top N", options=[5, 10, 15], value=10, key="topn2")

    if st.button("🚀 Find Similar Books", key="btn_title"):
        if not title_selected:
            st.warning("⚠️ Please select a book title.")
        else:
            with st.spinner("🔍 Searching and running Best-First Search…"):
                found_book, top_book, similar_df = recommend_by_title(
                    df,
                    title_query=title_selected,
                    top_n=top_n_2,
                )

            if found_book is None:
                render_no_results(title_selected)
            else:
                render_source_card(found_book)

                st.markdown(
                    f'<div class="info-box" style="margin-top:.4rem">🧠 Extracted — '
                    f'<b>Genre:</b> {found_book.get("Genre","—")} &nbsp;|&nbsp; '
                    f'<b>Author:</b> {found_book.get("Author","—")}<br>'
                    f'Using these as heuristic inputs for Best-First Search…</div>',
                    unsafe_allow_html=True,
                )

                if top_book is None and similar_df.empty:
                    render_no_results()
                else:
                    all_results = pd.DataFrame()
                    if top_book:
                        render_top_book(top_book)
                        all_results = pd.DataFrame([top_book])

                    if not similar_df.empty:
                        st.markdown(f'<div class="section-header" style="margin-top:1.3rem">📋 More Books You Might Enjoy</div>',
                                    unsafe_allow_html=True)
                        for i, (_, row) in enumerate(similar_df.iterrows()):
                            render_book_card(row.to_dict(), idx=i)
                        all_results = pd.concat([all_results, similar_df], ignore_index=True)

                    add_to_history(title_selected, "by_title", all_results)
                    if not all_results.empty:
                        st.download_button(
                            label="💾 Save Recommendations as CSV",
                            data=df_to_csv_bytes(all_results),
                            file_name="book_recommendations.csv",
                            mime="text/csv",
                            key="dl2",
                        )


# ───────────────────────────────────────────────────────────────────────────
# Footer
# ───────────────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown(f"""
<div style="text-align:center;color:{SUB_CLR};font-size:.82rem;padding:1rem 0;">
    📚 Smart Book Recommendation System &nbsp;·&nbsp;
    Best-First Search &nbsp;·&nbsp;
    h(n) = 0.6 × Genre + 0.4 × Author &nbsp;·&nbsp;
    Built with Python &amp; Streamlit
</div>
""", unsafe_allow_html=True)
