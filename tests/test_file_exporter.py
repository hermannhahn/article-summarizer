import os
import unittest
from unittest.mock import patch, mock_open, MagicMock, call
from src.utils import file_exporter

class TestFileExporter(unittest.TestCase):

    def test_save_as_txt(self):
        """Tests the save_as_txt function."""
        m = mock_open()
        with patch('builtins.open', m):
            file_exporter.save_as_txt("test content", "test.txt")
        m.assert_called_once_with("test.txt", 'w', encoding='utf-8')
        handle = m()
        handle.write.assert_called_once_with("test content")

    @patch('src.utils.file_exporter.FPDF')
    def test_save_as_pdf(self, mock_fpdf):
        """Tests the save_as_pdf function."""
        file_exporter.save_as_pdf("test content", "test.pdf")
        instance = mock_fpdf.return_value
        instance.add_page.assert_called_once()
        instance.set_font.assert_called_once_with("Helvetica", size=12)
        instance.multi_cell.assert_called_once()
        instance.output.assert_called_once_with("test.pdf")

    @patch('src.utils.file_exporter.Document')
    def test_save_as_docx(self, mock_document):
        """Tests the save_as_docx function."""
        file_exporter.save_as_docx("test content", "test.docx")
        instance = mock_document.return_value
        instance.add_paragraph.assert_called_once_with("test content")
        instance.save.assert_called_once_with("test.docx")

    @patch('src.utils.file_exporter.Workbook')
    def test_save_as_xlsx(self, mock_workbook):
        """Tests the save_as_xlsx function."""
        mock_ws = MagicMock()
        mock_wb_instance = mock_workbook.return_value
        mock_wb_instance.active = mock_ws

        mock_ws.__getitem__.side_effect = lambda key: {'A1': MagicMock(), 'A2': MagicMock()}.get(key)

        file_exporter.save_as_xlsx("test content", "test.xlsx")

        mock_workbook.assert_called_once()
        mock_ws.__setitem__.assert_any_call('A1', 'Article Summary')
        mock_ws.__setitem__.assert_any_call('A2', 'test content')
        mock_wb_instance.save.assert_called_once_with("test.xlsx")

    @patch('src.utils.file_exporter._ensure_directory_exists')
    @patch('src.utils.file_exporter.ImageDraw.Draw')
    @patch('src.utils.file_exporter.ImageFont.truetype')
    @patch('src.utils.file_exporter.ImageFont.load_default')
    @patch('src.utils.file_exporter.Image.new') # Keep this patch last
    def test_save_as_image(self, mock_image_new, mock_load_default, mock_truetype, mock_draw, mock_ensure_dir):
        """Tests the save_as_image function."""
        # A text that will definitely wrap into two lines with 70 char limit per line
        test_text = "This is a very long sentence that should definitely wrap into multiple lines when rendered."
        test_filename = "summary.png"

        # Mock the font to return a mock object with a getbbox method that returns integers
        mock_font_instance = MagicMock()
        # Simulate a font where each character is 10px wide and 15px high
        mock_font_instance.getbbox.return_value = (0, 0, 100, 15)  # (left, top, right, bottom) for a character
        mock_truetype.return_value = mock_font_instance
        mock_load_default.return_value = mock_font_instance

        # Mock the main image instance
        mock_img_instance = MagicMock()
        mock_image_new.return_value = mock_img_instance

        # Mock the draw object and its textbbox method for text wrapping calculations
        mock_draw_instance = MagicMock()
        mock_draw.return_value = mock_draw_instance
        # Simulate textbbox returning a value that allows text to fit within the width
        # This needs to be dynamic based on the text length for accurate wrapping simulation
        mock_draw_instance.textbbox.side_effect = lambda pos, text, font: (0, 0, len(text) * 10, 15)

        # Act
        file_exporter.save_as_image(test_text, test_filename, 'png')

        # Assert _ensure_directory_exists was called
        mock_ensure_dir.assert_called_once_with(test_filename)

        # Assert Image.new was called for the final image (not the internal ones for text measurement)
        # We need to check the arguments of the *last* call, as there are internal calls to Image.new
        # for text measurement that we don't care about for the final image creation.
        mock_image_new.assert_called_with('RGB', (800, 140), color=(255, 255, 255)) # Adjusted expected height based on new text

        # Assert ImageDraw.Draw was called for the final image
        mock_draw.assert_called_with(mock_img_instance)

        # Assert font loading logic
        mock_truetype.assert_called_once_with("arial.ttf", 20)
        mock_load_default.assert_not_called()

        # Assert text was drawn for each line
        expected_calls = [
            call(unittest.mock.ANY, 'This is a very long sentence that should definitely wrap into', font=mock_font_instance, fill=(0, 0, 0)),
            call(unittest.mock.ANY, 'multiple lines when rendered.', font=mock_font_instance, fill=(0, 0, 0))
        ]
        mock_draw_instance.text.assert_has_calls(expected_calls, any_order=False)

        # Assert image was saved
        mock_img_instance.save.assert_called_once_with(test_filename, 'PNG')

if __name__ == '__main__':
    unittest.main()