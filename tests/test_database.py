import unittest
from unittest.mock import patch, mock_open, MagicMock
import json
import os
from src.core import database

class TestDatabase(unittest.TestCase):

    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    @patch('os.path.dirname') # Patch os.path.dirname
    @patch('os.path.abspath') # Patch os.path.abspath
    def test_get_db_config_success(self, mock_abspath, mock_dirname, mock_json_load, mock_open_file):
        """Tests successful loading of database configuration from config.json."""
        # Arrange
        # Simulate the __file__ path
        mock_abspath.return_value = '/fake/project/root/src/core/database.py'

        # Simulate the sequence of os.path.dirname calls
        # 1st call: os.path.dirname(__file__) -> /fake/project/root/src/core
        # 2nd call: os.path.dirname('/fake/project/root/src/core') -> /fake/project/root/src
        # 3rd call: os.path.dirname('/fake/project/root/src') -> /fake/project/root
        mock_dirname.side_effect = [
            '/fake/project/root/src/core',
            '/fake/project/root/src',
            '/fake/project/root'
        ]

        mock_json_load.return_value = {
            "database_file": "test.db",
            "table_name": "summaries",
            "columns": {
                "id": "id",
                "source_url": "source_url",
                "summary_text": "summary_text",
                "style": "style",
                "language": "language",
                "created_at": "created_at"
            }
        }

        # Act
        config = database.get_db_config()

        # Assert
        expected_config_path = os.path.normpath('/fake/project/root/config.json')
        mock_open_file.assert_called_once_with(expected_config_path, 'r')
        mock_json_load.assert_called_once_with(mock_open_file())
        self.assertIsNotNone(config)
        self.assertEqual(config["database_file"], "test.db")

    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    @patch('os.path.dirname') # Patch os.path.dirname
    @patch('os.path.abspath') # Patch os.path.abspath
    def test_get_db_config_file_not_found(self, mock_abspath, mock_dirname, mock_json_load, mock_open_file):
        """Tests get_db_config when config.json is not found."""
        # Arrange
        mock_abspath.return_value = '/fake/project/root/src/core/database.py'
        mock_dirname.side_effect = [
            '/fake/project/root/src/core',
            '/fake/project/root/src',
            '/fake/project/root'
        ]
        mock_open_file.side_effect = FileNotFoundError("config.json not found")

        # Act & Assert
        with self.assertRaises(FileNotFoundError) as cm:
            database.get_db_config()
        
        self.assertIn("config.json not found", str(cm.exception))
        mock_open_file.assert_called_once()
        mock_json_load.assert_not_called()

    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    @patch('os.path.dirname') # Patch os.path.dirname
    @patch('os.path.abspath') # Patch os.path.abspath
    def test_get_db_config_invalid_json(self, mock_abspath, mock_dirname, mock_json_load, mock_open_file):
        """Tests get_db_config when config.json contains invalid JSON."""
        # Arrange
        mock_abspath.return_value = '/fake/project/root/src/core/database.py'
        mock_dirname.side_effect = [
            '/fake/project/root/src/core',
            '/fake/project/root/src',
            '/fake/project/root'
        ]
        mock_json_load.side_effect = json.JSONDecodeError("Invalid JSON", doc="", pos=0)

        # Act & Assert
        with self.assertRaises(json.JSONDecodeError) as cm:
            database.get_db_config()
        
        self.assertIn("Invalid JSON", str(cm.exception))
        mock_open_file.assert_called_once()
        mock_json_load.assert_called_once_with(mock_open_file())

    @patch('src.core.database.get_db_config')
    @patch('src.core.database.sqlite3.connect')
    @patch('src.core.database.os.getenv')
    def test_get_db_connection_success(self, mock_getenv, mock_sqlite_connect, mock_get_db_config):
        """Tests successful database connection."""
        # Arrange
        mock_get_db_config.return_value = {'database_file': 'default.db'}
        mock_getenv.return_value = 'my_test_db.db' # Simulate env var overriding config

        mock_conn = MagicMock()
        mock_sqlite_connect.return_value = mock_conn

        # Act
        conn = database.get_db_connection()

        # Assert
        self.assertEqual(conn, mock_conn)
        mock_getenv.assert_called_once_with('DATABASE_FILE', 'default.db')
        mock_sqlite_connect.assert_called_once_with('my_test_db.db', timeout=10)

    @patch('src.core.database.get_db_config')
    @patch('src.core.database.sqlite3.connect')
    @patch('src.core.database.os.getenv')
    def test_get_db_connection_failure(self, mock_getenv, mock_sqlite_connect, mock_get_db_config):
        """Tests database connection failure."""
        # Arrange
        mock_get_db_config.return_value = {'database_file': 'default.db'}
        mock_getenv.return_value = 'my_test_db.db'
        mock_sqlite_connect.side_effect = database.sqlite3.Error("Simulated connection error")

        # Act & Assert
        with self.assertRaises(database.sqlite3.Error) as cm:
            database.get_db_connection()
        
        self.assertIn("Simulated connection error", str(cm.exception))
        mock_getenv.assert_called_once_with('DATABASE_FILE', 'default.db')
        mock_sqlite_connect.assert_called_once_with('my_test_db.db', timeout=10)

    @patch('src.core.database.get_db_config')
    @patch('src.core.database.get_db_connection')
    def test_create_summary_table_success(self, mock_get_db_connection, mock_get_db_config):
        """
        Tests that the summary table is created correctly based on config.
        """
        # Arrange
        mock_get_db_config.return_value = {
            "table_name": "custom_summaries",
            "columns": {
                "id": "summary_id",
                "source_url": "url",
                "summary_text": "text",
                "style": "style_type",
                "language": "lang",
                "created_at": "timestamp"
            }
        }

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Act
        database.create_summary_table()

        # Assert
        mock_get_db_connection.assert_called_once()
        mock_conn.cursor.assert_called_once()
        
        expected_sql = """
    CREATE TABLE IF NOT EXISTS custom_summaries (
        summary_id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT NOT NULL,
        text TEXT NOT NULL,
        style_type TEXT,
        lang TEXT,
        timestamp TEXT NOT NULL
    );
    """
        
        # Normalize whitespace for comparison
        normalized_expected_sql = " ".join(expected_sql.split())
        normalized_actual_sql = " ".join(mock_cursor.execute.call_args[0][0].split())

        self.assertEqual(normalized_actual_sql, normalized_expected_sql)
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('src.core.database.get_db_config')
    def test_create_summary_table_missing_config(self, mock_get_db_config):
        """
        Tests that a ValueError is raised if the config is missing required columns.
        """
        # Arrange
        mock_get_db_config.return_value = {
            "table_name": "custom_summaries",
            "columns": {
                "id": "summary_id"
                # Missing other required columns
            }
        }

        # Act & Assert
        with self.assertRaises(ValueError) as cm:
            database.create_summary_table()
        
        self.assertIn("missing one or more required column mappings", str(cm.exception))

    @patch('src.core.database.datetime')
    @patch('src.core.database.create_summary_table')
    @patch('src.core.database.get_db_connection')
    @patch('src.core.database.get_db_config')
    def test_save_summary_to_db_success(self, mock_get_db_config, mock_get_db_connection, mock_create_summary_table, mock_datetime):
        """Tests that a summary is saved to the database correctly."""
        # Arrange
        mock_get_db_config.return_value = {
            "table_name": "summaries",
            "columns": {
                "source_url": "source_url",
                "summary_text": "summary_text",
                "style": "style",
                "language": "language",
                "created_at": "created_at"
            }
        }

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        fixed_time = "2025-07-08T12:00:00"
        mock_datetime.now.return_value.isoformat.return_value = fixed_time

        summary_data = {
            'source_url': 'http://example.com',
            'summary_text': ['summary line 1', 'summary line 2'],
            'style': 'bullet_points',
            'language': 'en'
        }

        # Act
        database.save_summary_to_db(summary_data)

        # Assert
        mock_create_summary_table.assert_called_once()
        mock_get_db_connection.assert_called_once()
        mock_conn.cursor.assert_called_once()

        expected_sql = "INSERT INTO summaries (source_url, summary_text, style, language, created_at) VALUES (?, ?, ?, ?, ?)"
        expected_values = (
            'http://example.com',
            json.dumps(['summary line 1', 'summary line 2']),
            'bullet_points',
            'en',
            fixed_time
        )

        mock_cursor.execute.assert_called_once_with(expected_sql, expected_values)
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('src.core.database.get_db_connection')
    @patch('src.core.database.get_db_config')
    def test_get_summaries_success(self, mock_get_db_config, mock_get_db_connection):
        """Tests retrieving summaries from the database successfully."""
        # Arrange
        mock_get_db_config.return_value = {
            "table_name": "summaries",
            "columns": {
                "id": "id",
                "source_url": "source_url",
                "summary_text": "summary_text",
                "style": "style",
                "language": "language",
                "created_at": "created_at"
            }
        }

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Mock database rows and description
        mock_cursor.description = [('id',), ('source_url',), ('summary_text',), ('style',), ('language',), ('created_at',)]
        mock_cursor.fetchall.return_value = [
            (1, 'http://example.com', json.dumps(['line 1']), 'bullet_points', 'en', '2025-07-08T12:00:00'),
            (2, 'http://example.org', json.dumps(['line 2']), 'narrative', 'fr', '2025-07-08T13:00:00')
        ]

        # Act
        summaries = database.get_summaries(limit=5, url_contains='example', style='bullet_points')

        # Assert
        mock_get_db_connection.assert_called_once()
        mock_conn.cursor.assert_called_once()

        expected_sql = (
            "SELECT id, source_url, summary_text, style, language, created_at FROM summaries "
            "WHERE source_url LIKE ? AND style = ? "
            "ORDER BY created_at DESC LIMIT ?"
        )
        expected_params = ['%example%', 'bullet_points', 5]

        # Normalize whitespace for comparison
        normalized_expected_sql = " ".join(expected_sql.split())
        normalized_actual_sql = " ".join(mock_cursor.execute.call_args[0][0].split())

        self.assertEqual(normalized_actual_sql, normalized_expected_sql)
        self.assertEqual(mock_cursor.execute.call_args.args[1], expected_params)
        
        self.assertEqual(len(summaries), 2)
        self.assertEqual(summaries[0]['source_url'], 'http://example.com')
        self.assertEqual(summaries[0]['summary_text'], ['line 1'])

        mock_conn.close.assert_called_once()

if __name__ == '__main__':
    unittest.main()
