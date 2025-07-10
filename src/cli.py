"""Command-Line Interface for the AI Article Summarizer.

This module provides a CLI for summarizing articles from URLs or local files
and for querying previously saved summaries from the database.

It uses argparse to handle command-line arguments and orchestrates the calls
to the core modules for text extraction, summarization, and database operations.
"""

import argparse
import logging
import os
import sqlite3
import sys

from src.core.api_config import configure_api
from src.core.database import get_summaries, save_summary_to_db
from src.core.summarization import summarize_text
from src.core.text_extraction import extract_text
from src.utils.file_exporter import (
    save_as_docx,
    save_as_image,
    save_as_pdf,
    save_as_txt,
    save_as_xlsx,
)

# Add project root to the Python path to allow for absolute imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


def handle_summarize_command(args: argparse.Namespace) -> None:
    """Handle the summarization logic for the 'summarize' command.

    Args:
        args (argparse.Namespace): The parsed arguments from the command line.
    """
    try:
        model = configure_api()

        for i, source in enumerate(args.sources):
            logging.info(
                f"--- Processing source {i+1}/{len(args.sources)}: {source} ---"
            )
            article_text = extract_text(source)

            if not article_text:
                logging.warning(
                    f"Skipping summarization for '{source}' due to text extraction failure."
                )
                continue

            summary = summarize_text(model, article_text, args.language, args.style)

            if summary.get("error"):
                logging.error(
                    f"Could not summarize '{source}'. Reason: {summary.get('main_summary')}"
                )
                continue

            logging.info(f"--- Article Summary (Style: {args.style}) ---")
            logging.info(summary.get("main_summary", "No summary content received."))
            logging.info("----------------------------------------------------")

            # --- Saving Logic ---
            if args.save_to_db:
                summary_data = {
                    "source_url": (
                        source
                        if source.startswith(("http://", "https://"))
                        else f"file://{os.path.abspath(source)}"
                    ),
                    "summary_text": summary,
                    "style": args.style,
                    "language": args.language,
                }
                save_summary_to_db(summary_data)

            elif args.output_file:
                base_filename, ext = os.path.splitext(args.output_file.lower())
                output_filename = (
                    f"{base_filename}_{i}{ext}"
                    if len(args.sources) > 1
                    else f"{base_filename}{ext}"
                )
                main_summary_text = summary.get("main_summary", "")

                savers = {
                    ".txt": save_as_txt,
                    ".pdf": save_as_pdf,
                    ".docx": save_as_docx,
                    ".xlsx": save_as_xlsx,
                    ".png": lambda text, fname: save_as_image(text, fname, "png"),
                    ".jpeg": lambda text, fname: save_as_image(text, fname, "jpeg"),
                    ".jpg": lambda text, fname: save_as_image(text, fname, "jpeg"),
                }

                saver_func = savers.get(ext)
                if saver_func:
                    saver_func(main_summary_text, output_filename)
                else:
                    logging.warning(
                        f"Unsupported file format '{ext}'. Use .txt, .pdf, .docx, .xlsx, .png, or .jpg."
                    )

    except (ValueError, FileNotFoundError) as e:
        logging.error(f"Configuration or file error: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"An unexpected error occurred in the summarize command: {e}")
        sys.exit(1)


def handle_query_command(args: argparse.Namespace) -> None:
    """Handle the database query logic for the 'query' command.

    Args:
        args (argparse.Namespace): The parsed arguments from the command line.
    """
    try:
        logging.info("Querying summaries...")
        summaries = get_summaries(
            limit=args.limit, url_contains=args.url_contains, style=args.style
        )

        if not summaries:
            logging.info("No summaries found matching your criteria.")
            return

        for summary in summaries:
            logging.info(f"--- Summary ID: {summary.get('id')} ---")
            logging.info(f"URL: {summary.get('source_url')}")
            logging.info(f"Language: {summary.get('language')}")
            logging.info(f"Style: {summary.get('style')}")
            logging.info(f"Date: {summary.get('created_at')}")
            summary_text = summary.get("summary_text", {}).get(
                "main_summary", "[No summary text found]"
            )
            logging.info(f"Summary: {summary_text}")
            logging.info("----------------------------------------------------")
    except sqlite3.Error as e:
        logging.error(f"Database query failed: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"An unexpected error occurred in the query command: {e}")
        sys.exit(1)


def main() -> None:
    """Parse arguments and execute the chosen command."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        stream=sys.stdout,
    )

    parser = argparse.ArgumentParser(
        description="AI Article Summarizer using Google Gemini.",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    subparsers = parser.add_subparsers(
        dest="command", help="Available commands", required=True
    )

    # --- Summarize Command ---
    summarize_parser = subparsers.add_parser(
        "summarize", help="Summarize articles from URLs or local files"
    )
    summarize_parser.add_argument(
        "sources",
        nargs="+",
        help="One or more URLs or local file paths (PDF, DOCX, XLSX).",
    )
    summarize_parser.add_argument(
        "-l",
        "--language",
        default="português",
        help="Language of the summary (e.g., 'english'). Default: português.",
    )
    summarize_parser.add_argument(
        "-s",
        "--style",
        default="a concise paragraph",
        help="Style of the summary (e.g., 'bullet points'). Default: a concise paragraph.",
    )

    output_group = summarize_parser.add_mutually_exclusive_group()
    output_group.add_argument(
        "-o",
        "--output-file",
        help="Base filename to save the summary. Supported formats: .txt, .pdf, .docx, .xlsx, .png, .jpg.",
    )
    output_group.add_argument(
        "-db",
        "--save-to-db",
        action="store_true",
        help="Save the summary to the SQLite database.",
    )
    summarize_parser.set_defaults(func=handle_summarize_command)

    # --- Query Command ---
    query_parser = subparsers.add_parser(
        "query", help="Query summaries from the database"
    )
    query_parser.add_argument(
        "-l",
        "--limit",
        type=int,
        default=5,
        help="Limit the number of results. Default: 5.",
    )
    query_parser.add_argument(
        "-u", "--url-contains", help="Filter summaries by URL containing this string."
    )
    query_parser.add_argument("-s", "--style", help="Filter summaries by style.")
    query_parser.set_defaults(func=handle_query_command)

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
