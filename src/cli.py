import sys
import argparse

from src.core.api_config import configure_api
from src.core.text_extraction import extract_text_from_article
from src.core.summarization import summarize_text
from src.utils.file_exporter import save_as_txt, save_as_pdf, save_as_docx, save_as_xlsx, save_as_image

def main():
    """
    Main function that orchestrates the summarization and saving process.
    """
    parser = argparse.ArgumentParser(description="AI Article Summarizer using Google Gemini.")
    parser.add_argument("url", help="The URL of the article to be summarized.")
    parser.add_argument("--language", default="português", help="The language of the summary (e.g., 'english', 'spanish'). Default: português.")
    parser.add_argument("--style", default="a concise paragraph", help="The style of the summary (e.g., 'bullet points', 'for an executive').")
    parser.add_argument("--output", help="The filename to save the summary (e.g., summary.txt, summary.pdf, summary.docx, summary.xlsx, summary.png, summary.jpg).")
    
    args = parser.parse_args()
    
    try:
        model = configure_api()
        article_text = extract_text_from_article(args.url)
        
        if article_text:
            summary = summarize_text(model, article_text, args.language, args.style)
            
            print(f"\n--- Article Summary (Style: {args.style}) ---")
            print(summary)
            print("----------------------------------------------------\n")
            
            if args.output:
                filename = args.output.lower()
                if filename.endswith('.txt'):
                    save_as_txt(summary, filename)
                elif filename.endswith('.pdf'):
                    save_as_pdf(summary, filename)
                elif filename.endswith('.docx'):
                    save_as_docx(summary, filename)
                elif filename.endswith('.xlsx'):
                    save_as_xlsx(summary, filename)
                elif filename.endswith('.png'):
                    save_as_image(summary, filename, 'png')
                elif filename.endswith('.jpg') or filename.endswith('.jpeg'):
                    save_as_image(summary, filename, 'jpeg')
                else:
                    print("Unsupported file format. Use .txt, .pdf, .docx, .xlsx, .png, or .jpg.")
            
    except ValueError as e:
        print(f"Configuration error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
