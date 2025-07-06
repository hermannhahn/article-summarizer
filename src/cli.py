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
from src.utils.file_exporter import save_as_txt, save_as_pdf, save_as_docx, save_as_xlsx, save_as_image

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

    # --- Output Arguments (mutually exclusive) ---
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("-o", "--output-file", 
                              help="The base filename to save the summary. Supported formats: .txt, .pdf, .docx, .xlsx, .png, .jpg.\nFor multiple URLs, an index is added (e.g., summary_0.pdf, summary_1.pdf).")
    output_group.add_argument("-db", "--save-to-db", action="store_true", 
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
            print(summary)
            print("----------------------------------------------------\n")
            
            # --- Saving Logic ---
            if args.save_to_db:
                summary_data = {
                    'source_url': url,
                    'summary_text': summary,
                    'style': args.style,
                    'language': args.language
                }
                save_summary_to_db(summary_data)

            elif args.output_file:
                base_filename, ext = os.path.splitext(args.output_file.lower())
                # Add index only if there are multiple URLs
                output_filename = f"{base_filename}_{i}{ext}" if len(args.urls) > 1 else f"{base_filename}{ext}"

                if output_filename.endswith('.txt'):
                    save_as_txt(summary, output_filename)
                elif output_filename.endswith('.pdf'):
                    save_as_pdf(summary, output_filename)
                elif output_filename.endswith('.docx'):
                    save_as_docx(summary, output_filename)
                elif output_filename.endswith('.xlsx'):
                    save_as_xlsx(summary, output_filename)
                elif output_filename.endswith('.png'):
                    save_as_image(summary, output_filename, 'png')
                elif output_filename.endswith('.jpg') or output_filename.endswith('.jpeg'):
                    save_as_image(summary, output_filename, 'jpeg')
                else:
                    print(f"Warning: Unsupported file format for '{output_filename}'. Use .txt, .pdf, .docx, .xlsx, .png, or .jpg.")

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