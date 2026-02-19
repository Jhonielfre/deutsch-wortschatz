# Standard library imports
import os              # Access environment variables
import json            # Parse JSON strings into Python dictionaries

# OpenAI SDK
from openai import OpenAI

# Loads variables from a .env file into environment
from dotenv import load_dotenv


# ---------------------------------------------------
# Load API key from .env file
# ---------------------------------------------------
load_dotenv()

# Create OpenAI client using API key stored in environment variable
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_word_info(word):
    """
    Sends a prompt to OpenAI asking for structured information
    about a German word.

    Returns:
        dict containing:
            - type (noun, verb, adjective, adverb...)
            - genre (if noun)
            - conjugation (if verb)
            - translation (Spanish)
            - synonyms (Spanish)
            - example sentence (German)
    """

    # Prompt is carefully engineered to FORCE valid JSON output
    prompt = f"""
    Return ONLY valid JSON. No explanation. No markdown.

    German word: "{word}"

    JSON format:
    {{
        "type": "...",
        "genre": null,
        "conjugation": null,
        "translation": "...",
        "synonyms": "...",
        "example": "..."
    }}
    """

    # Send request to model
    response = client.chat.completions.create(
        model="gpt-4o-mini",            # Small, cheap, fast model
        messages=[{"role": "user", "content": prompt}],
        temperature=0,                  # Deterministic output
        response_format={"type": "json_object"}  # Force JSON structure
    )

    # Convert JSON string returned by model into Python dict
    return json.loads(response.choices[0].message.content)