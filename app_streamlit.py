import streamlit as st
from quiz_core import QuizSession
from database import (
    initialize_database,
    save_quiz_result,
    import_words_from_excel,
    get_connection
)

# Ensure DB exists
initialize_database()

st.set_page_config(page_title="Deutsch Wortschatz Trainer")

# ---------------------------
# Session State Setup
# ---------------------------

if "page" not in st.session_state:
    st.session_state.page = "home"

if "quiz" not in st.session_state:
    st.session_state.quiz = None

# ---------------------------
# Home Page
# ---------------------------

if st.session_state.page == "home":

    st.title("Deutsch Wortschatz Trainer")

    if st.button("Start Quiz"):
        st.session_state.quiz = QuizSession()
        st.session_state.page = "quiz"
        st.rerun()

# ---------------------------
# Quiz Page
# ---------------------------

elif st.session_state.page == "quiz":

    quiz = st.session_state.quiz

    question = quiz.generate_question()

    if question is None:
        st.session_state.page = "results"
        st.rerun()

    st.subheader(question["question_text"])

    user_answer = None

    if question["options"]:
        user_answer = st.radio(
            "Choose an option:",
            question["options"]
        )
    else:
        user_answer = st.text_input("Your answer:")

    if st.button("Submit"):

        is_correct, correct = quiz.submit_answer(user_answer)

        if is_correct:
            st.success("Correct!")
        else:
            st.error(f"Incorrect. Correct answer: {correct}")

        st.write(f"Score: {quiz.score} / {quiz.num_questions}")

        st.button("Next Question", on_click=lambda: None)

# ---------------------------
# Results Page
# ---------------------------

elif st.session_state.page == "results":

    quiz = st.session_state.quiz

    percentage = (quiz.score / quiz.num_questions) * 100

    save_quiz_result(quiz.score, quiz.num_questions)

    st.title("Quiz Finished")
    st.write(f"Final Score: {quiz.score}/{quiz.num_questions}")
    st.write(f"Percentage: {percentage:.1f}%")

    if st.button("Back to Home"):
        st.session_state.page = "home"
        st.session_state.quiz = None
        st.rerun()
