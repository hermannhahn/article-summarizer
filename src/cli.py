import sys
import argparse
import os

# Add project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.core.api_config import configure_api
from src.core.text_extraction import extract_text_from_article
from src.core.summarization import summarize_text
from src.core.database import save_summary_to_db

def main():
    """
    Main function that orchestrates the summarization and saving process via a command-line interface.
    """
    parser = argparse.ArgumentParser(
        description="AI Article Summarizer using Google Gemini.",
        formatter_class=argparse.RawTextHelpFormatter # Allows for better formatting of help text
    )
    
    # --- Input Arguments ---
    parser.add_argument("urls", nargs='+', help="One or more URLs of the articles to be summarized.")
    
    # --- Customization Arguments ---
    parser.add_argument("-l", "--language", default="português", 
                        help="The language of the summary (e.g., 'english', 'spanish').\nDefault: português.")
    parser.add_argument("-s", "--style", default="a concise paragraph", 
                        help="The style of the summary (e.g., 'bullet points', 'for an executive').\nDefault: a concise paragraph.")

    # --- Output Argument (only save to DB) ---
    parser.add_argument("-db", "--save-to-db", action="store_true", 
                              help="Save the summary to the SQLite database defined in config.json.")

    args = parser.parse_args()

    # --- Main Logic ---
    try:
        model = configure_api()
        
        for i, url in enumerate(args.urls):
            print(f"\n--- Processing URL {i+1}/{len(args.urls)}: {url} ---")
            article_text = extract_text_from_article(url)
            
            if not article_text:
                print(f"Skipping summarization for {url} due to text extraction failure.")
                continue

            summary = summarize_text(model, article_text, args.language, args.style)
            
            print(f"\n--- Article Summary (Style: {args.style}) ---")
            print(summary.get('main_summary', '')) # Display only main summary
            print("----------------------------------------------------\n")
            
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
                print("No output option selected. Summary displayed above.")

    except ValueError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    # Add a check to ensure the script is being run with arguments
    if len(sys.argv) == 1:
        print("No arguments provided. Use -h or --help to see the available options.", file=sys.stderr)
        sys.exit(1)
    main()
