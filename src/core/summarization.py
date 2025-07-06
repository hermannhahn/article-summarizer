def summarize_text(model, text, language, style):
    """
    Sends the text to the Gemini model and returns the summary in the specified language and style.
    """
    if not text:
        return "Could not extract text to summarize."
    
    print(f"Sending text to AI for summarization in {language} with style '{style}'... This may take a moment.")
    
    prompt = f"Please summarize the following article in {language}. The summary style should be: '{style}'.\n\n-- ARTICLE START --\n{text}\n-- ARTICLE END --"
    
    try:
        response = model.generate_content(prompt)
        return {"main_summary": response.text, "style_requested": style, "language_requested": language}
    except Exception as e:
        return f"An error occurred during summarization: {e}"

