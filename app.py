"""
app.py  (v3 — Glassmorphism Edition)
-------------------------------------
Smart Book Recommendation System — Streamlit Frontend

Design: True black / white, glassmorphism, no emojis, minimalist premium.
"""

import io
import urllib.parse
import streamlit as st
import pandas as pd

from data_loader import load_dataset
from recommender import recommend_by_genre_author, recommend_by_title

# ──────────────────────────────────────────────────────────────────────────
# Page config
# ──────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Smart Book Recommender",
    page_icon="B",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────────────────
# Session state
# ──────────────────────────────────────────────────────────────────────────
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True      # default to dark for glass effect
if "history" not in st.session_state:
    st.session_state.history = []

dark = st.session_state.dark_mode

# ──────────────────────────────────────────────────────────────────────────
# Palette — true black / true white
# ──────────────────────────────────────────────────────────────────────────
if dark:
    BG_PRIMARY  = "#000000"
    GLASS       = "rgba(255,255,255,0.06)"
    GLASS_BDR   = "rgba(255,255,255,0.10)"
    TEXT_PRIMARY = "#ffffff"
    TEXT_SECOND  = "rgba(255,255,255,0.55)"
    TEXT_MUTED   = "rgba(255,255,255,0.35)"
    ACCENT       = "#ffffff"
    ACCENT_DIM   = "rgba(255,255,255,0.12)"
    BANNER_BG    = "rgba(255,255,255,0.08)"
    BANNER_BDR   = "rgba(255,255,255,0.15)"
    INPUT_BG     = "rgba(255,255,255,0.05)"
    INPUT_BDR    = "rgba(255,255,255,0.12)"
    DIVIDER      = "rgba(255,255,255,0.08)"
    SCORE_BAR_BG = "rgba(255,255,255,0.08)"
    SCORE_BAR_FG = "rgba(255,255,255,0.70)"
    SIDEBAR_BG   = "rgba(10,10,10,0.95)"
else:
    BG_PRIMARY  = "#ffffff"
    GLASS       = "rgba(0,0,0,0.03)"
    GLASS_BDR   = "rgba(0,0,0,0.06)"
    TEXT_PRIMARY = "#000000"
    TEXT_SECOND  = "rgba(0,0,0,0.55)"
    TEXT_MUTED   = "rgba(0,0,0,0.35)"
    ACCENT       = "#000000"
    ACCENT_DIM   = "rgba(0,0,0,0.06)"
    BANNER_BG    = "rgba(0,0,0,0.04)"
    BANNER_BDR   = "rgba(0,0,0,0.08)"
    INPUT_BG     = "rgba(0,0,0,0.02)"
    INPUT_BDR    = "rgba(0,0,0,0.10)"
    DIVIDER      = "rgba(0,0,0,0.06)"
    SCORE_BAR_BG = "rgba(0,0,0,0.06)"
    SCORE_BAR_FG = "rgba(0,0,0,0.65)"
    SIDEBAR_BG   = "rgba(250,250,250,0.97)"

# ──────────────────────────────────────────────────────────────────────────
# CSS — glassmorphism + animations
# ──────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Animations ── */
@keyframes fadeInUp {{
    from {{ opacity:0; transform:translateY(18px); }}
    to   {{ opacity:1; transform:translateY(0); }}
}}
@keyframes fadeIn {{
    from {{ opacity:0; }}
    to   {{ opacity:1; }}
}}
@keyframes slideDown {{
    from {{ opacity:0; transform:translateY(-8px); }}
    to   {{ opacity:1; transform:translateY(0); }}
}}

/* ── Base ── */
html, body, [data-testid="stAppViewContainer"] {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background: {BG_PRIMARY} !important;
    color: {TEXT_PRIMARY};
}}
[data-testid="stHeader"] {{ background: transparent !important; }}
.block-container {{ max-width:1000px; padding-top:2rem; padding-bottom:3rem; }}

/* ── Sidebar ── */
[data-testid="stSidebar"] {{
    background: {SIDEBAR_BG} !important;
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border-right: 1px solid {GLASS_BDR};
}}
[data-testid="stSidebar"] * {{ color: {TEXT_PRIMARY} !important; }}

/* ── Typography ── */
.main-title {{
    text-align: center;
    font-size: 2.4rem;
    font-weight: 700;
    color: {TEXT_PRIMARY};
    letter-spacing: -1px;
    margin-bottom: 0.15rem;
    animation: fadeInUp 0.6s ease;
}}
.subtitle {{
    text-align: center;
    font-size: 0.95rem;
    color: {TEXT_SECOND};
    margin-bottom: 2.5rem;
    font-weight: 400;
    letter-spacing: 0.2px;
    animation: fadeInUp 0.6s ease 0.1s both;
}}

/* ── Section headers ── */
.section-header {{
    font-size: 0.85rem;
    font-weight: 600;
    color: {TEXT_SECOND};
    letter-spacing: 0.8px;
    text-transform: uppercase;
    margin-bottom: 1rem;
    padding-left: 0;
    animation: fadeIn 0.4s ease;
}}

/* ── Inputs ── */
label,
[data-testid="stTextInput"] label {{
    color: {TEXT_SECOND} !important;
    font-weight: 500;
    font-size: 0.85rem;
    letter-spacing: 0.3px;
}}
/* ── Text inputs — aggressive override ── */
.stTextInput > div > div > input,
.stTextInput input,
[data-baseweb="input"] input,
[data-baseweb="base-input"] input,
[data-testid="stForm"] input,
[data-testid="stForm"] input[type="text"],
[data-testid="stTextInput"] input {{
    background: {INPUT_BG} !important;
    background-color: {INPUT_BG} !important;
    color: {TEXT_PRIMARY} !important;
    -webkit-text-fill-color: {TEXT_PRIMARY} !important;
    border: 1px solid {INPUT_BDR} !important;
    border-radius: 10px !important;
    padding: 0.65rem 1rem !important;
    font-size: 0.92rem;
    backdrop-filter: blur(10px);
    transition: all 0.25s ease;
    caret-color: {TEXT_PRIMARY} !important;
}}
/* Input wrapper / container */
[data-baseweb="input"],
[data-baseweb="base-input"],
.stTextInput [data-baseweb="input"],
.stTextInput [data-baseweb="base-input"] {{
    background-color: {INPUT_BG} !important;
    background: {INPUT_BG} !important;
    border-color: {INPUT_BDR} !important;
}}
/* Placeholder */
.stTextInput input::placeholder,
[data-baseweb="input"] input::placeholder,
[data-testid="stTextInput"] input::placeholder {{
    color: {TEXT_MUTED} !important;
    -webkit-text-fill-color: {TEXT_MUTED} !important;
    opacity: 1 !important;
}}
.stTextInput > div > div > input:focus {{
    border-color: {ACCENT} !important;
    box-shadow: 0 0 0 2px {"rgba(255,255,255,0.08)" if dark else "rgba(0,0,0,0.05)"} !important;
    outline: none !important;
}}

/* ── Selectbox ── */
[data-testid="stSelectbox"] label {{
    color: {TEXT_SECOND} !important;
    font-weight: 500;
    font-size: 0.85rem;
}}
[data-testid="stSelectbox"] div[data-baseweb="select"] > div {{
    background: {INPUT_BG} !important;
    color: {TEXT_PRIMARY} !important;
    border: 1px solid {INPUT_BDR} !important;
    border-radius: 10px !important;
    backdrop-filter: blur(10px);
}}

/* ── Buttons ── */
.stButton > button {{
    background: {TEXT_PRIMARY} !important;
    color: {BG_PRIMARY} !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.6rem 1.8rem !important;
    font-size: 0.9rem !important;
    font-weight: 600 !important;
    cursor: pointer !important;
    transition: all 0.3s cubic-bezier(0.4,0,0.2,1) !important;
    letter-spacing: 0.3px;
}}
.stButton > button:hover {{
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 24px {"rgba(255,255,255,0.15)" if dark else "rgba(0,0,0,0.12)"} !important;
    opacity: 0.9 !important;
}}
.stButton > button:active {{ transform: translateY(0px) !important; }}

/* ── Form submit button ── */
.stFormSubmitButton > button {{
    background: {TEXT_PRIMARY} !important;
    color: {BG_PRIMARY} !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.6rem 1.8rem !important;
    font-size: 0.9rem !important;
    font-weight: 600 !important;
    cursor: pointer !important;
    transition: all 0.3s cubic-bezier(0.4,0,0.2,1) !important;
    letter-spacing: 0.3px;
}}
.stFormSubmitButton > button:hover {{
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 24px {"rgba(255,255,255,0.15)" if dark else "rgba(0,0,0,0.12)"} !important;
    opacity: 0.9 !important;
}}

/* ── Tabs ── */
[data-baseweb="tab-list"] {{
    gap: 0;
    background-color: transparent !important;
    border-bottom: 1px solid {DIVIDER};
    padding-bottom: 0;
}}
[data-baseweb="tab"] {{
    background-color: transparent !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    color: {TEXT_MUTED} !important;
    font-weight: 500 !important;
    padding: 0.6rem 1.5rem !important;
    font-size: 0.88rem !important;
    transition: all 0.25s ease;
    border-radius: 0 !important;
}}
[data-baseweb="tab"]:hover {{
    color: {TEXT_SECOND} !important;
}}
[aria-selected="true"][data-baseweb="tab"] {{
    background-color: transparent !important;
    color: {TEXT_PRIMARY} !important;
    font-weight: 600 !important;
    border-bottom: 2px solid {TEXT_PRIMARY} !important;
}}

/* ── Glass cards ── */
.book-card {{
    background: {GLASS};
    border: 1px solid {GLASS_BDR};
    border-radius: 14px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 0.75rem;
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
    animation: fadeInUp 0.45s ease both;
}}
.book-card:hover {{
    background: {"rgba(255,255,255,0.09)" if dark else "rgba(0,0,0,0.04)"};
    border-color: {"rgba(255,255,255,0.18)" if dark else "rgba(0,0,0,0.10)"};
    transform: translateY(-2px);
}}

.book-cover {{
    width: 48px;
    height: 68px;
    border-radius: 6px;
    background: {ACCENT_DIM};
    border: 1px solid {GLASS_BDR};
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
    font-weight: 700;
    color: {TEXT_PRIMARY};
    flex-shrink: 0;
    overflow: hidden;
}}
.book-cover img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
    border-radius: 5px;
}}
.book-cover-fallback {{
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 100%;
    font-size: 1.2rem;
    font-weight: 700;
}}
.card-grid {{ display: flex; gap: 1rem; align-items: flex-start; }}
.card-body {{ flex: 1; min-width: 0; }}

.book-title {{
    font-size: 1.05rem;
    font-weight: 600;
    color: {TEXT_PRIMARY};
    margin-bottom: 0.15rem;
    letter-spacing: -0.2px;
}}

/* ── Buy link ── */
.buy-link {{
    display: inline-block;
    font-size: 0.72rem;
    font-weight: 600;
    border-radius: 20px;
    padding: 0.15rem 0.7rem;
    margin-left: 0.2rem;
    border: 1px solid {GLASS_BDR};
    background: transparent;
    color: {TEXT_SECOND};
    text-decoration: none;
    letter-spacing: 0.3px;
    transition: all 0.2s ease;
}}
.buy-link:hover {{
    background: {TEXT_PRIMARY};
    color: {BG_PRIMARY};
    border-color: {TEXT_PRIMARY};
    text-decoration: none;
}}

/* ── Top banner cover ── */
.top-banner-grid {{
    display: flex;
    gap: 1.2rem;
    align-items: flex-start;
}}
.top-banner-cover {{
    width: 72px;
    height: 100px;
    border-radius: 8px;
    overflow: hidden;
    flex-shrink: 0;
    background: {ACCENT_DIM};
    border: 1px solid {BANNER_BDR};
}}
.top-banner-cover img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
}}
.book-meta {{
    font-size: 0.82rem;
    color: {TEXT_SECOND};
    margin-bottom: 0.4rem;
}}
.book-desc-short {{
    font-size: 0.84rem;
    color: {TEXT_MUTED};
    line-height: 1.55;
    margin-top: 0.4rem;
}}

/* ── Rank number ── */
.rank-num {{
    font-size: 0.72rem;
    font-weight: 600;
    color: {TEXT_MUTED};
    letter-spacing: 0.5px;
    margin-bottom: 0.35rem;
}}

/* ── Badges ── */
.badge {{
    display: inline-block;
    font-size: 0.72rem;
    font-weight: 600;
    border-radius: 20px;
    padding: 0.12rem 0.6rem;
    margin-right: 0.35rem;
    border: 1px solid {GLASS_BDR};
    background: {ACCENT_DIM};
    color: {TEXT_SECOND};
    letter-spacing: 0.2px;
}}
.badge-accent {{
    background: {TEXT_PRIMARY};
    color: {BG_PRIMARY};
    border-color: transparent;
}}

/* ── Score bar ── */
.score-bar-wrap {{ margin-top: 0.5rem; }}
.score-bar-bg {{
    background: {SCORE_BAR_BG};
    border-radius: 99px;
    height: 4px;
    overflow: hidden;
}}
.score-bar-fill {{
    height: 4px;
    border-radius: 99px;
    background: {SCORE_BAR_FG};
    transition: width 0.8s cubic-bezier(0.4,0,0.2,1);
}}
.score-label {{
    font-size: 0.72rem;
    color: {TEXT_MUTED};
    font-weight: 500;
    margin-bottom: 0.12rem;
    letter-spacing: 0.3px;
}}

/* ── Top banner ── */
.top-rec-banner {{
    background: {BANNER_BG};
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border: 1px solid {BANNER_BDR};
    border-radius: 16px;
    padding: 1.6rem 2rem;
    margin-bottom: 1.5rem;
    animation: fadeInUp 0.5s ease;
}}
.top-rec-label {{
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    color: {TEXT_MUTED};
    margin-bottom: 0.5rem;
}}
.top-rec-title {{
    font-size: 1.4rem;
    font-weight: 700;
    color: {TEXT_PRIMARY};
    margin-bottom: 0.2rem;
    letter-spacing: -0.3px;
}}
.top-rec-meta {{
    font-size: 0.85rem;
    color: {TEXT_SECOND};
    margin-bottom: 0.65rem;
    line-height: 1.6;
}}
.top-rec-desc {{
    font-size: 0.86rem;
    color: {TEXT_MUTED};
    line-height: 1.6;
}}

/* ── Info box ── */
.info-box {{
    background: {GLASS};
    border: 1px solid {GLASS_BDR};
    border-radius: 10px;
    padding: 0.7rem 1rem;
    color: {TEXT_SECOND};
    font-size: 0.84rem;
    margin-bottom: 1.3rem;
    backdrop-filter: blur(12px);
    animation: fadeIn 0.4s ease;
}}

/* ── No results ── */
.no-results {{
    text-align: center;
    padding: 2.5rem 1.5rem;
    background: {GLASS};
    border: 1px solid {GLASS_BDR};
    border-radius: 14px;
    color: {TEXT_SECOND};
    font-size: 0.95rem;
    backdrop-filter: blur(16px);
    animation: fadeIn 0.4s ease;
}}
.no-results ul {{ list-style: none; padding: 0; margin: 1rem 0 0; }}
.no-results li {{
    display: inline-block;
    margin: 0.2rem;
    background: {ACCENT_DIM};
    color: {TEXT_SECOND};
    border-radius: 20px;
    padding: 0.25rem 0.85rem;
    font-size: 0.82rem;
    font-weight: 500;
    border: 1px solid {GLASS_BDR};
    cursor: default;
    transition: all 0.2s ease;
}}
.no-results li:hover {{
    background: {"rgba(255,255,255,0.12)" if dark else "rgba(0,0,0,0.06)"};
}}

/* ── History item ── */
.hist-item {{
    background: {GLASS};
    border: 1px solid {GLASS_BDR};
    border-radius: 10px;
    padding: 0.5rem 0.75rem;
    font-size: 0.82rem;
    color: {TEXT_SECOND};
    margin-bottom: 0.4rem;
    backdrop-filter: blur(10px);
    transition: background 0.2s ease;
    animation: slideDown 0.3s ease both;
}}
.hist-item:hover {{
    background: {"rgba(255,255,255,0.08)" if dark else "rgba(0,0,0,0.04)"};
}}

/* ── Slider ── */
[data-testid="stSlider"] label {{ color: {TEXT_SECOND} !important; font-weight: 500; }}

/* ── Download button ── */
[data-testid="stDownloadButton"] > button {{
    background: transparent !important;
    color: {TEXT_SECOND} !important;
    border: 1px solid {GLASS_BDR} !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
    transition: all 0.25s ease !important;
    backdrop-filter: blur(10px);
}}
[data-testid="stDownloadButton"] > button:hover {{
    background: {ACCENT_DIM} !important;
    border-color: {"rgba(255,255,255,0.20)" if dark else "rgba(0,0,0,0.15)"} !important;
    color: {TEXT_PRIMARY} !important;
}}

/* ── Clear History / sidebar buttons ── */
[data-testid="stSidebar"] .stButton > button {{
    background: transparent !important;
    color: {TEXT_SECOND} !important;
    border: 1px solid {GLASS_BDR} !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
    font-size: 0.82rem !important;
    padding: 0.4rem 1rem !important;
}}
[data-testid="stSidebar"] .stButton > button:hover {{
    background: {ACCENT_DIM} !important;
    color: {TEXT_PRIMARY} !important;
    border-color: {"rgba(255,255,255,0.20)" if dark else "rgba(0,0,0,0.15)"} !important;
}}

/* ── Metric styling ── */
[data-testid="stMetric"] {{
    background: {GLASS};
    border: 1px solid {GLASS_BDR};
    border-radius: 12px;
    padding: 0.8rem 1rem;
    backdrop-filter: blur(12px);
}}
[data-testid="stMetricValue"] {{ color: {TEXT_PRIMARY} !important; font-weight: 600 !important; }}
[data-testid="stMetricLabel"] {{ color: {TEXT_MUTED} !important; font-size: 0.78rem !important; }}

/* ── Expander ── */
.streamlit-expanderHeader {{
    font-size: 0.84rem !important;
    color: {TEXT_SECOND} !important;
    font-weight: 500 !important;
}}

/* ── Source card accent ── */
.source-label {{
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: {TEXT_MUTED};
    margin-bottom: 0.4rem;
}}

/* ── Divider line ── */
.glass-divider {{
    height: 1px;
    background: {DIVIDER};
    margin: 1.5rem 0;
    animation: fadeIn 0.4s ease;
}}
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────
# Dataset (cached)
# ──────────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def get_data() -> pd.DataFrame:
    return load_dataset()

with st.spinner("Loading book dataset..."):
    df = get_data()

ALL_TITLES: list[str] = sorted(df["Title"].dropna().unique().tolist())
ALL_GENRES: list[str] = sorted(df["Genre"].dropna().unique().tolist())


# ──────────────────────────────────────────────────────────────────────────
# Utilities
# ──────────────────────────────────────────────────────────────────────────
def _cover_html(isbn: str, title: str) -> str:
    """Return <img> from Open Library Covers API, or a fallback letter."""
    fallback = title[0].upper() if title else "B"
    if isbn and isbn.strip() and isbn.strip() != "nan":
        url = f"https://covers.openlibrary.org/b/isbn/{isbn.strip()}-M.jpg"
        return f'<img src="{url}" alt="{title}" onerror="this.outerHTML=\'{fallback}\'" loading="lazy">'
    return f'<span class="book-cover-fallback">{fallback}</span>'


def _buy_url(title: str, author: str) -> str:
    """Return an Amazon search URL for the book."""
    query = urllib.parse.quote_plus(f"{title} {author}")
    return f"https://www.amazon.com/s?k={query}"


def _score_bar(score: float) -> str:
    pct = int(score * 100)
    return f"""
    <div class="score-bar-wrap">
        <div class="score-label">Match: {pct}%</div>
        <div class="score-bar-bg">
            <div class="score-bar-fill" style="width:{pct}%"></div>
        </div>
    </div>"""


def df_to_csv_bytes(results_df: pd.DataFrame) -> bytes:
    buf = io.StringIO()
    results_df.to_csv(buf, index=False)
    return buf.getvalue().encode()


def add_to_history(query: str, qtype: str, results_df: pd.DataFrame) -> None:
    entry = {"query": query, "type": qtype, "results": results_df}
    if st.session_state.history and st.session_state.history[-1]["query"] == query:
        return
    st.session_state.history.insert(0, entry)
    if len(st.session_state.history) > 10:
        st.session_state.history.pop()


# ──────────────────────────────────────────────────────────────────────────
# Render helpers
# ──────────────────────────────────────────────────────────────────────────
def render_top_book(book: dict) -> None:
    """Highlighted banner for the #1 recommendation."""
    title  = book.get("Title", "Unknown Title")
    author = book.get("Author", "Unknown")
    genre  = book.get("Genre", "—")
    rating = book.get("Rating", None)
    isbn   = str(book.get("ISBN", ""))
    rating_str = f"{rating:.1f} / 5.0" if isinstance(rating, (int, float)) else "—"
    score = book.get("Score", 0)
    pct = int(score * 100)
    desc = book.get("Description", "No description available.")
    cover = _cover_html(isbn, title)
    buy  = _buy_url(title, author)
    st.markdown(f"""
    <div class="top-rec-banner">
        <div class="top-rec-label">Best Match</div>
        <div class="top-banner-grid">
            <div class="top-banner-cover">{cover}</div>
            <div>
                <div class="top-rec-title">{title}</div>
                <div class="top-rec-meta">
                    {author} &nbsp;·&nbsp;
                    {genre} &nbsp;·&nbsp;
                    {rating_str}
                </div>
                <div style="margin-bottom:.65rem;">
                    <div class="score-label">Match: {pct}%</div>
                    <div class="score-bar-bg" style="max-width:280px;">
                        <div class="score-bar-fill" style="width:{pct}%"></div>
                    </div>
                </div>
                <div class="top-rec-desc">{desc[:260]}{"..." if len(desc)>260 else ""}</div>
                <div style="margin-top:.6rem"><a class="buy-link" href="{buy}" target="_blank" rel="noopener">Buy on Amazon</a></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_book_card(book: dict, rank: int = 0, show_score: bool = True) -> None:
    """Glass card for a recommendation with cover image and buy link."""
    title   = book.get("Title", "Unknown Title")
    author  = book.get("Author", "Unknown Author")
    genre   = book.get("Genre", "")
    rating  = book.get("Rating", None)
    isbn    = str(book.get("ISBN", ""))
    score   = book.get("Score", 0)
    desc    = book.get("Description", "No description available.")
    cover   = _cover_html(isbn, title)
    buy     = _buy_url(title, author)

    rating_html  = f'<span class="badge">{rating:.1f}</span>' if isinstance(rating, (int, float)) else ""
    genre_html   = f'<span class="badge">{genre}</span>' if genre else ""
    score_html   = f'<span class="badge badge-accent">{int(score*100)}% match</span>' if show_score else ""
    bar_html     = _score_bar(score) if show_score else ""
    rank_html    = f'<div class="rank-num">#{rank}</div>' if rank > 0 else ""
    short_desc   = desc[:140] + ("..." if len(desc) > 140 else "")

    st.markdown(f"""
    <div class="book-card" style="animation-delay:{rank * 0.05}s">
        {rank_html}
        <div class="card-grid">
            <div class="book-cover">{cover}</div>
            <div class="card-body">
                <div class="book-title">{title}</div>
                <div class="book-meta">{author}</div>
                <div style="margin-bottom:.35rem">{rating_html}{genre_html}{score_html}
                    <a class="buy-link" href="{buy}" target="_blank" rel="noopener">Buy</a>
                </div>
                {bar_html}
                <div class="book-desc-short">{short_desc}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if len(desc) > 140:
        with st.expander("Read full description", expanded=False):
            st.markdown(f'<span style="color:{TEXT_SECOND};font-size:.86rem;line-height:1.6">{desc}</span>',
                        unsafe_allow_html=True)


def render_source_card(book: dict) -> None:
    """Source/matched book card with cover image."""
    title   = book.get("Title", "Unknown Title")
    author  = book.get("Author", "Unknown Author")
    genre   = book.get("Genre", "")
    rating  = book.get("Rating", None)
    isbn    = str(book.get("ISBN", ""))
    desc    = book.get("Description", "No description available.")
    cover   = _cover_html(isbn, title)
    buy     = _buy_url(title, author)

    rating_html  = f'<span class="badge">{rating:.1f}</span>' if isinstance(rating, (int, float)) else ""
    genre_html   = f'<span class="badge">{genre}</span>' if genre else ""

    st.markdown(f"""
    <div class="book-card" style="border-color:{"rgba(255,255,255,0.18)" if dark else "rgba(0,0,0,0.10)"}">
        <div class="source-label">Your Selection</div>
        <div class="card-grid">
            <div class="book-cover">{cover}</div>
            <div class="card-body">
                <div class="book-title">{title}</div>
                <div class="book-meta">{author}</div>
                <div style="margin-bottom:.35rem">{rating_html}{genre_html}
                    <a class="buy-link" href="{buy}" target="_blank" rel="noopener">Buy</a>
                </div>
                <div class="book-desc-short">{desc[:140]}{"..." if len(desc)>140 else ""}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if len(desc) > 140:
        with st.expander("Read full description", expanded=False):
            st.markdown(f'<span style="color:{TEXT_SECOND};font-size:.86rem;line-height:1.6">{desc}</span>',
                        unsafe_allow_html=True)


def render_no_results(query: str = "") -> None:
    popular_genres = ["Fantasy", "Fiction", "Science Fiction", "Mystery",
                      "Thriller", "Romance", "Horror", "Dystopian", "Non-Fiction"]
    pills = "".join(f"<li>{g}</li>" for g in popular_genres)
    msg = f'No results for "<b>{query}</b>".' if query else "No matching books found."
    st.markdown(f"""
    <div class="no-results">
        {msg}
        <br><span style="font-size:.84rem">Try broadening your search or pick a genre below:</span>
        <ul>{pills}</ul>
    </div>
    """, unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────
# Sidebar
# ──────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f'<div style="font-size:1rem;font-weight:600;color:{TEXT_PRIMARY};margin-bottom:.6rem;letter-spacing:-0.3px">Controls</div>',
                unsafe_allow_html=True)

    toggled = st.toggle("Dark Mode", value=st.session_state.dark_mode, key="dm_toggle")
    if toggled != st.session_state.dark_mode:
        st.session_state.dark_mode = toggled
        st.rerun()

    st.markdown(f'<div class="glass-divider"></div>', unsafe_allow_html=True)

    # Dataset stats
    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("Books", f"{len(df):,}")
    with col_b:
        st.metric("Genres", f"{len(ALL_GENRES)}")

    st.markdown(f'<div class="glass-divider"></div>', unsafe_allow_html=True)

    # History
    st.markdown(f'<div style="font-size:.88rem;font-weight:600;color:{TEXT_PRIMARY};margin-bottom:.5rem">Recent Searches</div>',
                unsafe_allow_html=True)

    if not st.session_state.history:
        st.markdown(f'<span style="font-size:.82rem;color:{TEXT_MUTED}">No searches yet. Try the search tabs to get started.</span>',
                    unsafe_allow_html=True)
    else:
        for i, h in enumerate(st.session_state.history):
            label = "Genre / Author" if h["type"] == "genre_author" else "By Title"
            st.markdown(f"""
            <div class="hist-item" style="animation-delay:{i * 0.05}s">
                <b>{h['query']}</b><br>
                <span style="font-size:.74rem;color:{TEXT_MUTED}">{label} · {len(h['results'])} results</span>
            </div>""", unsafe_allow_html=True)

        if st.button("Clear History", key="clear_hist"):
            st.session_state.history = []
            st.rerun()


# ──────────────────────────────────────────────────────────────────────────
# Header
# ──────────────────────────────────────────────────────────────────────────
st.markdown(f'<div class="main-title">Smart Book Recommender</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="subtitle">Best-First Search · Heuristic AI · '
    f'{len(df):,} books</div>',
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────────────────────────────────
# Tabs
# ──────────────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["By Genre & Author", "By Book Title"])


# ══════════════════════════════════════════════════════════════════════════
# TAB 1 — Genre & Author
# ══════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown(f'<div class="section-header">Search by Genre & Author</div>',
                unsafe_allow_html=True)
    st.markdown(
        f'<div class="info-box">Pick a genre from the dropdown and optionally type an author name. '
        'Press Enter or click the button to search. The system uses a Best-First Search heuristic '
        '(0.6 Genre + 0.4 Author) to rank results.</div>',
        unsafe_allow_html=True,
    )

    with st.form("genre_author_form", clear_on_submit=False):
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            genre_options = ["(Any genre)"] + ALL_GENRES
            genre_selected = st.selectbox("Genre", options=genre_options, key="genre_select")
            genre_input = "" if genre_selected == "(Any genre)" else genre_selected
        with col2:
            author_input = st.text_input("Author",
                                         placeholder="e.g. Rowling, Tolkien...",
                                         key="author_input")
        with col3:
            top_n_1 = st.select_slider("Results", options=[5, 10, 15], value=10, key="topn1")

        submitted_1 = st.form_submit_button("Get Recommendations")

    if submitted_1:
        if not genre_input.strip() and not author_input.strip():
            st.warning("Please enter at least a genre or an author name.")
        else:
            with st.spinner("Searching..."):
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
                    st.markdown(f'<div class="section-header" style="margin-top:1.3rem">More Recommendations</div>',
                                unsafe_allow_html=True)
                    for i, (_, row) in enumerate(similar_df.iterrows()):
                        render_book_card(row.to_dict(), rank=i + 2)
                    all_results = pd.concat([all_results, similar_df], ignore_index=True)

                query_label = f"Genre:{genre_input} Author:{author_input}".strip()
                add_to_history(query_label, "genre_author", all_results)
                st.download_button(
                    label="Save as CSV",
                    data=df_to_csv_bytes(all_results),
                    file_name="book_recommendations.csv",
                    mime="text/csv",
                    key="dl1",
                )


# ══════════════════════════════════════════════════════════════════════════
# TAB 2 — Book Title
# ══════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown(f'<div class="section-header">Search by Book Title</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="info-box">Type to filter titles, select one from the dropdown, then submit. '
        'The system extracts the book\'s genre and author to find similar reads.</div>',
        unsafe_allow_html=True,
    )

    # Title filter lives outside the form so it updates the selectbox dynamically
    title_filter = st.text_input("Filter titles...", placeholder="Start typing a book name...", key="title_filter")
    if title_filter.strip():
        filtered_titles = [t for t in ALL_TITLES
                           if title_filter.strip().lower() in t.lower()][:60]
    else:
        filtered_titles = ALL_TITLES[:60]

    with st.form("title_form", clear_on_submit=False):
        col_t, col_n = st.columns([3, 1])
        with col_t:
            if not filtered_titles:
                st.warning("No matching titles — try a different keyword.")
                title_selected = ""
            else:
                title_selected = st.selectbox("Select Book", options=filtered_titles,
                                              key="title_select")
        with col_n:
            top_n_2 = st.select_slider("Results", options=[5, 10, 15], value=10, key="topn2")

        submitted_2 = st.form_submit_button("Find Similar Books")

    if submitted_2:
        if not title_selected:
            st.warning("Please select a book title.")
        else:
            with st.spinner("Searching..."):
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
                    f'<div class="info-box" style="margin-top:.4rem">'
                    f'<b>Genre:</b> {found_book.get("Genre","—")} &nbsp;·&nbsp; '
                    f'<b>Author:</b> {found_book.get("Author","—")} — '
                    f'using these as search heuristics.</div>',
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
                        st.markdown(f'<div class="section-header" style="margin-top:1.3rem">More Recommendations</div>',
                                    unsafe_allow_html=True)
                        for i, (_, row) in enumerate(similar_df.iterrows()):
                            render_book_card(row.to_dict(), rank=i + 2)
                        all_results = pd.concat([all_results, similar_df], ignore_index=True)

                    add_to_history(title_selected, "by_title", all_results)
                    if not all_results.empty:
                        st.download_button(
                            label="Save as CSV",
                            data=df_to_csv_bytes(all_results),
                            file_name="book_recommendations.csv",
                            mime="text/csv",
                            key="dl2",
                        )


# ──────────────────────────────────────────────────────────────────────────
# Footer
# ──────────────────────────────────────────────────────────────────────────
st.markdown(f'<div class="glass-divider"></div>', unsafe_allow_html=True)
st.markdown(f"""
<div style="text-align:center;color:{TEXT_MUTED};font-size:.78rem;padding:.5rem 0;letter-spacing:0.3px;">
    Smart Book Recommender &nbsp;·&nbsp; Best-First Search &nbsp;·&nbsp; Python + Streamlit
</div>
""", unsafe_allow_html=True)
