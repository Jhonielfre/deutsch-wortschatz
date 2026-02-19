import pandas as pd
from ai_enrichment import get_word_info

FILE_PATH = "lista_palabras.xlsx"


def update_vocabulary():
    """
    Goes through every word in Excel.
    If translation column is empty,
    it enriches the row using OpenAI.
    """

    # Load Excel into DataFrame
    df = pd.read_excel(FILE_PATH)

    # Force all columns to be object type (avoid pandas type issues)
    for col in df.columns:
        df[col] = df[col].astype("object")

    # Required columns for enriched data
    required_columns = [
        "type", "genre", "conjugation",
        "translation", "synonyms", "example"
    ]

    # If column doesn't exist, create it
    for col in required_columns:
        if col not in df.columns:
            df[col] = ""

    # Iterate row by row
    for index, row in df.iterrows():

        word = row["word"]

        # Skip empty rows
        if pd.isna(word) or str(word).strip() == "":
            continue

        # Skip already processed words
        if pd.notna(row["translation"]) and str(row["translation"]).strip() != "":
            print(f"Skipping: {word}")
            continue

        print(f"Processing: {word}")

        # Call AI enrichment
        info = get_word_info(word)

        if info:
            df.at[index, "type"] = info.get("type", "")
            df.at[index, "genre"] = info.get("genre", "")
            df.at[index, "translation"] = info.get("translation", "")
            df.at[index, "synonyms"] = info.get("synonyms", "")
            df.at[index, "example"] = info.get("example", "")

            # Handle verb conjugation separately
            conjugation = info.get("conjugation")
            if conjugation:
                df.at[index, "conjugation"] = (
                    f"ich: {conjugation.get('ich')}, "
                    f"du: {conjugation.get('du')}, "
                    f"er/sie/es: {conjugation.get('er_sie_es')}"
                )

            # Save file after EACH word
            df.to_excel(FILE_PATH, index=False)

    print("Vocabulary update complete.")