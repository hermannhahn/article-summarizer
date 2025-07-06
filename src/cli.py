import sys
import argparse
import os

from src.core.api_config import configure_api
from src.core.text_extraction import extract_text_from_article
from src.core.summarization import summarize_text
from src.utils.file_exporter import save_as_txt, save_as_pdf, save_as_docx, save_as_xlsx, save_as_image

def main():
    """
    Main function that orchestrates the summarization and saving process.
    """
    parser = argparse.ArgumentParser(description="AI Article Summarizer using Google Gemini.")
    parser.add_argument("urls", nargs='+', help="One or more URLs of the articles to be summarized.")
    parser.add_argument("--language", default="português", help="The language of the summary (e.g., 'english', 'spanish'). Default: português.")
    parser.add_argument("--style", default="a concise paragraph", help="The style of the summary (e.g., 'bullet points', 'for an executive').")
    parser.add_argument("--output", help="The base filename to save the summary (e.g., summary.txt, summary.pdf). For multiple URLs, an index will be added (e.g., summary_0.pdf, summary_1.pdf).")
    
    args = parser.parse_args()
    
    try:
        model = configure_api()
        
        for i, url in enumerate(args.urls):
            print(f"\n--- Processing URL {i+1}/{len(args.urls)}: {url} ---")
            article_text = extract_text_from_article(url)
            
            if article_text:
                summary = summarize_text(model, article_text, args.language, args.style)
                
                print(f"\n--- Article Summary (Style: {args.style}) ---")
                print(summary)
                print("----------------------------------------------------\n")
                
                if args.output:
                    base_filename, ext = os.path.splitext(args.output.lower())
                    output_filename = f"{base_filename}_{i}{ext}"

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
                        print("Unsupported file format. Use .txt, .pdf, .docx, .xlsx, .png, or .jpg.")
            else:
                print(f"Skipping summarization for {url} due to text extraction failure.")
            
    except ValueError as e:
        print(f"Configuration error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()