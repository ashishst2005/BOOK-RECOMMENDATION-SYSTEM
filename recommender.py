"""
recommender.py
--------------
Best-First Search recommendation engine.

Heuristic:
  h(n) = 0.6 × genre_match + 0.4 × author_match

Priority queue stores (-score, index, book_dict) to avoid
Pandas Series comparison errors (ValueError: truth value is ambiguous).
"""

from __future__ import annotations

import queue
from typing import Optional

import pandas as pd


# ---------------------------------------------------------------------------
# Heuristic
# ---------------------------------------------------------------------------

def _genre_match(book_genre: str, preferred_genre: str) -> float:
    """Return 1.0 if preferred_genre appears (case-insensitive) in book_genre, else 0.0."""
    if not preferred_genre.strip():
        return 0.0
    return 1.0 if preferred_genre.strip().lower() in str(book_genre).lower() else 0.0


def _author_match(book_author: str, preferred_author: str) -> float:
    """Return 1.0 if preferred_author appears (case-insensitive) in book_author, else 0.0."""
    if not preferred_author.strip():
        return 0.0
    return 1.0 if preferred_author.strip().lower() in str(book_author).lower() else 0.0


def heuristic(book_genre: str, book_author: str, preferred_genre: str, preferred_author: str) -> float:
    """
    f(n) = h(n) = 0.6 × genre_match + 0.4 × author_match

    Returns a float in [0.0, 1.0].
    """
    g = _genre_match(book_genre, preferred_genre)
    a = _author_match(book_author, preferred_author)
    return round(0.6 * g + 0.4 * a, 4)


# ---------------------------------------------------------------------------
# Best-First Search
# ---------------------------------------------------------------------------

def best_first_search(
    df: pd.DataFrame,
    preferred_genre: str,
    preferred_author: str,
    top_n: int = 10,
) -> pd.DataFrame:
    """
    Implements Best-First Search over the book dataset.

    Each book is a node; priority is determined by -h(n) so that
    the highest-scoring books are explored first.

    The priority queue stores (neg_score, row_index, book_dict) tuples.
    Storing a plain Python dict (not a Pandas Series/row) prevents the
    'truth value of a Series is ambiguous' ValueError.

    Returns a DataFrame of the top_n results sorted by score descending.
    """
    pq: queue.PriorityQueue = queue.PriorityQueue()

    # Enqueue every book as a node
    for idx, row in df.iterrows():
        book_dict = {
            "Title":       str(row.get("Title", "")),
            "Author":      str(row.get("Author", "")),
            "Genre":       str(row.get("Genre", "")),
            "Rating":      row.get("Rating", 0.0),
            "ISBN":        str(row.get("ISBN", "")),
            "Description": str(row.get("Description", "")),
        }
        score = heuristic(
            book_dict["Genre"],
            book_dict["Author"],
            preferred_genre,
            preferred_author,
        )
        # Store (-score, idx, book_dict) — Python compares tuples left-to-right,
        # so tie-breaking uses 'idx' (int), never the dict, which is safe.
        pq.put((-score, idx, book_dict))

    results = []
    seen_titles: set[str] = set()

    while not pq.empty() and len(results) < top_n:
        neg_score, _, book_dict = pq.get()
        score = -neg_score
        title_key = book_dict["Title"].lower()

        if title_key not in seen_titles and score > 0.0:
            seen_titles.add(title_key)
            book_dict["Score"] = score
            results.append(book_dict)

    if not results:
        return pd.DataFrame()

    result_df = pd.DataFrame(results)
    result_df = result_df.sort_values("Score", ascending=False).reset_index(drop=True)
    return result_df


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def recommend_by_genre_author(
    df: pd.DataFrame,
    preferred_genre: str,
    preferred_author: str,
    top_n: int = 10,
) -> tuple[Optional[dict], pd.DataFrame]:
    """
    Recommend books based on preferred genre and/or author.

    Returns:
        top_book  – dict of the best match (or None if no results)
        similar   – DataFrame of next (top_n - 1) similar books
    """
    results = best_first_search(df, preferred_genre, preferred_author, top_n=top_n)

    if results.empty:
        return None, pd.DataFrame()

    top_book = results.iloc[0].to_dict()
    similar  = results.iloc[1:].reset_index(drop=True) if len(results) > 1 else pd.DataFrame()
    return top_book, similar


def recommend_by_title(
    df: pd.DataFrame,
    title_query: str,
    top_n: int = 10,
) -> tuple[Optional[dict], Optional[dict], pd.DataFrame]:
    """
    Find a book by title, then recommend similar books based on its genre & author.

    Returns:
        found_book – dict of the matched source book (or None)
        top_book   – dict of the best recommended book (excluding source, or None)
        similar    – DataFrame of additional recommendations
    """
    mask = df["Title"].str.lower().str.contains(title_query.strip().lower(), na=False)
    matches = df[mask]

    if matches.empty:
        return None, None, pd.DataFrame()

    # Pick the highest-rated matching book as the source
    if "Rating" in matches.columns:
        source_row = matches.sort_values("Rating", ascending=False).iloc[0]
    else:
        source_row = matches.iloc[0]

    found_book = {
        "Title":       str(source_row.get("Title", "")),
        "Author":      str(source_row.get("Author", "")),
        "Genre":       str(source_row.get("Genre", "")),
        "Rating":      source_row.get("Rating", 0.0),
        "ISBN":        str(source_row.get("ISBN", "")),
        "Description": str(source_row.get("Description", "")),
    }

    preferred_genre  = found_book["Genre"]
    preferred_author = found_book["Author"]

    # Exclude the source book from recommendations
    filtered_df = df[~mask].reset_index(drop=True)
    results = best_first_search(filtered_df, preferred_genre, preferred_author, top_n=top_n)

    if results.empty:
        return found_book, None, pd.DataFrame()

    top_book = results.iloc[0].to_dict()
    similar  = results.iloc[1:].reset_index(drop=True) if len(results) > 1 else pd.DataFrame()
    return found_book, top_book, similar
