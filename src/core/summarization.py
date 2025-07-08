"""
Handles the summarization of text using the Google Gemini API.

This module provides the core function to interact with the configured Gemini
model, sending it a text prompt for summarization and returning the result.
"""

import logging
import google.generativeai as genai

def summarize_text(model: genai.GenerativeModel, text: str, language: str, style: str) -> dict:
    """Sends text to the Gemini model for summarization.

    Constructs a detailed prompt and calls the Gemini API to generate a summary
    based on the provided text, desired language, and style.

    Args:
        model (genai.GenerativeModel): The initialized Gemini model instance.
        text (str): The article text to be summarized.
        language (str): The target language for the summary (e.g., 'english').
        style (str): The desired style of the summary (e.g., 'a concise paragraph').

    Returns:
        dict: A dictionary containing the main summary, the requested style,
              and language. In case of an error, it includes an error message.
    """
    if not text or not text.strip():
        logging.warning("No text provided for summarization.")
        return {"main_summary": "Error: No text to summarize.", "error": True}

    logging.info(f"Sending text to AI for summarization in {language} with style '{style}'...")

    prompt = (
        f"Please summarize the following article in {language}. "
        f"The summary style should be: '{style}'.\n\n"
        f"-- ARTICLE START --\n{text}\n-- ARTICLE END --"
    )

    try:
        response = model.generate_content(prompt)
        # Accessing the text part of the response safely
        summary_text = response.text if hasattr(response, 'text') else ""
        if not summary_text:
            logging.warning("Summarization resulted in an empty response from the API.")
            return {"main_summary": "Warning: Received an empty summary.", "error": False}
        
        logging.info("Successfully received summary from the AI.")
        return {"main_summary": summary_text, "style_requested": style, "language_requested": language}
    except Exception as e:
        # Catching a broad exception from the API call is often necessary
        # as the google-generativeai library can raise various exceptions.
        logging.error(f"An error occurred during the API call to Gemini: {e}")
        return {"main_summary": f"An error occurred during summarization: {e}", "error": True}

