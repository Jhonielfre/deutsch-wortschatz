import sqlite3
from datetime import datetime
import pandas as pd

DB_NAME = "database.db"

def get_connection():
    return sqlite3.connect(DB_NAME)


def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()

    # Create words table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word TEXT UNIQUE,
            type TEXT,
            genre TEXT,
            conjugation TEXT,
            translation TEXT,
            synonyms TEXT,
            example TEXT
        )
    """)

    # Create word stats table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS word_stats (
            word_id INTEGER,
            asked INTEGER DEFAULT 0,
            correct INTEGER DEFAULT 0,
            last_seen TEXT,
            FOREIGN KEY(word_id) REFERENCES words(id)
        )
    """)

    # Create quiz history table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quiz_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            score INTEGER,
            total INTEGER,
            percentage REAL
        )
    """)

    conn.commit()
    conn.close()


def save_quiz_result(score, total):
    conn = get_connection()
    cursor = conn.cursor()

    percentage = round((score / total) * 100, 2)

    cursor.execute("""
        INSERT INTO quiz_history (date, score, total, percentage)
        VALUES (?, ?, ?, ?)
    """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), score, total, percentage))

    conn.commit()
    conn.close()


def import_words_from_excel(file_path="lista_palabras.xlsx"):
    conn = get_connection()
    cursor = conn.cursor()

    df = pd.read_excel(file_path)

    # Normalize column names
    df.columns = df.columns.str.strip().str.lower()

    required_columns = [
        "word", "type", "genre",
        "conjugation", "translation",
        "synonyms", "example"
    ]

    for col in required_columns:
        if col not in df.columns:
            df[col] = None

    for _, row in df.iterrows():
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO words
                (word, type, genre, conjugation, translation, synonyms, example)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                row["word"],
                row["type"],
                row["genre"],
                row["conjugation"],
                row["translation"],
                row["synonyms"],
                row["example"]
            ))
        except Exception as e:
            print(f"Error inserting word {row['word']}: {e}")

    conn.commit()
    conn.close()

def get_all_words():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM words WHERE translation IS NOT NULL AND translation != ''")
    rows = cursor.fetchall()

    conn.close()
    return rows


def get_word_stats(word_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT asked, correct FROM word_stats WHERE word_id = ?
    """, (word_id,))
    result = cursor.fetchone()

    conn.close()

    if result:
        return result
    return (0, 0)


def update_word_stats(word_id, is_correct):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT asked, correct FROM word_stats WHERE word_id = ?
    """, (word_id,))
    result = cursor.fetchone()

    if result:
        asked, correct = result
        asked += 1
        if is_correct:
            correct += 1

        cursor.execute("""
            UPDATE word_stats
            SET asked = ?, correct = ?, last_seen = CURRENT_TIMESTAMP
            WHERE word_id = ?
        """, (asked, correct, word_id))
    else:
        cursor.execute("""
            INSERT INTO word_stats (word_id, asked, correct, last_seen)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        """, (word_id, 1, 1 if is_correct else 0))

    conn.commit()
    conn.close()