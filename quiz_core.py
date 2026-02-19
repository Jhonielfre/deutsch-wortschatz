import random
from database import (
    get_all_words,
    get_word_stats,
    update_word_stats
)


class QuizSession:

    def __init__(self, num_questions=10):
        self.num_questions = num_questions
        self.score = 0
        self.current_index = 0

        self.words = get_all_words()

        if len(self.words) < num_questions:
            raise ValueError("Not enough words in database.")

        self.questions = self.get_weighted_sample(num_questions)
        self.current_question_data = None

    # ---------------------------
    # Weighted Sampling
    # ---------------------------

    def get_weighted_sample(self, n):
        weighted_words = []
        weights = []

        for word_row in self.words:
            word_id = word_row[0]

            asked, correct = get_word_stats(word_id)

            if asked == 0:
                weight = 3
            else:
                accuracy = correct / asked
                if accuracy < 0.6:
                    weight = 3
                elif accuracy < 0.8:
                    weight = 2
                else:
                    weight = 1

            weighted_words.append(word_row)
            weights.append(weight)

        total = sum(weights)
        probabilities = [w / total for w in weights]

        return random.choices(
            population=weighted_words,
            weights=probabilities,
            k=n
        )

    # ---------------------------
    # Question Generation
    # ---------------------------

    def generate_question(self):

        if self.current_index >= self.num_questions:
            return None

        row = self.questions[self.current_index]

        word_id, word, word_type, genre, conjugation, translation, synonyms, example = row

        question_types = ["de_es", "es_de", "sentence"]

        if word_type == "noun" and genre:
            question_types.append("gender")

        if word_type == "verb" and conjugation:
            question_types.append("conjugation")

        question_type = random.choice(question_types)

        question_data = {
            "word_id": word_id,
            "type": question_type,
            "word": word,
            "correct": None,
            "question_text": "",
            "options": None
        }

        if question_type == "de_es":
            question_data["question_text"] = f"Spanish for '{word}'"
            question_data["correct"] = translation

        elif question_type == "es_de":
            question_data["question_text"] = f"German for '{translation}'"
            question_data["correct"] = word

        elif question_type == "gender":
            question_data["question_text"] = f"Gender of '{word}'"
            question_data["correct"] = genre

        elif question_type == "conjugation":
            person = random.choice(["ich", "du", "er/sie/es"])
            parts = dict(item.split(": ") for item in conjugation.split(", "))
            question_data["question_text"] = f"Conjugate '{word}' for '{person}'"
            question_data["correct"] = parts.get(person)

        elif question_type == "sentence":
            sentence = example.replace(word, "_____")
            question_data["question_text"] = sentence
            question_data["correct"] = word

            other_words = [
                w[1] for w in self.words if w[1] != word
            ]

            distractors = random.sample(
                other_words,
                min(3, len(other_words))
            )

            options = distractors + [word]
            random.shuffle(options)

            question_data["options"] = options

        self.current_question_data = question_data
        return question_data

    # ---------------------------
    # Answer Evaluation
    # ---------------------------

    def submit_answer(self, answer):

        question_type = self.current_question_data["type"]
        correct = self.current_question_data["correct"]
        word_id = self.current_question_data["word_id"]

        valid_answers = []

        if question_type == "de_es":
            valid_answers.append(correct)

            synonyms = next(
                (w[6] for w in self.words if w[0] == word_id),
                ""
            )

            if synonyms:
                synonym_list = [s.strip() for s in synonyms.split(";")]
                valid_answers.extend(synonym_list)
        else:
            valid_answers.append(correct)

        valid_answers = [v.strip().lower() for v in valid_answers]

        is_correct = answer.strip().lower() in valid_answers

        if is_correct:
            self.score += 1

        update_word_stats(word_id, is_correct)

        self.current_index += 1

        return is_correct, correct
