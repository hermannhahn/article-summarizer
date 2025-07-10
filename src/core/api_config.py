import logging
import os

import google.generativeai as genai
from dotenv import load_dotenv


def configure_api() -> genai.GenerativeModel:
    """Load the API key from the .env file and configure the Gemini SDK."""
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        logging.error("Google API key not found. Please check your .env file.")
        raise ValueError("Google API key not found. Please check your .env file.")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-1.5-flash")
