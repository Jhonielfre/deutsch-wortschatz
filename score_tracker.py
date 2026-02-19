import json                         # Read/write JSON files
import os                           # Check if files exist
import matplotlib.pyplot as plt     # Graph plotting
from datetime import datetime       # Timestamp generation


SCORE_FILE = "quiz_history.json"    # Stores quiz session history
WORD_STATS_FILE = "word_stats.json" # Stores per-word statistics


def save_score(score, total):
    """
    Saves quiz result to quiz_history.json.
    """

    percentage = round((score / total) * 100, 2)

    record = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "score": score,
        "total": total,
        "percentage": percentage
    }

    # Load existing history
    if os.path.exists(SCORE_FILE):
        with open(SCORE_FILE, "r") as f:
            history = json.load(f)
    else:
        history = []

    history.append(record)

    # Save updated history
    with open(SCORE_FILE, "w") as f:
        json.dump(history, f, indent=4)

    print("Score saved.")


def show_statistics():
    """
    Displays overall quiz performance statistics.
    """

    if not os.path.exists(SCORE_FILE):
        print("No quiz history yet.")
        return

    with open(SCORE_FILE, "r") as f:
        history = json.load(f)

    total_quizzes = len(history)

    avg_score = sum(item["percentage"] for item in history) / total_quizzes
    best_score = max(item["percentage"] for item in history)
    worst_score = min(item["percentage"] for item in history)

    print("\n--- Quiz Statistics ---")
    print(f"Total quizzes taken: {total_quizzes}")
    print(f"Average score: {avg_score:.2f}%")
    print(f"Best score: {best_score:.2f}%")
    print(f"Worst score: {worst_score:.2f}%")

    print("\nLast 5 Results:")
    for item in history[-5:]:
        print(f"{item['date']} → {item['percentage']}%")

    print()


def update_word_stats(word, is_correct):
    """
    Updates per-word performance statistics.
    """

    if os.path.exists(WORD_STATS_FILE):
        with open(WORD_STATS_FILE, "r") as f:
            stats = json.load(f)
    else:
        stats = {}

    # Initialize word entry if new
    if word not in stats:
        stats[word] = {
            "asked": 0,
            "correct": 0,
            "last_seen": None
        }

    stats[word]["asked"] += 1

    if is_correct:
        stats[word]["correct"] += 1

    stats[word]["last_seen"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(WORD_STATS_FILE, "w") as f:
        json.dump(stats, f, indent=4)


def show_word_statistics():
    """
    Displays performance per individual word.
    """

    if not os.path.exists(WORD_STATS_FILE):
        print("No word statistics yet.")
        return

    with open(WORD_STATS_FILE, "r") as f:
        stats = json.load(f)

    print("\n--- Word Performance ---")

    for word, data in stats.items():
        asked = data["asked"]
        correct = data["correct"]

        accuracy = (correct / asked) * 100 if asked > 0 else 0

        print(f"{word}: {accuracy:.1f}% ({correct}/{asked})")

    print()


def show_performance_graph():
    """
    Plots quiz performance over time.
    """

    if not os.path.exists(SCORE_FILE):
        print("No quiz history yet.")
        return

    with open(SCORE_FILE, "r") as f:
        history = json.load(f)

    if len(history) < 2:
        print("Need at least 2 quizzes to show progress graph.")
        return

    dates = []
    percentages = []

    for item in history:
        date = datetime.strptime(item["date"], "%Y-%m-%d %H:%M:%S")
        dates.append(date)
        percentages.append(item["percentage"])

    plt.figure(figsize=(8, 5))
    plt.plot(dates, percentages, marker="o")

    plt.title("Quiz Performance Over Time")
    plt.xlabel("Date")
    plt.ylabel("Score (%)")
    plt.ylim(0, 100)
    plt.grid(True)

    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()