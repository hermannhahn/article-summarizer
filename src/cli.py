import sys
import argparse
import os
import logging

# Add project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.core.api_config import configure_api
from src.core.text_extraction import extract_text_from_article
from src.core.summarization import summarize_text
from src.core.database import save_summary_to_db

def handle_summarize_command(args):
    """Handles the summarization logic."""
    try:
        model = configure_api()
        
        for i, url in enumerate(args.urls):
            logging.info(f"--- Processing URL {i+1}/{len(args.urls)}: {url} ---")
            article_text = extract_text_from_article(url)
            
            if not article_text:
                logging.warning(f"Skipping summarization for {url} due to text extraction failure.")
                continue

            summary = summarize_text(model, args.language, args.style, article_text)
            
            logging.info(f"--- Article Summary (Style: {args.style}) ---")
            logging.info(summary.get('main_summary', '')) # Display only main summary
            logging.info("----------------------------------------------------")
            
            # --- Saving Logic (only to DB) ---
            if args.save_to_db:
                summary_data = {
                    'source_url': url,
                    'summary_text': summary,
                    'style': args.style,
                    'language': args.language
                }
                save_summary_to_db(summary_data)
            else:
                logging.info("No output option selected. Summary displayed above.")

    except ValueError as e:
        logging.error(f"Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        sys.exit(1)

def handle_query_command(args):
    """Handles the query logic for summaries."""
    from src.core.database import get_summaries # Import here to avoid circular dependency if not needed by summarize
    
    logging.info("Querying summaries...")
    summaries = get_summaries(limit=args.limit, url_contains=args.url_contains, style=args.style)
    
    if not summaries:
        logging.info("No summaries found matching your criteria.")
        return

    for summary in summaries:
        logging.info(f"--- Summary ID: {summary.get('id')} ---")
        logging.info(f"URL: {summary.get('source_url')}")
        logging.info(f"Language: {summary.get('language')}")
        logging.info(f"Style: {summary.get('style')}")
        logging.info(f"Date: {summary.get('created_at')}")
        logging.info(f"Summary: {summary.get('summary_text', {}).get('main_summary', '')}")
        logging.info("----------------------------------------------------")


def main():
    """
    Main function that orchestrates the summarization and query processes via a command-line interface.
    """
    # Configure basic logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s: %(message)s',
        stream=sys.stdout
    )

    parser = argparse.ArgumentParser(
        description="AI Article Summarizer using Google Gemini.",
        formatter_class=argparse.RawTextHelpFormatter # Allows for better formatting of help text
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # --- Summarize Command ---
    summarize_parser = subparsers.add_parser('summarize', help='Summarize articles from URLs')
    summarize_parser.add_argument("urls", nargs='+', help="One or more URLs of the articles to be summarized.")
    summarize_parser.add_argument("-l", "--language", default="português", 
                                help="The language of the summary (e.g., 'english', 'spanish').\nDefault: português.")
    summarize_parser.add_argument("-s", "--style", default="a concise paragraph", 
                                help="The style of the summary (e.g., 'bullet points', 'for an executive').\nDefault: a concise paragraph.")
    summarize_parser.add_argument("-db", "--save-to-db", action="store_true", 
                                help="Save the summary to the SQLite database defined in config.json.")
    summarize_parser.set_defaults(func=handle_summarize_command)

    # --- Query Command ---
    query_parser = subparsers.add_parser('query', help='Query summaries from the database')
    query_parser.add_argument("-l", "--limit", type=int, default=5, 
                              help="Limit the number of results. Default: 5.")
    query_parser.add_argument("-u", "--url-contains", 
                              help="Filter summaries by URL containing this string.")
    query_parser.add_argument("-s", "--style", 
                              help="Filter summaries by style.")
    query_parser.set_defaults(func=handle_query_command)

    args = parser.parse_args()

    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    # Add a check to ensure the script is being run with arguments
    if len(sys.argv) == 1:
        logging.info("No arguments provided. Use -h or --help to see the available options.")
        sys.exit(1)
    main()