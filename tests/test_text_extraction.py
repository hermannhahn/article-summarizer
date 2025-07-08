

import unittest
from unittest.mock import patch, MagicMock
from src.core import text_extraction

class TestTextExtraction(unittest.TestCase):

    @patch('src.core.text_extraction.requests.get')
    def test_extract_text_from_url_success(self, mock_requests_get):
        """Tests successful text extraction from a URL with <p> tags."""
        # Arrange
        html_content = "<html><body><p>Hello</p><p>World</p></body></html>"
        mock_response = MagicMock()
        mock_response.content = html_content.encode('utf-8')
        mock_response.raise_for_status.return_value = None
        mock_requests_get.return_value = mock_response

        # Act
        result = text_extraction.extract_text("http://example.com")

        # Assert
        self.assertEqual(result, "Hello\nWorld")
        mock_requests_get.assert_called_once_with("http://example.com", headers=unittest.mock.ANY, timeout=15)

    @patch('src.core.text_extraction.os.path.exists')
    @patch('src.core.text_extraction._extract_text_from_pdf')
    def test_extract_text_delegates_to_pdf_extractor(self, mock_pdf_extractor, mock_exists):
        """Tests that extract_text delegates to the correct helper for PDF files."""
        # Arrange
        mock_exists.return_value = True
        mock_pdf_extractor.return_value = "PDF text"
        
        # Act
        result = text_extraction.extract_text("/path/to/file.pdf")

        # Assert
        mock_exists.assert_called_once_with("/path/to/file.pdf")
        mock_pdf_extractor.assert_called_once_with("/path/to/file.pdf")
        self.assertEqual(result, "PDF text")

    @patch('src.core.text_extraction.os.path.exists')
    def test_extract_text_source_not_found(self, mock_exists):
        """Tests behavior when the source is not a URL and the file does not exist."""
        # Arrange
        mock_exists.return_value = False

        # Act
        result = text_extraction.extract_text("/invalid/path/file.txt")

        # Assert
        self.assertIsNone(result)
        mock_exists.assert_called_once_with("/invalid/path/file.txt")

    @patch('src.core.text_extraction.requests.get')
    def test_extract_text_from_url_fallback(self, mock_requests_get):
        """Tests URL extraction fallback when no <p> tags are found."""
        # Arrange
        html_content = "<html><body><div>Hello World</div></body></html>"
        mock_response = MagicMock()
        mock_response.content = html_content.encode('utf-8')
        mock_response.raise_for_status.return_value = None
        mock_requests_get.return_value = mock_response

        # Act
        result = text_extraction.extract_text("http://example.com")

        # Assert
        self.assertEqual(result, "Hello World")

    @patch('src.core.text_extraction.requests.get')
    def test_extract_text_from_url_http_error(self, mock_requests_get):
        """Tests URL extraction failure on HTTP error."""
        # Arrange
        mock_requests_get.side_effect = text_extraction.requests.exceptions.HTTPError

        # Act
        result = text_extraction.extract_text("http://example.com")

        # Assert
        self.assertIsNone(result)

    @patch('src.core.text_extraction.os.path.exists')
    @patch('src.core.text_extraction._extract_text_from_docx')
    def test_extract_text_delegates_to_docx_extractor(self, mock_docx_extractor, mock_exists):
        """Tests delegation to the DOCX extractor."""
        # Arrange
        mock_exists.return_value = True
        mock_docx_extractor.return_value = "DOCX text"

        # Act
        result = text_extraction.extract_text("/path/to/file.docx")

        # Assert
        mock_docx_extractor.assert_called_once_with("/path/to/file.docx")
        self.assertEqual(result, "DOCX text")

    @patch('src.core.text_extraction.os.path.exists')
    @patch('src.core.text_extraction._extract_text_from_xlsx')
    def test_extract_text_delegates_to_xlsx_extractor(self, mock_xlsx_extractor, mock_exists):
        """Tests delegation to the XLSX extractor."""
        # Arrange
        mock_exists.return_value = True
        mock_xlsx_extractor.return_value = "XLSX text"

        # Act
        result = text_extraction.extract_text("/path/to/file.xlsx")

        # Assert
        mock_xlsx_extractor.assert_called_once_with("/path/to/file.xlsx")
        self.assertEqual(result, "XLSX text")

    @patch('src.core.text_extraction.os.path.exists')
    def test_extract_text_unsupported_file_type(self, mock_exists):
        """Tests that unsupported file types return None."""
        # Arrange
        mock_exists.return_value = True

        # Act
        result = text_extraction.extract_text("/path/to/file.txt")

        # Assert
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()

