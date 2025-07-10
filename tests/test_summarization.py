import unittest
from unittest.mock import MagicMock

from src.core import summarization


class TestSummarization(unittest.TestCase):
    """Tests for the summarization module."""

    def test_summarize_text_success(self) -> None:
        """Tests successful summarization with a valid response."""
        # Arrange
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "This is a summary."
        mock_model.generate_content.return_value = mock_response

        text = "This is the article text."
        language = "English"
        style = "a concise paragraph"

        # Act
        result = summarization.summarize_text(mock_model, text, language, style)

        # Assert
        mock_model.generate_content.assert_called_once()
        self.assertIn(
            "summarize the following article in English",
            mock_model.generate_content.call_args[0][0],
        )
        self.assertEqual(
            result,
            {
                "main_summary": "This is a summary.",
                "style_requested": style,
                "language_requested": language,
            },
        )

    def test_summarize_text_no_input_text(self) -> None:
        """Tests the function's response to empty input text."""
        # Arrange
        mock_model = MagicMock()

        # Act
        result = summarization.summarize_text(
            mock_model, "", "English", "a concise paragraph"
        )

        # Assert
        mock_model.generate_content.assert_not_called()
        self.assertEqual(
            result, {"main_summary": "Error: No text to summarize.", "error": True}
        )

    def test_summarize_text_api_error(self) -> None:
        """Tests the function's handling of an API exception."""
        # Arrange
        mock_model = MagicMock()
        mock_model.generate_content.side_effect = Exception("API Error")

        # Act
        result = summarization.summarize_text(
            mock_model, "Some text", "English", "a concise paragraph"
        )

        # Assert
        mock_model.generate_content.assert_called_once()
        self.assertTrue(result.get("error"))
        self.assertIn(
            "An error occurred during summarization: API Error", result["main_summary"]
        )

    def test_summarize_text_empty_response(self) -> None:
        """Tests handling of an empty text response from the API."""
        # Arrange
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = ""
        mock_model.generate_content.return_value = mock_response

        # Act
        result = summarization.summarize_text(
            mock_model, "Some text", "English", "a concise paragraph"
        )

        # Assert
        self.assertEqual(
            result,
            {"main_summary": "Warning: Received an empty summary.", "error": False},
        )


if __name__ == "__main__":
    unittest.main()
