import pandas as pd                 # Excel file handling
import random                       # Random question selection
from score_tracker import save_score, update_word_stats
import json                         # Read word statistics file
import os                           # File existence checking


FILE_PATH = "lista_palabras.xlsx"   # Vocabulary Excel file
WORD_STATS_FILE = "word_stats.json" # Per-word statistics storage


def get_weighted_sample(df, n=10):
    """
    Returns n words sampled using adaptive weighting.

    Words answered incorrectly more often
    receive higher probability of being selected.
    """

    # If no word statistics exist yet → return random sample
    if not os.path.exists(WORD_STATS_FILE):
        return df.sample(n)

    # Load statistics from JSON file
    with open(WORD_STATS_FILE, "r") as f:
        stats = json.load(f)

    weights = []

    # Assign weight per word
    for _, row in df.iterrows():
        word = row["word"]

        if word not in stats:
            # New word → prioritize
            weight = 3
        else:
            asked = stats[word]["asked"]
            correct = stats[word]["correct"]

            if asked == 0:
                weight = 3
            else:
                accuracy = correct / asked

                # Weak word → high weight
                if accuracy < 0.6:
                    weight = 3
                # Medium → medium weight
                elif accuracy < 0.8:
                    weight = 2
                # Strong → low weight
                else:
                    weight = 1

        weights.append(weight)

    # Convert raw weights to probabilities
    total = sum(weights)
    probabilities = [w / total for w in weights]

    # Weighted random selection
    sampled_indices = random.choices(
        population=df.index.tolist(),
        weights=probabilities,
        k=n
    )

    return df.loc[sampled_indices]


def run_quiz():
    """
    Runs terminal-based quiz version.
    """

    # Load vocabulary
    df = pd.read_excel(FILE_PATH)

    # Only use completed entries (must have translation)
    df = df[df["translation"].notna() & (df["translation"].str.strip() != "")]

    # Ensure enough words exist
    if len(df) < 10:
        print("Need at least 10 completed words.")
        return

    print("\n--- Vocabulary Quiz (10 Questions) ---\n")

    score = 0

    # Select 10 weighted words
    questions = get_weighted_sample(df, 10)

    for _, row in questions.iterrows():

        word = row["word"]
        translation = row["translation"]
        word_type = row["type"]
        genre = row["genre"]
        conjugation = row["conjugation"]
        example = row["example"]

        # Base question types
        question_types = ["de_es", "es_de", "sentence"]

        # Add gender question for nouns
        if word_type == "noun" and pd.notna(genre) and str(genre).strip() != "":
            question_types.append("gender")

        # Add conjugation question for verbs
        if word_type == "verb" and pd.notna(conjugation) and str(conjugation).strip() != "":
            question_types.append("conjugation")

        # Randomly choose question type
        question_type = random.choice(question_types)

        # -----------------------------------------------------
        # Question Logic
        # -----------------------------------------------------

        if question_type == "de_es":
            answer = input(f"Spanish for '{word}': ").strip()
            correct = translation.strip()

        elif question_type == "es_de":
            answer = input(f"German for '{translation}': ").strip()
            correct = word.strip()

        elif question_type == "gender":
            answer = input(
                f"Gender of '{word}'? (masculine/feminine/neuter): "
            ).strip()
            correct = genre.strip()

        elif question_type == "conjugation":
            person = random.choice(["ich", "du", "er/sie/es"])

            answer = input(
                f"Conjugate '{word}' for '{person}': "
            ).strip()

            # Convert conjugation string into dictionary
            # Example string:
            # "ich: gehe, du: gehst, er/sie/es: geht"
            parts = dict(item.split(": ") for item in conjugation.split(", "))
            correct = parts.get(person).strip()

        elif question_type == "sentence":

            # Skip if no example sentence
            if pd.isna(example) or str(example).strip() == "":
                continue

            # Replace correct word with blank
            sentence = example.replace(word, "_____")

            # Select distractor words
            available_words = df[df["word"] != word]["word"]

            num_distractors = min(3, len(available_words))
            distractors = available_words.sample(num_distractors).tolist()

            options = distractors + [word]
            random.shuffle(options)

            print(f"\nFill in the blank:\n{sentence}\n")

            # Display options
            for i, option in enumerate(options):
                print(f"{chr(65+i)}) {option}")

            choice = input("Choose A, B, C, or D: ").strip().upper()

            if choice not in ["A", "B", "C", "D"][: len(options)]:
                print("Invalid choice. Skipping question.\n")
                continue

            selected_word = options[ord(choice) - 65]
            answer = selected_word.strip()
            correct = word.strip()

        # -----------------------------------------------------
        # Answer Evaluation
        # -----------------------------------------------------

        if answer.lower() == correct.lower():
            print("✅ Correct!\n")
            score += 1
            update_word_stats(word, True)
        else:
            print(f"❌ Incorrect. Correct answer: {correct}\n")
            update_word_stats(word, False)

    # -----------------------------------------------------
    # Final Score
    # -----------------------------------------------------

    percentage = (score / 10) * 100
    print(f"Final Score: {score}/10 ({percentage:.0f}%)")

    save_score(score, 10)

    # Offer retry if performance low
    if percentage < 60:
        retry = input("Score below 60%. Retry quiz? (y/n): ").strip().lower()
        if retry == "y":
            run_quiz()