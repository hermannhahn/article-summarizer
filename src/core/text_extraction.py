import requests
from bs4 import BeautifulSoup
import logging
import os
from PyPDF2 import PdfReader
from docx import Document
from openpyxl import load_workbook

def _extract_text_from_pdf(file_path):
    """Extracts text from a PDF file."""
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        logging.info(f"Text extracted from PDF: {file_path}")
        return text
    except Exception as e:
        logging.error(f"Error extracting text from PDF {file_path}: {e}")
        return None

def _extract_text_from_docx(file_path):
    """Extracts text from a DOCX file."""
    try:
        document = Document(file_path)
        text = "\n".join([paragraph.text for paragraph in document.paragraphs])
        logging.info(f"Text extracted from DOCX: {file_path}")
        return text
    except Exception as e:
        logging.error(f"Error extracting text from DOCX {file_path}: {e}")
        return None

def _extract_text_from_xlsx(file_path):
    """Extracts text from an XLSX file."""
    try:
        workbook = load_workbook(file_path)
        text = ""
        for sheet_name in workbook.sheetnames:
            sheet = workbook[sheet_name]
            for row in sheet.iter_rows():
                for cell in row:
                    if cell.value is not None:
                        text += str(cell.value) + " "
            text += "\n"
        logging.info(f"Text extracted from XLSX: {file_path}")
        return text
    except Exception as e:
        logging.error(f"Error extracting text from XLSX {file_path}: {e}")
        return None

def extract_text(source_path):
    """Accesses a URL or local file, downloads/reads content, and extracts text."""
    if source_path.startswith(('http://', 'https://')):
        logging.info(f"Accessing article at: {source_path}")
        try:
            response = requests.get(source_path, headers={'User-Agent': 'Mozilla/5.0'})
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
    elif os.path.exists(source_path):
        file_extension = os.path.splitext(source_path)[1].lower()
        if file_extension == '.pdf':
            return _extract_text_from_pdf(source_path)
        elif file_extension == '.docx':
            return _extract_text_from_docx(source_path)
        elif file_extension == '.xlsx':
            return _extract_text_from_xlsx(source_path)
        else:
            logging.warning(f"Unsupported local file type: {file_extension}. Only .pdf, .docx, .xlsx are supported for text extraction.")
            return None
    else:
        logging.error(f"Invalid source: {source_path}. Must be a valid URL or existing local file path.")
        return None
