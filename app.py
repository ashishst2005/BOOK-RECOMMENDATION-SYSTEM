"""
app.py  (v3 — Glassmorphism Edition)
-------------------------------------
Smart Book Recommendation System — Streamlit Frontend

Design: True black / white, glassmorphism, no emojis, minimalist premium.
"""

import html
import io
import math
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
if "view_mode" not in st.session_state:
    st.session_state.view_mode = "tiles"   # "tiles" or "list"
if "tab1_results" not in st.session_state:
    st.session_state.tab1_results = None   # cached genre/author results
if "tab2_results" not in st.session_state:
    st.session_state.tab2_results = None   # cached title results

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

/* ── Tile / Grid View ── */
.tile-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 1rem;
    animation: fadeIn 0.4s ease;
}}
.tile-card {{
    background: {GLASS};
    border: 1px solid {GLASS_BDR};
    border-radius: 14px;
    padding: 0;
    overflow: hidden;
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
    animation: fadeInUp 0.45s ease both;
    display: flex;
    flex-direction: column;
}}
.tile-card:hover {{
    background: {"rgba(255,255,255,0.09)" if dark else "rgba(0,0,0,0.04)"};
    border-color: {"rgba(255,255,255,0.18)" if dark else "rgba(0,0,0,0.10)"};
    transform: translateY(-4px);
    box-shadow: 0 12px 32px {"rgba(0,0,0,0.4)" if dark else "rgba(0,0,0,0.10)"};
}}
.tile-cover {{
    width: 100%;
    aspect-ratio: 2/3;
    background: {ACCENT_DIM};
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    position: relative;
}}
.tile-cover img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
}}
.tile-cover-fallback {{
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 100%;
    font-size: 2.2rem;
    font-weight: 700;
    color: {TEXT_MUTED};
}}
.tile-body {{
    padding: 0.75rem 0.9rem 0.9rem;
    flex: 1;
    display: flex;
    flex-direction: column;
}}
.tile-title {{
    font-size: 0.88rem;
    font-weight: 600;
    color: {TEXT_PRIMARY};
    margin-bottom: 0.15rem;
    letter-spacing: -0.2px;
    line-height: 1.3;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}}
.tile-author {{
    font-size: 0.76rem;
    color: {TEXT_SECOND};
    margin-bottom: 0.4rem;
}}
.tile-badges {{
    margin-top: auto;
    display: flex;
    flex-wrap: wrap;
    gap: 0.25rem;
}}
.tile-rank {{
    position: absolute;
    top: 8px;
    left: 8px;
    background: {"rgba(0,0,0,0.65)" if dark else "rgba(255,255,255,0.85)"};
    backdrop-filter: blur(8px);
    color: {TEXT_PRIMARY};
    font-size: 0.68rem;
    font-weight: 700;
    padding: 0.15rem 0.5rem;
    border-radius: 20px;
    letter-spacing: 0.5px;
}}
.tile-score-pill {{
    position: absolute;
    top: 8px;
    right: 8px;
    background: {TEXT_PRIMARY};
    color: {BG_PRIMARY};
    font-size: 0.65rem;
    font-weight: 700;
    padding: 0.15rem 0.5rem;
    border-radius: 20px;
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
def _cover_html(isbn: str, title: str, cover_url: str = "") -> str:
    """Return <img> using CoverURL, Open Library ISBN fallback, or letter."""
    fallback = title[0].upper() if title else "B"
    # Prefer the direct cover URL from the dataset (e.g. Goodreads)
    if cover_url and cover_url.strip() and cover_url.strip() != "nan":
        return f'<img src="{cover_url.strip()}" alt="{title}" class="book-cover-img" onerror="this.outerHTML=\'{fallback}\'" loading="lazy">'
    # Fallback: Open Library Covers API via ISBN
    if isbn and isbn.strip() and isbn.strip() != "nan":
        url = f"https://covers.openlibrary.org/b/isbn/{isbn.strip()}-M.jpg"
        return f'<img src="{url}" alt="{title}" class="book-cover-img" onerror="this.outerHTML=\'{fallback}\'" loading="lazy">'
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
def _tile_cover_html(isbn: str, title: str, cover_url: str = "") -> str:
    """Return <img> for tile view (larger, no fallback span wrapper)."""
    fallback = html.escape(title[0].upper()) if title else "B"
    safe_title = html.escape(title, quote=True)
    if cover_url and cover_url.strip() and cover_url.strip() != "nan":
        src = html.escape(cover_url.strip(), quote=True)
        return f'<img src="{src}" alt="{safe_title}" onerror="this.style.display=&quot;none&quot;;this.parentElement.innerHTML=&quot;{fallback}&quot;" loading="lazy">'
    if isbn and isbn.strip() and isbn.strip() != "nan":
        url = f"https://covers.openlibrary.org/b/isbn/{isbn.strip()}-M.jpg"
        return f'<img src="{url}" alt="{safe_title}" onerror="this.style.display=&quot;none&quot;;this.parentElement.innerHTML=&quot;{fallback}&quot;" loading="lazy">'
    return f'<div class="tile-cover-fallback">{fallback}</div>'


def render_top_book(book: dict) -> None:
    """Highlighted banner for the #1 recommendation."""
    title  = book.get("Title", "Unknown Title")
    author = book.get("Author", "Unknown")
    genre  = book.get("Genre", "—")
    rating = book.get("Rating", None)
    isbn   = str(book.get("ISBN", ""))
    cover_url = str(book.get("CoverURL", ""))
    rating_str = f"{rating:.1f} / 5.0" if isinstance(rating, (int, float)) else "—"
    score = book.get("Score", 0)
    pct = int(score * 100)
    desc = book.get("Description", "No description available.")
    cover = _cover_html(isbn, title, cover_url)
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
    """Glass card for a recommendation with cover image and buy link (list view)."""
    title   = book.get("Title", "Unknown Title")
    author  = book.get("Author", "Unknown Author")
    genre   = book.get("Genre", "")
    rating  = book.get("Rating", None)
    isbn    = str(book.get("ISBN", ""))
    cover_url = str(book.get("CoverURL", ""))
    score   = book.get("Score", 0)
    desc    = book.get("Description", "No description available.")
    cover   = _cover_html(isbn, title, cover_url)
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


def _build_tile_html(book: dict, rank: int = 0, show_score: bool = True) -> str:
    """Return the HTML string for a single tile card."""
    title   = html.escape(book.get("Title", "Unknown Title"), quote=True)
    author  = html.escape(book.get("Author", "Unknown Author"), quote=True)
    genre   = html.escape(book.get("Genre", ""), quote=True)
    rating  = book.get("Rating", None)
    isbn    = str(book.get("ISBN", ""))
    cover_url = str(book.get("CoverURL", ""))
    score   = book.get("Score", 0)
    cover   = _tile_cover_html(isbn, book.get("Title", "Unknown Title"), cover_url)
    buy     = _buy_url(book.get("Title", ""), book.get("Author", ""))

    rank_html  = f'<div class="tile-rank">#{rank}</div>' if rank > 0 else ""
    score_html = f'<div class="tile-score-pill">{int(score*100)}%</div>' if show_score else ""
    rating_badge = f'<span class="badge">{rating:.1f}</span>' if isinstance(rating, (int, float)) else ""
    genre_badge  = f'<span class="badge">{genre}</span>' if genre else ""

    return (
        f'<a href="{html.escape(buy, quote=True)}" target="_blank" rel="noopener" '
        f'style="text-decoration:none;color:inherit;">'
        f'<div class="tile-card" style="animation-delay:{rank * 0.04}s">'
        f'<div class="tile-cover">{rank_html}{score_html}{cover}</div>'
        f'<div class="tile-body">'
        f'<div class="tile-title">{title}</div>'
        f'<div class="tile-author">{author}</div>'
        f'<div class="tile-badges">{rating_badge}{genre_badge}</div>'
        f'</div></div></a>'
    )


def render_tiles(books: list[dict], start_rank: int = 2, show_score: bool = True) -> None:
    """Render a list of book dicts as a tile grid."""
    tiles_html = "".join(
        _build_tile_html(b, rank=start_rank + i, show_score=show_score)
        for i, b in enumerate(books)
    )
    st.markdown(f'<div class="tile-grid">{tiles_html}</div>', unsafe_allow_html=True)


def render_view_toggle(key_suffix: str = "main") -> None:
    """Render the tiles / list toggle using st.radio with a stable key."""
    mode = st.radio(
        "View",
        options=["tiles", "list"],
        index=0 if st.session_state.view_mode == "tiles" else 1,
        format_func=lambda x: "▦  Tiles" if x == "tiles" else "☰  List",
        horizontal=True,
        key=f"view_toggle_{key_suffix}",
        label_visibility="collapsed",
    )
    if mode != st.session_state.view_mode:
        st.session_state.view_mode = mode
        st.rerun()


# ──────────────────────────────────────────────────────────────────────────
# Evaluation Metrics
# ──────────────────────────────────────────────────────────────────────────
def compute_metrics(
    results_df: pd.DataFrame,
    target_genre: str = "",
    target_author: str = "",
) -> dict:
    """
    Compute evaluation metrics for the recommendation results.

    Metrics:
      - Genre Precision@K: fraction of results matching target genre
      - Author Recall:     whether any result matches the target author
      - Mean Match Score:  average heuristic score across results
      - NDCG@K:           Normalized Discounted Cumulative Gain
      - Coverage:          number of unique genres in results / unique authors
    """
    if results_df.empty:
        return {}

    k = len(results_df)
    scores = results_df["Score"].tolist() if "Score" in results_df.columns else []

    # Genre Precision@K
    genre_precision = 0.0
    if target_genre.strip():
        genre_matches = sum(
            1 for g in results_df["Genre"].fillna("")
            if target_genre.strip().lower() in str(g).lower()
        )
        genre_precision = genre_matches / k if k else 0.0

    # Author Recall (binary: did we find at least one book by this author?)
    author_recall = 0.0
    if target_author.strip():
        author_hits = sum(
            1 for a in results_df["Author"].fillna("")
            if target_author.strip().lower() in str(a).lower()
        )
        author_recall = min(author_hits / max(1, k), 1.0)

    # F1 Score (harmonic mean of genre precision and author recall)
    f1 = 0.0
    if (genre_precision + author_recall) > 0:
        f1 = 2 * (genre_precision * author_recall) / (genre_precision + author_recall)

    # Mean Match Score
    mean_score = sum(scores) / len(scores) if scores else 0.0

    # NDCG@K — using heuristic scores as relevance
    dcg = 0.0
    for i, s in enumerate(scores):
        dcg += s / math.log2(i + 2)  # i+2 because position is 1-indexed
    ideal_scores = sorted(scores, reverse=True)
    idcg = 0.0
    for i, s in enumerate(ideal_scores):
        idcg += s / math.log2(i + 2)
    ndcg = dcg / idcg if idcg > 0 else 0.0

    # Coverage
    unique_genres  = results_df["Genre"].fillna("").nunique()
    unique_authors = results_df["Author"].fillna("").nunique()

    return {
        "Genre Precision@K": genre_precision,
        "Author Recall": author_recall,
        "F1 Score": f1,
        "Mean Match Score": mean_score,
        "NDCG@K": ndcg,
        "Unique Genres": unique_genres,
        "Unique Authors": unique_authors,
        "K (result count)": k,
    }


def render_metrics_panel(metrics: dict) -> None:
    """Render evaluation metrics in a styled expander."""
    if not metrics:
        return

    with st.expander("Evaluation Metrics", expanded=False):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("F1 Score", f"{metrics['F1 Score']:.2%}")
        with col2:
            st.metric("Genre Prec.", f"{metrics['Genre Precision@K']:.2%}")
        with col3:
            st.metric("Author Recall", f"{metrics['Author Recall']:.2%}")
        with col4:
            st.metric("NDCG@K", f"{metrics['NDCG@K']:.3f}")

        col5, col6, col7, col8 = st.columns(4)
        with col5:
            st.metric("Mean Score", f"{metrics['Mean Match Score']:.2%}")
        with col6:
            st.metric("Genres Found", metrics["Unique Genres"])
        with col7:
            st.metric("Authors Found", metrics["Unique Authors"])
        with col8:
            st.metric("Results (K)", metrics["K (result count)"])

        st.markdown(
            f'<div style="font-size:.78rem;color:{TEXT_MUTED};margin-top:.5rem;line-height:1.6">'
            '<b>Genre Precision@K</b> — fraction of results matching the target genre. '
            '<b>Author Recall</b> — fraction of results by the target author. '
            '<b>F1 Score</b> — harmonic mean of precision &amp; recall. '
            '<b>NDCG@K</b> — ranking quality (1.0 = perfect ordering). '
            '<b>Mean Score</b> — average heuristic score (0.6×genre + 0.4×author).</div>',
            unsafe_allow_html=True,
        )


def render_source_card(book: dict) -> None:
    """Source/matched book card with cover image."""
    title   = book.get("Title", "Unknown Title")
    author  = book.get("Author", "Unknown Author")
    genre   = book.get("Genre", "")
    rating  = book.get("Rating", None)
    isbn    = str(book.get("ISBN", ""))
    cover_url = str(book.get("CoverURL", ""))
    desc    = book.get("Description", "No description available.")
    cover   = _cover_html(isbn, title, cover_url)
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
            # Cache results in session state
            st.session_state.tab1_results = {
                "top_book": top_book,
                "similar_df": similar_df,
                "genre_input": genre_input,
                "author_input": author_input,
            }

    # Display results from session state (survives rerun from toggle)
    if st.session_state.tab1_results is not None:
        res = st.session_state.tab1_results
        top_book = res["top_book"]
        similar_df = res["similar_df"]
        genre_input_cached = res["genre_input"]
        author_input_cached = res["author_input"]

        if top_book is None:
            render_no_results(f"{genre_input_cached} / {author_input_cached}".strip(" /"))
        else:
            render_top_book(top_book)

            all_results = pd.DataFrame([top_book])
            if not similar_df.empty:
                st.markdown(f'<div class="section-header" style="margin-top:1.3rem">More Recommendations</div>',
                            unsafe_allow_html=True)
                render_view_toggle(key_suffix="tab1")
                if st.session_state.view_mode == "tiles":
                    render_tiles([row.to_dict() for _, row in similar_df.iterrows()], start_rank=2)
                else:
                    for i, (_, row) in enumerate(similar_df.iterrows()):
                        render_book_card(row.to_dict(), rank=i + 2)
                all_results = pd.concat([all_results, similar_df], ignore_index=True)

            # Evaluation metrics
            metrics = compute_metrics(all_results, target_genre=genre_input_cached, target_author=author_input_cached)
            render_metrics_panel(metrics)

            if submitted_1:
                query_label = f"Genre:{genre_input_cached} Author:{author_input_cached}".strip()
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
            # Cache results in session state
            st.session_state.tab2_results = {
                "found_book": found_book,
                "top_book": top_book,
                "similar_df": similar_df,
                "title_selected": title_selected,
            }

    # Display results from session state (survives rerun from toggle)
    if st.session_state.tab2_results is not None:
        res = st.session_state.tab2_results
        found_book = res["found_book"]
        top_book = res["top_book"]
        similar_df = res["similar_df"]
        title_cached = res["title_selected"]

        if found_book is None:
            render_no_results(title_cached)
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
                    render_view_toggle(key_suffix="tab2")
                    if st.session_state.view_mode == "tiles":
                        render_tiles([row.to_dict() for _, row in similar_df.iterrows()], start_rank=2)
                    else:
                        for i, (_, row) in enumerate(similar_df.iterrows()):
                            render_book_card(row.to_dict(), rank=i + 2)
                    all_results = pd.concat([all_results, similar_df], ignore_index=True)

                # Evaluation metrics
                metrics = compute_metrics(
                    all_results,
                    target_genre=found_book.get("Genre", ""),
                    target_author=found_book.get("Author", ""),
                )
                render_metrics_panel(metrics)

                if submitted_2:
                    add_to_history(title_cached, "by_title", all_results)
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
