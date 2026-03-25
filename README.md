# Smart Book Recommender

A heuristic-based book recommendation system built with Python and Streamlit. Uses a **Best-First Search** algorithm to find books that match your preferred genre and author.

---

## Features

- **Genre & Author Search** — Select a genre from a dropdown and optionally type an author name. Results are ranked by a weighted heuristic (60% genre match + 40% author match).
- **Title-Based Search** — Pick a book you like; the system extracts its genre and author to find similar reads.
- **Book Cover Images** — Real cover art fetched from the [Open Library Covers API](https://openlibrary.org/dev/docs/api/covers) using ISBNs.
- **Buy Links** — Every recommendation card has a direct link to search the book on Amazon.
- **Dark / Light Mode** — Toggle between a true-black glassmorphism theme and a clean white theme.
- **Export** — Download your recommendations as a CSV file.

## Dataset

The built-in sample includes **115 books** across **14 genres**: Fantasy, Science Fiction, Thriller, Mystery, Dystopian, Romance, Fiction, Horror, Non-Fiction, Self-Help, Historical Fiction, Philosophy, Adventure, and Classics.

If you have a `GoodReads_100k_books.csv` file in the project directory, the app will use it instead (up to 20,000 rows).

---

## Quick Start

### Prerequisites

- Python 3.9+
- pip

### Install & Run

```bash
# Clone / navigate to the project
cd BOOK-RECOMMENDATION-SYSTEM

# Install dependencies
pip install streamlit pandas

# Run the app
streamlit run app.py
```

The app opens at **http://localhost:8501**.

---

## Project Structure

```
BOOK-RECOMMENDATION-SYSTEM/
├── app.py            # Streamlit UI, styling, and render logic
├── data_loader.py    # Dataset loading (CSV or built-in sample)
├── recommender.py    # Best-First Search algorithm and heuristic
├── README.md         # This file
└── TECH_STACK.md     # Tech stack choices and rationale
```

## How It Works

1. **Data Loading** — `data_loader.py` loads and preprocesses books (title, author, genre, rating, ISBN, description).
2. **Heuristic Scoring** — For each book, the heuristic computes:
   ```
   h(n) = 0.6 × genre_match + 0.4 × author_match
   ```
   where each match is binary (1.0 if the user's input appears in the book's field, 0.0 otherwise).
3. **Best-First Search** — All books are pushed into a priority queue keyed by `-h(n)`. The top-N highest-scoring books are dequeued as recommendations.
4. **Rendering** — Results are displayed as animated glassmorphism cards with cover images, metadata, match scores, and buy links.

---

## Tech Stack

See [TECH_STACK.md](TECH_STACK.md) for a detailed explanation of every technology used and why it was chosen.

| Layer       | Technology                |
|-------------|---------------------------|
| Language    | Python 3                  |
| UI          | Streamlit                 |
| Data        | Pandas                    |
| Algorithm   | Best-First Search (heapq) |
| Cover API   | Open Library Covers API   |
| Buy Links   | Amazon Search URL         |
| Styling     | Custom CSS (glassmorphism)|

---

## License

Academic project — Semester 6, AI Course.