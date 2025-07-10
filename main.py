import argparse
import logging

from src.core.api_config import configure_api
from src.core.database import create_summary_table, save_summary_to_db
from src.core.summarization import summarize_text
from src.core.text_extraction import extract_text


def main() -> None:
    """Run the article summarizer CLI."""
    # --- Argument Parsing ---
    parser = argparse.ArgumentParser(
        description="Summarize an article from a URL or local file."
    )
    parser.add_argument(
        "source", help="The URL or local file path (PDF, DOCX, XLSX) to summarize."
    )
    parser.add_argument(
        "--language", default="Portuguese", help="The target language for the summary."
    )
    parser.add_argument(
        "--style",
        default="a concise paragraph",
        help="The desired style of the summary (e.g., 'bullet points').",
    )
    args = parser.parse_args()

    # --- Logging Setup ---
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # --- Database Initialization ---
    logging.info("Initializing database...")
    create_summary_table()

    # --- Text Extraction ---
    logging.info(f"Extracting text from source: {args.source}")
    article_text = extract_text(args.source)
    if not article_text:
        logging.error("Failed to extract text. Exiting.")
        return

    # --- API Configuration ---
    try:
        logging.info("Configuring AI model...")
        model = configure_api()
    except ValueError as e:
        logging.error(f"API configuration failed: {e}")
        return

    # --- Summarization ---
    logging.info("Generating summary...")
    summary_result = summarize_text(model, article_text, args.language, args.style)

    if summary_result.get("error"):
        logging.error(f"Summarization failed: {summary_result['main_summary']}")
        return

    # --- Save and Display Summary ---
    summary_data = {
        "source_url": args.source,
        "summary_text": summary_result.get("main_summary"),
        "style": summary_result.get("style_requested"),
        "language": summary_result.get("language_requested"),
    }

    save_summary_to_db(summary_data)

    print("\n--- Summary ---")
    print(summary_result.get("main_summary"))
    print("---------------")


if __name__ == "__main__":
    main()
