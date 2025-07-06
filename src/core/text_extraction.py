import requests
from bs4 import BeautifulSoup
import logging

def extract_text_from_article(url):
    """
    Accesses a URL, downloads the HTML content, and extracts text from paragraphs.
    """
    logging.info(f"Accessing article at: {url}")
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract text from all <p> tags
        paragraphs = soup.find_all('p')
        article_text = '\n'.join([p.get_text() for p in paragraphs])
        
        if not article_text:
            logging.warning("No paragraph (<p>) text found on the page. Attempting generic text extraction.")
            # Fallback to generic text extraction if <p> tags are not found
            return soup.get_text(separator='\n', strip=True)

        return article_text
    except requests.exceptions.RequestException as e:
        logging.error(f"Error accessing URL: {e}")
        return None
