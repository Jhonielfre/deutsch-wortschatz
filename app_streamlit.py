import streamlit as st
from quiz_core import QuizSession
from database import (
    initialize_database,
    save_quiz_result,
    import_words_from_excel,
    get_connection
)

st.set_page_config(page_title="Deutsch Wortschatz Trainer")

# ---------------------------
# Database Initialization
# ---------------------------

@st.cache_resource
def setup_database():
    initialize_database()

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM words")
    count = cursor.fetchone()[0]
    conn.close()

    if count == 0:
        import_words_from_excel()

setup_database()

# ---------------------------
# Session State Setup
# ---------------------------

if "quiz" not in st.session_state:
    st.session_state.quiz = None

if "current_question" not in st.session_state:
    st.session_state.current_question = None

if "mode" not in st.session_state:
    st.session_state.mode = "home"   # home, asking, feedback, results

# ---------------------------
# Home
# ---------------------------

if st.session_state.mode == "home":

    st.title("Deutsch Wortschatz Trainer")

    if st.button("Start Quiz"):
        st.session_state.quiz = QuizSession()
        st.session_state.current_question = (
            st.session_state.quiz.generate_question()
        )
        st.session_state.mode = "asking"
        st.rerun()

# ---------------------------
# Asking Mode
# ---------------------------

elif st.session_state.mode == "asking":

    quiz = st.session_state.quiz
    question = st.session_state.current_question

    if question is None:
        st.session_state.mode = "results"
        st.rerun()

    st.subheader(question["question_text"])

    if question["options"]:
        user_answer = st.radio(
            "Choose an option:",
            question["options"],
            key="answer_input"
        )
    else:
        user_answer = st.text_input(
            "Your answer:",
            key="answer_input"
        )

    if st.button("Submit"):

        is_correct, correct = quiz.submit_answer(user_answer)

        st.session_state.feedback = {
            "is_correct": is_correct,
            "correct": correct
        }

        st.session_state.mode = "feedback"
        st.rerun()

# ---------------------------
# Feedback Mode
# ---------------------------

elif st.session_state.mode == "feedback":

    quiz = st.session_state.quiz
    feedback = st.session_state.feedback

    if feedback["is_correct"]:
        st.success("Correct!")
    else:
        st.error(f"Incorrect. Correct answer: {feedback['correct']}")

    st.write(f"Score: {quiz.score} / {quiz.num_questions}")

    if st.button("Next Question"):

        next_q = quiz.generate_question()

        if next_q is None:
            st.session_state.mode = "results"
        else:
            st.session_state.current_question = next_q
            st.session_state.mode = "asking"

        st.session_state.answer_input = ""
        st.rerun()

# ---------------------------
# Results
# ---------------------------

elif st.session_state.mode == "results":

    quiz = st.session_state.quiz
    percentage = (quiz.score / quiz.num_questions) * 100

    save_quiz_result(quiz.score, quiz.num_questions)

    st.title("Quiz Finished")
    st.write(f"Final Score: {quiz.score}/{quiz.num_questions}")
    st.write(f"Percentage: {percentage:.1f}%")

    if st.button("Back to Home"):
        st.session_state.mode = "home"
        st.session_state.quiz = None
        st.session_state.current_question = None
        st.rerun()
