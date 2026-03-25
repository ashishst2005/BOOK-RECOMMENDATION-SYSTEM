# Tech Stack & Design Rationale

This document explains every technology used in the Smart Book Recommender system and why each was chosen.

---

## 1. Python 3

**Role:** Core programming language for all backend logic, data processing, and UI.

**Why Python:**
- **AI/ML ecosystem** — Python is the standard language for AI coursework. Libraries like Pandas, NumPy, and scikit-learn are immediately available.
- **Rapid prototyping** — Dynamic typing and a vast standard library allow fast iteration without boilerplate.
- **Streamlit compatibility** — Streamlit is Python-native, so the entire stack (data loading → algorithm → UI) lives in one language with zero context-switching.

---

## 2. Streamlit

**Role:** Web application framework — handles the UI, routing, state management, and live reloading.

**Why Streamlit over Flask/Django/React:**
- **Zero frontend code** — Streamlit generates the entire UI from Python. No HTML templates, no JavaScript bundling, no REST API layer.
- **Built-in widgets** — Forms, dropdowns, sliders, toggles, tabs, download buttons, and metrics are all first-class. Adding a new input takes one line of code.
- **Hot reload** — The app re-runs on every file save, making the development loop instant.
- **State management** — `st.session_state` provides a simple key-value store for tracking dark mode, search history, and form state without external state libraries.
- **Caching** — `@st.cache_data` caches the dataset in memory so it loads only once, even across reruns.

**Trade-off:** Streamlit controls the layout engine, so pixel-perfect custom layouts require CSS overrides (which we do via `st.markdown` with `unsafe_allow_html=True`).

---

## 3. Pandas

**Role:** Data loading, preprocessing, filtering, and result formatting.

**Why Pandas:**
- **CSV ingestion** — `pd.read_csv()` handles malformed rows, type coercion, and column mapping in one call.
- **Vectorized operations** — Filtering by genre, sorting by rating, and deduplicating titles are all one-liners.
- **DataFrame ↔ dict** — Pandas rows convert to plain Python dicts for the priority queue, and results convert back to DataFrames for display and CSV export.
- **Industry standard** — The most widely used data manipulation library in Python; well-documented and performant for datasets up to millions of rows.

---

## 4. Best-First Search Algorithm

**Role:** Core recommendation engine — ranks books by relevance to the user's query.

**Why Best-First Search:**
- **AI course requirement** — This is a heuristic search algorithm, directly aligned with the course's focus on informed search strategies.
- **Heuristic-driven** — The scoring function `h(n) = 0.6 × genre_match + 0.4 × author_match` prioritizes genre similarity (the stronger signal) while still rewarding author alignment.
- **Priority queue** — Python's `queue.PriorityQueue` provides an O(log n) insertion and extraction, making it efficient even for large datasets.
- **Interpretable** — Unlike black-box ML models, the match percentage on each card is directly derived from the heuristic, making results explainable.

**Implementation detail:** The priority queue stores `(-score, row_index, book_dict)` tuples. The negative score ensures highest-scoring books are dequeued first. The `row_index` integer breaks ties safely, avoiding Pandas Series comparison errors.

### Heuristic Design

| Component       | Weight | Logic                                              |
|-----------------|--------|-----------------------------------------------------|
| `genre_match`   | 0.6    | 1.0 if user's genre appears in book's genre, else 0 |
| `author_match`  | 0.4    | 1.0 if user's author appears in book's author, else 0|

Genre is weighted higher because users typically browse by genre first, then filter by author preference.

---

## 5. Open Library Covers API

**Role:** Fetches real book cover images by ISBN.

**Why Open Library:**
- **Free & open** — No API key required. Covers are served as static images via a simple URL pattern.
- **ISBN-based** — Our dataset includes ISBNs for every book, so lookups are deterministic (no fuzzy title matching needed).
- **Lazy loading** — Images use `loading="lazy"` and `onerror` fallback to a letter initial, so the UI is never blocked by slow or missing cover images.

**URL pattern:**
```
https://covers.openlibrary.org/b/isbn/{ISBN}-M.jpg
```
- `M` = medium size (suitable for cards)
- Returns a blank 1×1 image if no cover exists (handled by our `onerror` fallback)

**Rate limit:** 100 requests per IP per 5 minutes — more than sufficient for a local app with 115 books.

---

## 6. Amazon Search URLs (Buy Links)

**Role:** Provides a "Buy" link on every recommendation card.

**Why Amazon search links:**
- **No API key needed** — A simple URL format (`https://www.amazon.com/s?k={title}+{author}`) opens Amazon's search results page.
- **Universal availability** — Works globally without regional restrictions.
- **Zero maintenance** — No affiliate accounts, no API quotas, no token expiry.

---

## 7. Custom CSS (Glassmorphism Design)

**Role:** Visual styling — overrides Streamlit's default theme with a premium glassmorphism design system.

**Why custom CSS over Streamlit's built-in theming:**
- **Glassmorphism** — `backdrop-filter: blur()` and semi-transparent backgrounds create the frosted-glass effect that Streamlit's theme system doesn't support.
- **True black/white** — The palette uses `#000000` and `#ffffff` exclusively, avoiding Streamlit's default purple/blue accent colors.
- **Animations** — `@keyframes fadeInUp`, `fadeIn`, and `slideDown` add polish that Streamlit doesn't offer natively.
- **Full control** — Custom CSS lets us style every element: inputs, buttons, tabs, cards, badges, score bars, sidebar, and the buy-link hover effect.

**Injection method:** All CSS is injected via `st.markdown(f"<style>...</style>", unsafe_allow_html=True)` at the top of the page, using Python f-strings to swap palette variables based on the dark/light mode toggle.

---

## 8. `urllib.parse` (Standard Library)

**Role:** URL-encodes book titles and author names for the Amazon search link.

**Why:** `urllib.parse.quote_plus()` safely handles special characters (spaces, apostrophes, ampersands) in book titles like "Harry Potter and the Sorcerer's Stone" without breaking the URL.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────┐
│                   Streamlit UI                   │
│  (app.py — forms, cards, CSS, session state)     │
├──────────────────┬──────────────────────────────┤
│   Data Layer     │      Algorithm Layer          │
│  (data_loader.py)│     (recommender.py)           │
│  CSV / Sample    │   Best-First Search            │
│  → Pandas DF     │   → Priority Queue             │
│                  │   → Heuristic Scoring           │
├──────────────────┴──────────────────────────────┤
│              External Services                   │
│  Open Library Covers API    Amazon Search URLs    │
└─────────────────────────────────────────────────┘
```

---

## Summary

| Choice              | Alternative Considered     | Why We Chose This                                    |
|----------------------|----------------------------|------------------------------------------------------|
| Python               | Java, C++                  | AI course standard, Streamlit compatibility           |
| Streamlit            | Flask + React, Django      | Zero frontend code, rapid prototyping, built-in widgets|
| Pandas               | Raw CSV parsing, SQLite    | One-liner data ops, DataFrame ↔ dict conversion       |
| Best-First Search    | Collaborative filtering, KNN| Course requirement, interpretable, no training data needed|
| Open Library API     | Google Books API           | Free, no API key, simple ISBN-based URL               |
| Amazon Search URLs   | Affiliate API, Google Shopping| Zero setup, no API key, universal                    |
| Custom CSS           | Streamlit themes, Tailwind | Full glassmorphism control, animations, dark mode     |
