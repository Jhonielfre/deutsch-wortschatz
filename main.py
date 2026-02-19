# Import functions from other modules
from data_manager import update_vocabulary
from quiz_engine import run_quiz
from score_tracker import show_statistics
from score_tracker import show_word_statistics
from score_tracker import show_performance_graph


def main():
    """
    Entry point for terminal-based interaction.
    Displays menu and dispatches user selection
    to the appropriate function.
    """

    print("Choose mode:")
    print("1 - Update vocabulary")
    print("2 - Take quiz")
    print("3 - Show statistics")
    print("4 - Show word statistics")
    print("5 - Show performance graph")

    # Capture user selection
    choice = input("Enter 1, 2, 3, 4 or 5: ")

    # Dispatch pattern (manual router)
    if choice == "1":
        update_vocabulary()
    elif choice == "2":
        run_quiz()
    elif choice == "3":
        show_statistics()
    elif choice == "4":
        show_word_statistics()
    elif choice == "5":
        show_performance_graph()
    else:
        print("Invalid choice.")


# Only execute main() if file is run directly
if __name__ == "__main__":
    main()