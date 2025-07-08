import os
from fpdf import FPDF
from docx import Document
from openpyxl import Workbook
from PIL import Image, ImageDraw, ImageFont
import logging

def _ensure_directory_exists(filename):
    directory = os.path.dirname(filename)
    if directory:
        os.makedirs(directory, exist_ok=True)

def save_as_txt(text, filename):
    """Saves the provided text to a .txt file."""
    try:
        _ensure_directory_exists(filename)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(text)
        logging.info(f"Summary successfully saved to: {filename}")
    except IOError as e:
        logging.error(f"Error saving .txt file: {e}")

def save_as_pdf(text, filename):
    """
    Saves the provided text to a .pdf file.
    Note: fpdf2 might have issues with non-latin characters without proper font setup.
    """
    try:
        _ensure_directory_exists(filename)
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=12)
        # Encode to latin-1 and decode back to handle some character issues, or use a font that supports UTF-8
        pdf.multi_cell(0, 10, text=text.encode('latin-1', 'replace').decode('latin-1'))
        pdf.output(filename)
        logging.info(f"Summary successfully saved to: {filename}")
    except Exception as e:
        logging.error(f"Error saving .pdf file: {e}")

def save_as_docx(text, filename):
    """Saves the provided text to a .docx file."""
    try:
        _ensure_directory_exists(filename)
        document = Document()
        document.add_paragraph(text)
        document.save(filename)
        logging.info(f"Summary successfully saved to: {filename}")
    except Exception as e:
        logging.error(f"Error saving .docx file: {e}")

def save_as_xlsx(text, filename):
    """Saves the provided text to an .xlsx file."""
    try:
        _ensure_directory_exists(filename)
        wb = Workbook()
        ws = wb.active
        ws['A1'] = "Article Summary"
        ws['A2'] = text
        wb.save(filename)
        logging.info(f"Summary successfully saved to: {filename}")
    except Exception as e:
        logging.error(f"Error saving .xlsx file: {e}")

def save_as_image(text, filename, image_type='png'):
    """
    Saves the provided text to an image file (PNG or JPG).
    Note: Requires Pillow. Font handling might need system-specific fonts for full UTF-8 support.
    """
    try:
        _ensure_directory_exists(filename)
        # Image settings
        width = 800
        padding = 50
        font_size = 20
        bg_color = (255, 255, 255)  # White
        text_color = (0, 0, 0)      # Black

        # Try to load a system font
        try:
            # This font path might need to be adjusted based on the OS
            font = ImageFont.truetype("arial.ttf", font_size)
        except IOError:
            # Fallback to a generic font if arial.ttf is not found
            logging.warning("arial.ttf not found. Falling back to default font for image export.")
            font = ImageFont.load_default()

        # Calculate necessary height for text
        lines = []
        draw_temp = ImageDraw.Draw(Image.new('RGB', (1, 1)))
        
        # Break text into lines that fit within image width
        words = text.split(' ')
        current_line = []
        for word in words:
            try_line = " ".join(current_line + [word])
            bbox = draw_temp.textbbox((0,0), try_line, font=font)
            text_width = bbox[2] - bbox[0]
            if text_width <= (width - 2 * padding):
                current_line.append(word)
            else:
                lines.append(" ".join(current_line))
                current_line = [word]
        lines.append(" ".join(current_line))

        total_text_height = len(lines) * (font_size + 5) # +5 for line spacing
        height = total_text_height + 2 * padding
        if height < 200: # Minimum height for very short images
            height = 200

        img = Image.new('RGB', (width, height), color = bg_color)
        d = ImageDraw.Draw(img)

        y_text = padding
        for line in lines:
            d.text((padding, y_text), line, font=font, fill=text_color)
            y_text += (font_size + 5)

        img.save(filename, image_type.upper())
        logging.info(f"Summary successfully saved to: {filename}")
    except Exception as e:
        logging.error(f"Error saving image file: {e}")
