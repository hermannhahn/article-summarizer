# AI Article Summarizer

A command-line tool that uses the Google Gemini API to summarize web articles from a given URL. This project is part of a professional portfolio demonstrating skills in Python, API integration, and AI application development.

## Features

- Extracts the main text content from any article URL.
- Leverages the Google Gemini API (`gemini-1.5-flash`) for fast and intelligent summarization.
- Simple and straightforward command-line interface.

## Prerequisites

- Python 3.8+
- Git

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/hermannhahn/article-summarizer.git
    cd article-summarizer
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up your API Key:**
    - Get your free API key from [Google AI Studio](https://aistudio.google.com/app/apikey).
    - Create a file named `.env` in the project's root directory.
    - Add your API key to the `.env` file like this:
      ```
      GOOGLE_API_KEY='YOUR_API_KEY_HERE'
      ```

## Usage

Run the script from your terminal, passing the article URL as an argument:

```bash
python summarizer.py <URL_OF_THE_ARTICLE>
```

### Example

```bash
python summarizer.py https://www.theverge.com/2024/5/14/24156213/google-io-2024-ai-gemini-android-search-summary
```