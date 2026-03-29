# Viva Preparation Guide — Smart Book Recommender System

> **Quick reminder:** This is YOUR project. You built a Book Recommendation System using **Best-First Search** with a **weighted heuristic** for an AI course.

---

## 🔢 Key Numbers to Memorize

| Stat | Value | Where it comes from |
|------|-------|---------------------|
| Total books loaded | **15,309** | `Book_Details.csv` after filtering |
| Total genres | **234** | Unique genres extracted from Goodreads data |
| Unique authors | **7,615** | Distinct author names in dataset |
| Rating range | **3.0 – 5.0** | Books below 3.0 are filtered out |
| Fallback sample books | **115** | Built-in `SAMPLE_BOOKS` list in `data_loader.py` |
| Fallback sample genres | **14** | Fantasy, Sci-Fi, Thriller, Mystery, Dystopian, Romance, Fiction, Horror, Non-Fiction, Self-Help, Historical Fiction, Philosophy, Adventure, Classics |
| Max rows limit | **20,000** | `load_dataset(max_rows=20000)` |
| Average search latency | **< 50 ms** | Per query across 15,309 books |
| Memory footprint | **~25 MB** | Entire app in a single Python process |
| Genre weight in heuristic | **0.6** (60%) | Genre is the primary signal |
| Author weight in heuristic | **0.4** (40%) | Author is the secondary signal |
| Time complexity | **O(n log n)** | Priority queue insert + extract |
| Space complexity | **O(n)** | Storing all books in queue + results |

---

## 🏗️ Architecture (3-Layer)

```
┌─────────────────────────────────────────────────┐
│              Presentation Layer                  │
│   (app.py — Streamlit UI, CSS, session state)    │
├──────────────────┬──────────────────────────────┤
│   Data Layer     │      Algorithm Layer          │
│ (data_loader.py) │     (recommender.py)          │
│ Book_Details.csv │   Best-First Search           │
│  → Pandas DF     │   → Priority Queue            │
│  → 15,309 books  │   → Heuristic Scoring         │
├──────────────────┴──────────────────────────────┤
│              External Services                   │
│  Goodreads Cover Images    Amazon Search URLs     │
└─────────────────────────────────────────────────┘
```

### Files and their roles:

| File | Lines | Role |
|------|-------|------|
| `app.py` | ~1031 | Streamlit UI, CSS styling, rendering logic, session state |
| `data_loader.py` | ~265 | CSV loading, column mapping, genre parsing, filtering, fallback dataset |
| `recommender.py` | ~191 | Heuristic function, Best-First Search, two public API functions |
| `Book_Details.csv` | ~22 MB | Primary Goodreads dataset |
| `requirements.txt` | 4 deps | streamlit, pandas, numpy, requests |

---

## 🧠 The Algorithm — Best-First Search

### What is Best-First Search?
- An **informed (heuristic) search** algorithm
- Uses a **priority queue** to always expand the *most promising* node first
- Unlike BFS/DFS (uninformed), it uses domain knowledge via a heuristic function `h(n)`
- It's a **greedy** variant — picks the best-looking node but doesn't guarantee global optimality

### How does it work in YOUR system?

```
1. Initialize: PQ ← empty priority queue
2. For each book b in dataset:
     score ← h(genre, author, preferred_genre, preferred_author)
     PQ.put((-score, index, book_dict))    ← negative for max-priority
3. While PQ not empty AND |results| < k:
     (neg_score, _, b) ← PQ.get()          ← dequeue highest score
     score ← -neg_score
     If b.title not seen AND score > 0:
         Add b to results
4. Return results sorted by score descending
```

### Why negative scores?
Python's `PriorityQueue` is a **min-heap** — smallest value comes out first. By storing `-score`, the **highest** scoring book gets the **most negative** value and is dequeued first.

### Why store `(neg_score, idx, book_dict)` tuples?
Python compares tuples left-to-right. If two books have the same score, it would try to compare the next element. Using `idx` (an integer) as the tiebreaker avoids comparing `dict` or Pandas `Series` objects, which would raise a `ValueError`.

---

## 📐 The Heuristic Function

```python
h(n) = 0.6 × genre_match + 0.4 × author_match
```

| Component | Weight | Value | Logic |
|-----------|--------|-------|-------|
| `genre_match` | 0.6 | 0.0 or 1.0 | 1.0 if user's genre appears *within* book's genre string (case-insensitive), else 0.0 |
| `author_match` | 0.4 | 0.0 or 1.0 | 1.0 if user's author appears *within* book's author string (case-insensitive), else 0.0 |

### Possible output scores:

| Genre Match? | Author Match? | Score | Percentage |
|---|---|---|---|
| ✅ Yes | ✅ Yes | **1.0** | 100% |
| ✅ Yes | ❌ No | **0.6** | 60% |
| ❌ No | ✅ Yes | **0.4** | 40% |
| ❌ No | ❌ No | **0.0** | 0% (filtered out) |

### Why 0.6/0.4 split?
- Users **primarily browse by genre** — genre is the dominant discovery signal
- Author is a **secondary refinement** — "I like Fantasy by Tolkien"
- This reflects real user behavior patterns

### Is this heuristic admissible?
This is a **ranking heuristic**, not a path-cost heuristic, so admissibility (A* sense) doesn't strictly apply. We use a **greedy best-first** approach — we want the best matches, not the shortest path.

---

## 📊 Two Search Modes

### Mode 1: Genre & Author Search
1. User selects genre from dropdown (234 options) + optionally types author
2. System calls `recommend_by_genre_author(df, genre, author, top_n)`
3. Internally calls `best_first_search()` with user's preferences
4. Returns: `top_book` (best match dict) + `similar_df` (remaining recommendations)

### Mode 2: Title-Based Search
1. User selects a book title from a filterable dropdown
2. System calls `recommend_by_title(df, title, top_n)`
3. Finds the matching book, extracts its genre & author
4. Runs `best_first_search()` using extracted genre & author (excluding the source book)
5. Returns: `found_book` (source) + `top_book` (best rec) + `similar_df`

> **Key insight:** Both modes use the **same underlying BFS algorithm** — Mode 2 just automates input extraction.

---

## 📦 Data Pipeline (data_loader.py)

### Loading flow:
```
1. Check if Book_Details.csv exists
2. Read CSV with pd.read_csv(on_bad_lines="skip")
3. Map columns: book_title→Title, genres→Genre, average_rating→Rating, etc.
4. Parse genres: ast.literal_eval("['Fantasy','Young Adult']") → "Fantasy"
5. Filter: Rating >= 3.0
6. Deduplicate titles (keep first)
7. Limit to 20,000 rows
8. If CSV fails → use built-in SAMPLE_BOOKS (115 books)
```

### Column mapping (handles noisy CSV column names):
```python
"Title":  ["book_title", "title", "name"]
"Author": ["author", "authors", "book_author"]
"Genre":  ["genres", "genre", "categories", "shelves"]
"Rating": ["average_rating", "rating", "avg_rating"]
"ISBN":   ["isbn", "isbn13", "isbn_13"]
"Description": ["book_details", "desc", "description", "synopsis"]
"CoverURL": ["cover_image_uri", "cover_url", "image_url", "thumbnail"]
```

### Genre extraction:
Uses `ast.literal_eval` to parse Python list strings like `"['Fantasy', 'Young Adult', 'Fiction']"` and takes **only the first genre** as the primary genre.

---

## 🎨 UI / Frontend (app.py)

### Design System: Glassmorphism
- **Glassmorphism** = frosted glass effect using `backdrop-filter: blur()` + semi-transparent backgrounds
- Dark mode: true black `#000000` with white glass overlays
- Light mode: true white `#FFFFFF` with dark glass overlays
- Google Font: **Inter** (modern, clean)
- CSS animations: `fadeInUp`, `fadeIn`, `slideDown`

### Key UI Features:
| Feature | How it's implemented |
|---------|---------------------|
| Dark/Light mode | `st.session_state.dark_mode` toggle → swaps CSS palette |
| Book covers | Goodreads CDN URL → Open Library ISBN fallback → letter initial |
| Buy links | `urllib.parse.quote_plus(f"{title} {author}")` → Amazon search URL |
| Match percentage | Score × 100 shown as badge + animated progress bar |
| Search history | `st.session_state.history` — last 10 searches |
| CSV export | `st.download_button` with `io.StringIO` buffer |
| Dataset caching | `@st.cache_data` decorator on `get_data()` |

### Cover image fallback chain:
```
1. Goodreads CoverURL from dataset    → <img src="...goodreads...">
2. Open Library API via ISBN           → <img src="covers.openlibrary.org/b/isbn/{ISBN}-M.jpg">
3. Letter initial                      → <span>H</span>  (first letter of title)
```

---

## 🛠️ Tech Stack Justifications (for "Why did you use X?" questions)

| Technology | Why | Alternative rejected |
|---|---|---|
| **Python** | AI course standard, Pandas/Streamlit ecosystem | Java, C++ — too verbose for prototyping |
| **Streamlit** | Zero frontend code, hot reload, built-in widgets, `session_state` | Flask+React — requires separate frontend |
| **Pandas** | One-liner CSV ops, DataFrame↔dict conversion, vectorized filtering | Raw CSV parsing — no filtering/sorting |
| **Best-First Search** | AI course requirement, interpretable, no training data needed | Collaborative filtering — needs user ratings |
| **PriorityQueue** | O(log n) insert/extract, built into Python stdlib | List sort — O(n log n) every time |
| **Open Library API** | Free, no API key, ISBN-based deterministic lookup | Google Books API — requires API key |
| **Custom CSS** | Full glassmorphism control, animations, true black/white | Streamlit themes — no backdrop-filter support |
| **Goodreads dataset** | Rich metadata: titles, authors, genres, ratings, covers, descriptions | BookCrossing — less metadata |

---

## ✅ Strengths & ❌ Limitations

### Strengths:
1. **Interpretable** — match percentage is directly from heuristic, no black box
2. **Cold-start resilient** — no user history needed, only book metadata
3. **Fast** — < 50ms per query, O(n log n) complexity
4. **Lightweight** — ~25MB memory, single Python process, no GPU
5. **Production features** — real covers, buy links, dark/light mode, CSV export
6. **Scalable** — handles 15,309 books; would work with 100K+ with minor optimization

### Limitations:
1. **Binary heuristic** — genre/author match is 0 or 1, no partial/fuzzy matching
2. **No personalization** — doesn't learn from user behavior
3. **No semantic similarity** — can't recognize "Dystopian" is related to "Science Fiction"
4. **Single genre** — only uses the first genre from multi-genre books
5. **No description matching** — TF-IDF on descriptions would improve relevance

### Future work:
1. Word2Vec/GloVe embeddings for semantic genre matching
2. TF-IDF/BM25 on descriptions
3. User profiles with persistent taste learning
4. Multi-factor heuristic (rating, popularity, recency)
5. Fuzzy genre mapping ("Urban Fantasy" → "Fantasy")

---

## ❓ Likely Viva Questions & Answers

### Category 1: Project Overview

**Q1: What is your project about?**
> A: It's a Smart Book Recommender System that uses Best-First Search, an informed AI search algorithm, to recommend books based on genre and author preferences. It works on a 15,309-book Goodreads dataset and is deployed as a Streamlit web app.

**Q2: Why did you choose this project for an AI course?**
> A: It directly applies core AI concepts — heuristic functions, informed search, and state-space exploration — to a real-world problem. Best-First Search is a fundamental AI search algorithm, and the recommendation domain makes the results tangible and testable.

**Q3: What AI technique does your project use?**
> A: Best-First Search — an informed search algorithm that uses a **priority queue** and a **heuristic function** to explore the most promising nodes first. The heuristic is `h(n) = 0.6 × genre_match + 0.4 × author_match`.

---

### Category 2: Algorithm Deep-Dive

**Q4: What is Best-First Search?**
> A: It's an informed graph search algorithm that selects nodes for expansion based on a heuristic evaluation function h(n). It uses a priority queue to always process the most promising node next. It was formalized by Judea Pearl in 1984.

**Q5: How is Best-First Search different from BFS and DFS?**
> A: BFS and DFS are *uninformed* — they don't use any domain knowledge. BFS explores level by level, DFS goes deep first. Best-First Search uses a *heuristic* to decide which node to explore next, making it more efficient for goal-directed tasks.

**Q6: How is Best-First Search different from A*?**
> A: A* uses `f(n) = g(n) + h(n)` where g(n) is the path cost. Our system doesn't have path costs — we're ranking items, not finding paths. So we use greedy Best-First Search with `f(n) = h(n)` only. A* guarantees optimality with an admissible heuristic; we don't need optimality, we need ranking.

**Q7: Explain your heuristic function.**
> A: `h(n) = 0.6 × genre_match + 0.4 × author_match`. Genre match returns 1.0 if the user's preferred genre appears in the book's genre string (case-insensitive substring match), else 0.0. Author match works similarly. Genre is weighted 60% because users primarily discover books by genre, and author is a secondary filter at 40%.

**Q8: Why did you choose 0.6 and 0.4 as weights?**
> A: Based on user behavior analysis — genre is the primary browsing dimension (most users start with "I want a Fantasy book"), while author is a refinement ("...by Tolkien"). The 60/40 split reflects this natural hierarchy while still rewarding author matches.

**Q9: What is the time complexity of your algorithm?**
> A: O(n log n) where n is the number of books. Each insertion into the priority queue is O(log n), and we do n insertions. Extraction is also O(log n), and we extract at most k elements (where k << n). So total is O(n log n + k log n) ≈ O(n log n).

**Q10: What is the space complexity?**
> A: O(n) — we store all n books in the priority queue plus O(k) for results.

**Q11: Why do you use negative scores in the priority queue?**
> A: Python's `PriorityQueue` is a min-heap — it dequeues the smallest value first. By storing `-score`, the highest scoring book (e.g., score=1.0 stored as -1.0) has the smallest value and gets dequeued first.

**Q12: Why do you store book data as dicts instead of Pandas rows?**
> A: To avoid the `ValueError: The truth value of a Series is ambiguous` error. When Python compares tuples in the priority queue, it may need to compare the third element. Comparing two Pandas Series raises this error, but comparing dicts doesn't happen because the integer index (second element) always breaks ties.

---

### Category 3: Data & Preprocessing

**Q13: What dataset are you using?**
> A: A cleaned Goodreads catalog (`Book_Details.csv`) with 15,309 books across 234 genres. Each entry has: Title, Author, Genre, Rating (3.0-5.0), Description, and Cover Image URL.

**Q14: How do you handle the genre field?**
> A: The raw data stores genres as Python list strings like `"['Fantasy', 'Young Adult', 'Fiction']"`. I use `ast.literal_eval()` to parse this, then take only the **first genre** as the primary genre. I also handle comma, pipe, and slash separators as fallbacks.

**Q15: What preprocessing steps do you perform?**
> A: (1) Column name mapping to handle variant names, (2) Convert ratings to numeric and filter out < 3.0, (3) Parse and extract first genre, (4) Drop rows with missing required fields, (5) Deduplicate titles, (6) Limit to 20,000 rows for performance.

**Q16: What happens if the CSV file is missing?**
> A: The system falls back to a built-in sample dataset of 115 curated books across 14 genres, hardcoded in `data_loader.py`. This ensures the app always works even without the external CSV.

**Q17: Why do you filter books with rating < 3.0?**
> A: To ensure recommendation quality. Books rated below 3.0 are generally considered poor by readers. By filtering them out, we only recommend books that the reading community has rated favorably.

---

### Category 4: Code-Level Questions

**Q18: Walk me through the `recommend_by_title` function.**
> A: (1) Search the DataFrame for titles matching the query using case-insensitive substring match. (2) Pick the highest-rated match as the source book. (3) Extract the source book's genre and author. (4) Remove the source book from the dataset. (5) Run `best_first_search()` on the filtered dataset using the extracted genre/author. (6) Return the source book, best recommendation, and additional recommendations.

**Q19: How does the cover image system work?**
> A: Three-level fallback: First, try the Goodreads cover URL stored in the dataset's `CoverURL` field. If that's missing/invalid, use the Open Library Covers API with the book's ISBN (`covers.openlibrary.org/b/isbn/{ISBN}-M.jpg`). If both fail, show the first letter of the book title as a styled placeholder. Images use `loading="lazy"` and `onerror` handlers.

**Q20: How does session state work in your app?**
> A: Streamlit's `st.session_state` is a dictionary-like store that persists across reruns. I use it for: (1) `dark_mode` — boolean for theme toggle, (2) `history` — list of recent searches (max 10). When dark mode is toggled, I call `st.rerun()` to re-render with the new palette.

**Q21: What does `@st.cache_data` do?**
> A: It caches the return value of `get_data()` so the 22MB CSV is loaded and processed only once. Subsequent reruns (from user interactions) use the cached DataFrame, making the app responsive.

**Q22: How do you generate Amazon buy links?**
> A: Using `urllib.parse.quote_plus(f"{title} {author}")` to URL-encode the book title and author, then constructing `https://www.amazon.com/s?k={encoded_query}`. This opens Amazon's search results page for that book.

---

### Category 5: UI & Design

**Q23: What is Glassmorphism?**
> A: A modern UI design trend featuring frosted glass effects. Achieved through `backdrop-filter: blur()`, semi-transparent backgrounds (e.g., `rgba(255,255,255,0.06)`), subtle borders, and layered depth. It creates a premium, modern look.

**Q24: How do you implement dark/light mode?**
> A: I define two complete CSS palettes (dark: black backgrounds with white overlays; light: white backgrounds with dark overlays). The active palette is selected based on `st.session_state.dark_mode`. When toggled, the app reruns and the CSS is re-injected with the new palette variables using Python f-strings.

**Q25: What animations does your UI have?**
> A: Three CSS keyframe animations: `fadeInUp` (cards slide up while fading in), `fadeIn` (simple opacity fade), `slideDown` (history items slide from top). Cards have staggered animation delays based on their rank for a cascading effect.

---

### Category 6: Comparison & Theory

**Q26: How does your system compare to collaborative filtering?**
> A: 
> | Aspect | My System (Content-Based BFS) | Collaborative Filtering |
> |--------|------|------|
> | Data needed | Only book metadata | User-item interaction matrix |
> | Cold start | ✅ No cold start | ❌ Suffers cold start |
> | Training | None | Requires training |
> | Interpretability | ✅ Match % visible | ❌ Often black box |
> | Personalization | ❌ No user learning | ✅ Learns preferences |

**Q27: Is your system content-based or collaborative?**
> A: It's **content-based**. It uses book attributes (genre, author) to make recommendations, not user interaction data. Specifically, it uses a content-based filtering approach powered by heuristic search.

**Q28: What is the difference between informed and uninformed search?**
> A: Uninformed search (BFS, DFS) has no knowledge about which states are closer to the goal — it explores blindly. Informed search (Best-First, A*) uses a heuristic function h(n) that estimates how promising each state is, guiding exploration toward likely solutions.

**Q29: Can your system handle new books without retraining?**
> A: Yes! Since it's metadata-based with no training phase, adding new books to the CSV is sufficient. The system will include them in the next run — this is the cold-start resilience advantage of content-based approaches.

**Q30: What are the 12 references in your paper?**
> A: Key ones: Adomavicius & Tuzhilin (2005) — RS survey; Pazzani & Billsus (2007) — content-based RS; Resnick et al. (1994) — collaborative filtering; Burke (2002) — hybrid RS; Pearl (1984) — heuristic search; Nilsson (1980) — AI principles.

---

### Category 7: Performance & Validation

**Q31: How did you validate your system?**
> A: (1) **Functional correctness** — tested specific queries (e.g., Genre:Horror → "The Terror", Genre:Fantasy+Author:Tolkien → "The Hobbit" with 100% match). (2) **Title search accuracy** — verified "Dune" → "The Dosadi Experiment" (same author+genre). (3) **Latency** — measured < 50ms per query. (4) **UI testing** — recorded video demos of all features.

**Q32: What is the search latency?**
> A: Under 50 milliseconds per query across 15,309 books. This includes iterating over all books, computing heuristics, priority queue operations, and extracting top-N results.

**Q33: Give an example of a 100% match.**
> A: Query: Genre=Fantasy, Author=Tolkien → Result: "The Hobbit" by J.R.R. Tolkien, Genre=Fantasy. Both genre and author match → h(n) = 0.6(1.0) + 0.4(1.0) = 1.0 = 100%.

**Q34: Give an example of a 60% match.**
> A: Query: Genre=Horror → Result: "The Terror" by Dan Simmons. Genre matches (Horror) but no author was specified → h(n) = 0.6(1.0) + 0.4(0.0) = 0.6 = 60%.

---

### Category 8: Tricky / Deep Questions

**Q35: Why not just sort the dataset instead of using a priority queue?**
> A: Theoretically, sorting gives the same result for this full-scan scenario. However: (1) A priority queue demonstrates the Best-First Search paradigm required by the course, (2) If we later add pruning or early termination, the PQ approach supports it naturally, (3) PQ allows extracting only top-k without fully sorting all n elements.

**Q36: Your heuristic is binary (0 or 1). Isn't that too simple?**
> A: Yes, it's a limitation I acknowledge. It works well for exact genre/author matching but misses partial matches. Future work could use fuzzy matching (Levenshtein distance), TF-IDF on descriptions, or semantic embeddings to produce continuous similarity scores.

**Q37: What if a user searches for only an author with no genre?**
> A: The genre_match returns 0.0 (empty string check), and only author_match contributes. Books by that author get score 0.4 (40% match). This still works — the system returns all books by that author, ranked by the heuristic.

**Q38: What happens with genres that are substrings of other genres?**
> A: Because I use `in` (substring match), searching for "Fiction" would also match "Science Fiction", "Historical Fiction", etc. This is actually beneficial — it provides broader, more inclusive results.

**Q39: Why Streamlit instead of Flask?**
> A: Streamlit eliminates the need for HTML templates, JavaScript, and REST APIs. The entire app — data loading, algorithm, and UI — lives in one Python file. For an AI course project where the focus is the algorithm, this saves enormous development time while still producing a polished result.

**Q40: How would you scale this to millions of books?**
> A: (1) Pre-filter by genre before running BFS (reduce n), (2) Use database indexing instead of CSV, (3) Parallelize heuristic computation, (4) Use approximate nearest neighbor algorithms, (5) Cache frequent genre query results.

**Q41: Can you explain the `_extract_first_genre` function?**
> A: It handles multiple genre string formats: (1) Python list strings `"['Fantasy', 'Young Adult']"` → uses `ast.literal_eval` to parse and takes the first element. (2) Comma/pipe/slash separated strings → splits and takes the first. (3) Plain strings → returns as-is.

**Q42: What is `unsafe_allow_html=True` and why do you use it?**
> A: Streamlit sanitizes HTML by default for security. `unsafe_allow_html=True` lets us inject raw HTML and CSS. We need it for custom glassmorphism styling, book cards with cover images, and the complete design system that Streamlit's native components can't achieve.

---

## 🎯 One-Liner Summaries for Quick Recall

- **Project:** Book recommender using Best-First Search + heuristic AI on 15,309 Goodreads books
- **Algorithm:** Best-First Search with priority queue, h(n) = 0.6×genre + 0.4×author
- **Architecture:** 3-layer (Presentation → Data + Algorithm → External Services)
- **Tech stack:** Python + Streamlit + Pandas + PriorityQueue + Goodreads/OpenLibrary/Amazon
- **Search modes:** Genre/Author search + Title-based search (both use same BFS core)
- **UI:** Glassmorphism design, dark/light mode, animated cards, real covers, buy links
- **Performance:** O(n log n), < 50ms latency, ~25MB memory
- **Type:** Content-based filtering (not collaborative) — no cold-start problem
- **Key strength:** Interpretable — match % comes directly from heuristic
- **Key limitation:** Binary matching — no fuzzy/semantic similarity
