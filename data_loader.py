"""
data_loader.py
--------------
Handles loading and preprocessing of the GoodReads_100k_books.csv dataset.
Falls back to a built-in sample dataset if the CSV is not found.
"""

import os
import pandas as pd

# ---------------------------------------------------------------------------
# Fallback sample dataset (~50 well-known books)
# ---------------------------------------------------------------------------
SAMPLE_BOOKS = [
    {"Title": "Harry Potter and the Sorcerer's Stone", "Author": "J.K. Rowling", "Genre": "Fantasy", "Rating": 4.47, "Description": "A young boy discovers he is a wizard and attends Hogwarts School of Witchcraft and Wizardry."},
    {"Title": "Harry Potter and the Chamber of Secrets", "Author": "J.K. Rowling", "Genre": "Fantasy", "Rating": 4.43, "Description": "Harry Potter's second year at Hogwarts is marked by ominous events."},
    {"Title": "Harry Potter and the Prisoner of Azkaban", "Author": "J.K. Rowling", "Genre": "Fantasy", "Rating": 4.57, "Description": "Harry Potter learns more about his past as a dangerous prisoner escapes from Azkaban."},
    {"Title": "Harry Potter and the Goblet of Fire", "Author": "J.K. Rowling", "Genre": "Fantasy", "Rating": 4.56, "Description": "Harry Potter is mysteriously entered into the Triwizard Tournament."},
    {"Title": "The Hobbit", "Author": "J.R.R. Tolkien", "Genre": "Fantasy", "Rating": 4.28, "Description": "Bilbo Baggins is swept into an epic quest to reclaim the Lonely Mountain from the dragon Smaug."},
    {"Title": "The Lord of the Rings", "Author": "J.R.R. Tolkien", "Genre": "Fantasy", "Rating": 4.50, "Description": "A meek hobbit and eight companions set out on a journey to destroy the One Ring."},
    {"Title": "The Fellowship of the Ring", "Author": "J.R.R. Tolkien", "Genre": "Fantasy", "Rating": 4.36, "Description": "The first part of Tolkien's epic tale of the One Ring."},
    {"Title": "A Game of Thrones", "Author": "George R.R. Martin", "Genre": "Fantasy", "Rating": 4.44, "Description": "Noble families fight for control of the Iron Throne of the Seven Kingdoms."},
    {"Title": "A Clash of Kings", "Author": "George R.R. Martin", "Genre": "Fantasy", "Rating": 4.41, "Description": "The Seven Kingdoms are torn apart as five kings claim the Iron Throne."},
    {"Title": "The Name of the Wind", "Author": "Patrick Rothfuss", "Genre": "Fantasy", "Rating": 4.55, "Description": "The chronicle of the magically gifted young man who grows to be the most notorious wizard his world has ever seen."},
    {"Title": "Mistborn: The Final Empire", "Author": "Brandon Sanderson", "Genre": "Fantasy", "Rating": 4.46, "Description": "A world where ash falls from the sky and mists dominate the night has been conquered by a dark lord."},
    {"Title": "The Way of Kings", "Author": "Brandon Sanderson", "Genre": "Fantasy", "Rating": 4.64, "Description": "An epic fantasy set in the world of Roshar, where highstorms and Shardblades rule."},
    {"Title": "Eragon", "Author": "Christopher Paolini", "Genre": "Fantasy", "Rating": 3.97, "Description": "A farm boy finds a mysterious stone which turns out to be a dragon egg."},
    {"Title": "The Alchemist", "Author": "Paulo Coelho", "Genre": "Fiction", "Rating": 3.88, "Description": "A young shepherd journeys to the Egyptian pyramids following a recurring dream."},
    {"Title": "To Kill a Mockingbird", "Author": "Harper Lee", "Genre": "Fiction", "Rating": 4.28, "Description": "A lawyer in the Deep South defends a Black man accused of a crime."},
    {"Title": "1984", "Author": "George Orwell", "Genre": "Science Fiction", "Rating": 4.19, "Description": "A dystopian social science fiction novel set in a totalitarian society called Oceania."},
    {"Title": "Brave New World", "Author": "Aldous Huxley", "Genre": "Science Fiction", "Rating": 3.99, "Description": "A futuristic World State where citizens are environmentally engineered into intelligence-based social hierarchy."},
    {"Title": "Fahrenheit 451", "Author": "Ray Bradbury", "Genre": "Science Fiction", "Rating": 3.97, "Description": "In a future American society where books are outlawed and burned by firemen."},
    {"Title": "The Martian", "Author": "Andy Weir", "Genre": "Science Fiction", "Rating": 4.40, "Description": "An astronaut must survive alone on Mars after being presumed dead and left behind."},
    {"Title": "Dune", "Author": "Frank Herbert", "Genre": "Science Fiction", "Rating": 4.25, "Description": "Set in the distant future amidst a feudal interstellar society, a boy becomes a desert warrior."},
    {"Title": "Ender's Game", "Author": "Orson Scott Card", "Genre": "Science Fiction", "Rating": 4.30, "Description": "A young prodigy is trained to be Earth's greatest military leader to fight an alien race."},
    {"Title": "The Hitchhiker's Guide to the Galaxy", "Author": "Douglas Adams", "Genre": "Science Fiction", "Rating": 4.22, "Description": "Moments before Earth is demolished for a hyperspace bypass, Arthur Dent is swept off his feet."},
    {"Title": "The Da Vinci Code", "Author": "Dan Brown", "Genre": "Thriller", "Rating": 3.67, "Description": "A Harvard professor becomes entangled in secrets of symbols while investigating a murder."},
    {"Title": "Gone Girl", "Author": "Gillian Flynn", "Genre": "Thriller", "Rating": 3.86, "Description": "On a couple's fifth wedding anniversary, the wife mysteriously disappears."},
    {"Title": "The Girl with the Dragon Tattoo", "Author": "Stieg Larsson", "Genre": "Thriller", "Rating": 4.15, "Description": "A journalist and a hacker investigate the disappearance of a woman from a wealthy family."},
    {"Title": "Murder on the Orient Express", "Author": "Agatha Christie", "Genre": "Mystery", "Rating": 4.15, "Description": "Hercule Poirot investigates a murder on the famous train."},
    {"Title": "And Then There Were None", "Author": "Agatha Christie", "Genre": "Mystery", "Rating": 4.27, "Description": "Ten strangers are invited to an island and killed one by one."},
    {"Title": "The Sherlock Holmes Collection", "Author": "Arthur Conan Doyle", "Genre": "Mystery", "Rating": 4.50, "Description": "The complete adventures of the world's most famous detective."},
    {"Title": "The Hunger Games", "Author": "Suzanne Collins", "Genre": "Dystopian", "Rating": 4.34, "Description": "In a dystopian future, a young girl takes her sister's place in a televised death match."},
    {"Title": "Catching Fire", "Author": "Suzanne Collins", "Genre": "Dystopian", "Rating": 4.30, "Description": "The second book in the Hunger Games trilogy, following Katniss as a symbol of revolution."},
    {"Title": "Mockingjay", "Author": "Suzanne Collins", "Genre": "Dystopian", "Rating": 4.03, "Description": "The final battle against the Capitol begins as Katniss becomes the Mockingjay."},
    {"Title": "Divergent", "Author": "Veronica Roth", "Genre": "Dystopian", "Rating": 4.10, "Description": "In a dystopian Chicago, society is divided into five factions based on virtues."},
    {"Title": "The Maze Runner", "Author": "James Dashner", "Genre": "Dystopian", "Rating": 4.02, "Description": "A boy arrives in a community of boys who have no memory of the outside world."},
    {"Title": "Pride and Prejudice", "Author": "Jane Austen", "Genre": "Romance", "Rating": 4.28, "Description": "Elizabeth Bennet navigates issues of manners, morality, marriage and love in Georgian England."},
    {"Title": "Sense and Sensibility", "Author": "Jane Austen", "Genre": "Romance", "Rating": 4.08, "Description": "Two sisters navigate love and heartbreak in Regency-era England."},
    {"Title": "Wuthering Heights", "Author": "Emily Brontë", "Genre": "Romance", "Rating": 3.86, "Description": "A brooding tale of passionate love and revenge set on the Yorkshire moors."},
    {"Title": "The Great Gatsby", "Author": "F. Scott Fitzgerald", "Genre": "Fiction", "Rating": 3.93, "Description": "A portrait of the Jazz Age in all of its decadence and excess."},
    {"Title": "Of Mice and Men", "Author": "John Steinbeck", "Genre": "Fiction", "Rating": 3.88, "Description": "Two displaced migrant ranch workers move from place to place trying to find work."},
    {"Title": "Sapiens: A Brief History of Humankind", "Author": "Yuval Noah Harari", "Genre": "Non-Fiction", "Rating": 4.40, "Description": "A brief history of humankind exploring how biology and history defined us."},
    {"Title": "Atomic Habits", "Author": "James Clear", "Genre": "Non-Fiction", "Rating": 4.38, "Description": "A practical guide to building good habits and breaking bad ones."},
    {"Title": "Thinking, Fast and Slow", "Author": "Daniel Kahneman", "Genre": "Non-Fiction", "Rating": 4.18, "Description": "Explores the two systems that drive the way we think."},
    {"Title": "The Power of Now", "Author": "Eckhart Tolle", "Genre": "Self-Help", "Rating": 4.13, "Description": "A guide to spiritual enlightenment exploring the importance of living in the present moment."},
    {"Title": "Rich Dad Poor Dad", "Author": "Robert T. Kiyosaki", "Genre": "Self-Help", "Rating": 4.08, "Description": "What the rich teach their kids about money that the poor and middle class do not."},
    {"Title": "The Subtle Art of Not Giving a F*ck", "Author": "Mark Manson", "Genre": "Self-Help", "Rating": 3.90, "Description": "A counterintuitive approach to living a good life."},
    {"Title": "The Chronicles of Narnia", "Author": "C.S. Lewis", "Genre": "Fantasy", "Rating": 4.24, "Description": "Seven high fantasy novels set in the world of Narnia ruled by the lion Aslan."},
    {"Title": "Percy Jackson and the Olympians", "Author": "Rick Riordan", "Genre": "Fantasy", "Rating": 4.33, "Description": "A young boy discovers he is the son of a Greek god and embarks on epic quests."},
    {"Title": "The Lightning Thief", "Author": "Rick Riordan", "Genre": "Fantasy", "Rating": 4.25, "Description": "Percy Jackson, a troubled twelve-year-old, embarks on a quest across the United States."},
    {"Title": "Dracula", "Author": "Bram Stoker", "Genre": "Horror", "Rating": 3.98, "Description": "Count Dracula's attempt to move from Transylvania to England so he can find new blood."},
    {"Title": "Frankenstein", "Author": "Mary Shelley", "Genre": "Horror", "Rating": 3.82, "Description": "A young scientist creates a sapient creature in an unorthodox scientific experiment."},
    {"Title": "It", "Author": "Stephen King", "Genre": "Horror", "Rating": 4.24, "Description": "A group of children find themselves battling an evil supernatural entity called Pennywise."},
]


def _extract_first_genre(genre_str: str) -> str:
    """Return the first genre from a comma/pipe/slash-separated string."""
    if not isinstance(genre_str, str):
        return ""
    for sep in [",", "|", "/"]:
        if sep in genre_str:
            return genre_str.split(sep)[0].strip()
    return genre_str.strip()


def load_dataset(csv_path: str = "GoodReads_100k_books.csv", max_rows: int = 20000) -> pd.DataFrame:
    """
    Load and preprocess the GoodReads dataset.

    Priority:
      1. Local CSV file (csv_path)
      2. Built-in sample dataset

    Returns a cleaned DataFrame with columns:
      Title, Author, Genre, Rating, Description
    """

    # ---- Try loading the CSV ----
    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path, on_bad_lines="skip", low_memory=False)

            # Possible column name variants in the wild for this dataset
            col_map = {}
            lower_cols = {c.lower(): c for c in df.columns}

            for target, candidates in {
                "Title":       ["title", "book_title", "name"],
                "Author":      ["author", "authors", "book_author"],
                "Genre":       ["genre", "genres", "categories", "shelves"],
                "Rating":      ["rating", "average_rating", "avg_rating", "book_average_rating"],
                "Description": ["desc", "description", "synopsis", "summary", "book_desc"],
            }.items():
                for cand in candidates:
                    if cand in lower_cols:
                        col_map[lower_cols[cand]] = target
                        break

            df = df.rename(columns=col_map)

            # Keep only the five required columns that we managed to map
            available = [c for c in ["Title", "Author", "Genre", "Rating", "Description"] if c in df.columns]
            df = df[available].dropna(subset=available)

            # Ensure Rating is numeric
            if "Rating" in df.columns:
                df["Rating"] = pd.to_numeric(df["Rating"], errors="coerce")
                df = df.dropna(subset=["Rating"])
                df = df[df["Rating"] >= 3.0]

            # First genre only
            if "Genre" in df.columns:
                df["Genre"] = df["Genre"].apply(_extract_first_genre)
                df = df[df["Genre"].str.strip() != ""]

            # Limit rows for performance
            if len(df) > max_rows:
                df = df.sample(n=max_rows, random_state=42)

            df = df.reset_index(drop=True)

            if len(df) > 0:
                return df

        except Exception as exc:
            print(f"[data_loader] Could not read CSV ({exc}). Falling back to sample data.")

    # ---- Fallback: built-in sample ----
    print("[data_loader] Using built-in sample dataset (50 books).")
    df = pd.DataFrame(SAMPLE_BOOKS)
    df["Genre"] = df["Genre"].apply(_extract_first_genre)
    df = df.reset_index(drop=True)
    return df
