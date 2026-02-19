import pandas as pd        # Data handling (Excel file)
import random              # Random question selection
import json                # Load word statistics
import os                  # File existence checks

FILE_PATH = "lista_palabras.xlsx"     # Excel vocabulary file
WORD_STATS_FILE = "word_stats.json"   # Per-word performance tracking


class QuizSession:
    """
    Core engine of the GUI quiz.
    Responsible for:
        - Loading words
        - Applying weighted sampling
        - Generating different question types
        - Evaluating answers
        - Tracking score
    """

    def __init__(self, num_questions=10):
        """
        Initializes a quiz session.

        Parameters:
            num_questions (int): number of questions in this session
        """

        self.num_questions = num_questions
        self.score = 0                     # Correct answers counter
        self.current_index = 0             # Tracks current question number

        # Load vocabulary file
        df = pd.read_excel(FILE_PATH)

        # Only use words that have a translation filled in
        df = df[df["translation"].notna() & (df["translation"].str.strip() != "")]

        # Select weighted sample of words
        self.questions_df = self.get_weighted_sample(df, num_questions)

        # Holds current question data structure
        self.current_question_data = None

    # ---------------------------------------------------------
    # Weighted Sampling Logic
    # ---------------------------------------------------------

    def get_weighted_sample(self, df, n):
        """
        Returns n words sampled with adaptive weighting.

        Words with lower accuracy get higher probability.
        """

        # If no stats file exists yet → simple random sample
        if not os.path.exists(WORD_STATS_FILE):
            return df.sample(n)

        # Load word statistics
        with open(WORD_STATS_FILE, "r") as f:
            stats = json.load(f)

        weights = []

        # Assign weight to each word
        for _, row in df.iterrows():
            word = row["word"]

            if word not in stats:
                weight = 3  # New words get high priority
            else:
                asked = stats[word]["asked"]
                correct = stats[word]["correct"]

                if asked == 0:
                    weight = 3
                else:
                    accuracy = correct / asked

                    if accuracy < 0.6:
                        weight = 3      # Weak word
                    elif accuracy < 0.8:
                        weight = 2      # Medium
                    else:
                        weight = 1      # Strong word

            weights.append(weight)

        # Convert weights to probabilities
        total = sum(weights)
        probabilities = [w / total for w in weights]

        # Weighted random selection
        sampled_indices = random.choices(
            population=df.index.tolist(),
            weights=probabilities,
            k=n
        )

        return df.loc[sampled_indices]

    # ---------------------------------------------------------
    # Question Generation
    # ---------------------------------------------------------

    def generate_question(self):
        """
        Creates a question dictionary for the GUI.
        Returns None if quiz is finished.
        """

        if self.current_index >= self.num_questions:
            return None

        row = self.questions_df.iloc[self.current_index]

        word = row["word"]
        translation = row["translation"]
        word_type = row["type"]
        genre = row["genre"]
        conjugation = row["conjugation"]
        example = row["example"]

        # Base question types
        question_types = ["de_es", "es_de", "sentence"]

        # Add gender question for nouns
        if word_type == "noun" and pd.notna(genre):
            question_types.append("gender")

        # Add conjugation question for verbs
        if word_type == "verb" and pd.notna(conjugation):
            question_types.append("conjugation")

        question_type = random.choice(question_types)

        question_data = {
            "type": question_type,
            "word": word,
            "correct": None,
            "question_text": "",
            "options": None
        }

        # -------------------------
        # Question Type Logic
        # -------------------------

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
            # Replace correct word with blank
            sentence = example.replace(word, "_____")
            question_data["question_text"] = sentence
            question_data["correct"] = word

            # Choose distractors from different word types
            different_type = self.questions_df[
                (self.questions_df["type"] != row["type"]) &
                (self.questions_df["word"] != word)
            ]["word"]

            if len(different_type) >= 3:
                distractors = different_type.sample(3).tolist()
            else:
                distractors = self.questions_df[
                    self.questions_df["word"] != word
                ]["word"].sample(min(3, len(self.questions_df)-1)).tolist()

            options = distractors + [word]
            random.shuffle(options)

            question_data["options"] = options

        self.current_question_data = question_data
        return question_data

    # ---------------------------------------------------------
    # Answer Evaluation
    # ---------------------------------------------------------

    def submit_answer(self, answer):
        """
        Evaluates user input.
        Returns:
            (is_correct: bool, correct_answer: str)
        """

        question_type = self.current_question_data["type"]
        correct = self.current_question_data["correct"]

        valid_answers = []

        # Translation question allows synonyms
        if question_type == "de_es":
            row = self.questions_df.iloc[self.current_index]
            translation = row["translation"]
            synonyms = row.get("synonyms", "")

            valid_answers.append(translation)

            if pd.notna(synonyms) and str(synonyms).strip() != "":
                synonym_list = [s.strip() for s in synonyms.split(";")]
                valid_answers.extend(synonym_list)
        else:
            valid_answers.append(correct)

        # Normalize for case and whitespace
        valid_answers = [v.strip().lower() for v in valid_answers]

        is_correct = answer.strip().lower() in valid_answers

        if is_correct:
            self.score += 1

        self.current_index += 1

        return is_correct, correct