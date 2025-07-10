import unittest
from unittest.mock import MagicMock, patch

from src.core import api_config


class TestApiConfig(unittest.TestCase):
    """Tests for the API configuration module."""

    @patch("src.core.api_config.os.getenv")
    @patch("src.core.api_config.genai.configure")
    @patch("src.core.api_config.genai.GenerativeModel")
    @patch("src.core.api_config.load_dotenv")
    def test_configure_api_success(self, mock_load_dotenv, mock_generative_model, mock_genai_configure, mock_os_getenv) -> None:
        """Tests successful API configuration when the API key is present."""
        # Arrange
        mock_os_getenv.return_value = "test_api_key"
        mock_model_instance = MagicMock()
        mock_generative_model.return_value = mock_model_instance

        # Act
        model = api_config.configure_api()

        # Assert
        mock_load_dotenv.assert_called_once()
        mock_os_getenv.assert_called_once_with("GOOGLE_API_KEY")
        mock_genai_configure.assert_called_once_with(api_key="test_api_key")
        mock_generative_model.assert_called_once_with("gemini-1.5-flash")
        self.assertEqual(model, mock_model_instance)

    @patch("src.core.api_config.os.getenv")
    @patch("src.core.api_config.load_dotenv")
    def test_configure_api_key_not_found(self, mock_load_dotenv, mock_os_getenv) -> None:
        """Tests that a ValueError is raised when the API key is not found."""
        # Arrange
        mock_os_getenv.return_value = None

        # Act & Assert
        with self.assertRaises(ValueError) as cm:
            api_config.configure_api()

        self.assertIn("Google API key not found", str(cm.exception))
        mock_load_dotenv.assert_called_once()
        mock_os_getenv.assert_called_once_with("GOOGLE_API_KEY")


if __name__ == "__main__":
    unittest.main()
