# AI Article Summarizer

A command-line tool that uses the Google Gemini API to summarize web articles from a given URL. This project is part of a professional portfolio demonstrating skills in Python, API integration, and AI application development.

## Features

- Extracts the main text content from any article URL.
- Leverages the Google Gemini API (`gemini-1.5-flash`) for fast and intelligent summarization.
- Simple and straightforward command-line interface.
- **Enhanced Text Extraction**: Supports text extraction from URLs, PDF, DOCX, and XLSX files.
- **Flexible Output Options**: Save summaries to a SQLite database or export to TXT, PDF, DOCX, XLSX, PNG, and JPG formats.
- **Robust Error Handling**: Improved error management for better stability and debugging.
- **Comprehensive Code Documentation**: Detailed docstrings for all functions and modules.

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

Run the main script from your terminal, providing the source (URL or file path) and optional arguments for language and style.

```bash
python main.py <SOURCE> [--language <LANGUAGE>] [--style <STYLE>]
```

### Arguments:

-   `<SOURCE>`: (Required) The URL of the article or the local path to a file (PDF, DOCX, XLSX).
-   `--language`: (Optional) The target language for the summary. Defaults to `Portuguese`.
-   `--style`: (Optional) The desired style for the summary (e.g., 'a concise paragraph', 'bullet points'). Defaults to `a concise paragraph`.

### Examples:

1.  **Summarize a web article (default settings):**
    ```bash
    python main.py https://www.theverge.com/2024/5/14/24156213/google-io-2024-ai-gemini-android-search-summary
    ```

2.  **Summarize a local PDF in English using bullet points:**
    ```bash
    python main.py "/path/to/my_document.pdf" --language English --style "bullet points"
    ```

## Development

### Running Tests

This project uses `pytest` for unit testing. To run the tests, first ensure you have activated your virtual environment and installed the development dependencies:

```bash
pip install pytest pytest-mock
```

Then, you can run all tests using:

```bash
python -m pytest tests/
```

### Code Structure

- `src/`: Contains the main application source code.
  - `src/core/`: Core logic for API configuration, text extraction, summarization, and database interactions.
  - `src/utils/`: Utility functions, including file exporting.
  - `src/cli.py`: The command-line interface entry point.
- `tests/`: Contains unit tests for the application modules.
- `config.json`: Configuration for database settings.
- `.env`: Environment variables (e.g., API keys).
- `requirements.txt`: Project dependencies.

## Contributing

Contributions are welcome! Please feel free to open issues or submit pull requests. Ensure your code adheres to the existing style and passes all tests.
