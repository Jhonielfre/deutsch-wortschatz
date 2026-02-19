# CustomTkinter for modern themed GUI
import customtkinter as ctk

# Core quiz logic (question generation + evaluation)
from quiz_core import QuizSession

# Vocabulary updater (calls OpenAI enrichment)
from data_manager import update_vocabulary

# Statistics and graphs
from score_tracker import show_statistics, show_performance_graph


# Set system appearance (light/dark based on OS)
ctk.set_appearance_mode("System")

# Set default color theme
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    """
    Main GUI application class.
    Inherits from CTk (CustomTkinter main window).
    """

    def __init__(self):
        super().__init__()  # Initialize parent window

        # Window title
        self.title("Deutsch Wortschatz Trainer")

        # Window size
        self.geometry("600x500")

        # Container frame to dynamically swap screens
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)

        # Start with main menu
        self.show_main_menu()

    # ---------------------------------------------------------
    # Utility: Clear current screen
    # ---------------------------------------------------------

    def clear_container(self):
        """
        Removes all widgets from the container frame.
        Used when switching screens.
        """
        for widget in self.container.winfo_children():
            widget.destroy()

    # ---------------------------------------------------------
    # Main Menu Screen
    # ---------------------------------------------------------

    def show_main_menu(self):
        """
        Displays the main menu with navigation buttons.
        """
        self.clear_container()

        # Title label
        title = ctk.CTkLabel(
            self.container,
            text="Deutsch Wortschatz Trainer",
            font=("Arial", 24)
        )
        title.pack(pady=30)

        # Start quiz button
        ctk.CTkButton(
            self.container,
            text="Start Quiz",
            command=self.start_quiz
        ).pack(pady=10)

        # Update vocabulary (calls OpenAI enrichment)
        ctk.CTkButton(
            self.container,
            text="Update Vocabulary",
            command=update_vocabulary
        ).pack(pady=10)

        # Show text statistics
        ctk.CTkButton(
            self.container,
            text="Show Statistics",
            command=show_statistics
        ).pack(pady=10)

        # Show performance graph
        ctk.CTkButton(
            self.container,
            text="Show Performance Graph",
            command=show_performance_graph
        ).pack(pady=10)

    # ---------------------------------------------------------
    # Quiz Flow
    # ---------------------------------------------------------

    def start_quiz(self):
        """
        Creates a new quiz session.
        """
        self.quiz = QuizSession()
        self.show_question()

    def show_question(self):
        """
        Displays current question.
        If quiz finished → show results.
        """
        self.clear_container()

        question_data = self.quiz.generate_question()

        if question_data is None:
            self.show_results()
            return

        # Question text label
        self.question_label = ctk.CTkLabel(
            self.container,
            text=question_data["question_text"],
            font=("Arial", 18),
            wraplength=500
        )
        self.question_label.pack(pady=30)

        # Feedback label (Correct / Incorrect)
        self.feedback_label = ctk.CTkLabel(
            self.container,
            text="",
            font=("Arial", 16)
        )
        self.feedback_label.pack(pady=10)

        # -----------------------------------------------------
        # Multiple choice vs text entry
        # -----------------------------------------------------

        if question_data["options"]:
            # Multiple choice buttons
            self.option_buttons = []

            for option in question_data["options"]:
                btn = ctk.CTkButton(
                    self.container,
                    text=option,
                    command=lambda opt=option: self.submit_answer(opt)
                )
                btn.pack(pady=5)
                self.option_buttons.append(btn)

        else:
            # Free text answer
            self.answer_entry = ctk.CTkEntry(self.container, width=300)
            self.answer_entry.pack(pady=10)

            # Bind Enter key to submit
            self.answer_entry.bind(
                "<Return>",
                lambda event: self.submit_answer(self.answer_entry.get())
            )

            submit_btn = ctk.CTkButton(
                self.container,
                text="Submit",
                command=lambda: self.submit_answer(self.answer_entry.get())
            )
            submit_btn.pack(pady=10)

        # Progress indicator
        self.progress_label = ctk.CTkLabel(
            self.container,
            text=f"Question {self.quiz.current_index + 1} / {self.quiz.num_questions}"
        )
        self.progress_label.pack(pady=20)

    def submit_answer(self, answer):
        """
        Sends answer to quiz engine and displays feedback.
        """

        is_correct, correct = self.quiz.submit_answer(answer)

        if is_correct:
            self.feedback_label.configure(
                text="✅ Correct!",
                text_color="green"
            )
        else:
            self.feedback_label.configure(
                text=f"❌ Incorrect! Correct answer: {correct}",
                text_color="red"
            )

        # Wait 1.5 seconds before next question
        self.after(1500, self.show_question)

    # ---------------------------------------------------------
    # Results Screen
    # ---------------------------------------------------------

    def show_results(self):
        """
        Displays final quiz score.
        """
        self.clear_container()

        percentage = (self.quiz.score / self.quiz.num_questions) * 100

        # Import locally to avoid circular dependency
        from score_tracker import save_score
        save_score(self.quiz.score, self.quiz.num_questions)

        result_label = ctk.CTkLabel(
            self.container,
            text=f"Final Score: {self.quiz.score}/{self.quiz.num_questions}\n({percentage:.0f}%)",
            font=("Arial", 22)
        )
        result_label.pack(pady=30)

        ctk.CTkButton(
            self.container,
            text="Back to Main Menu",
            command=self.show_main_menu
        ).pack(pady=20)


# Run app only if file executed directly
if __name__ == "__main__":
    app = App()
    app.mainloop()