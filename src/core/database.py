"""Manages the SQLite database for storing and retrieving article summaries.

This module handles the connection to the database, the creation of the
summary table, and provides functions to save and query summary data.
It uses a `config.json` file for database configuration, allowing for
flexible table and column naming.
"""

import json
import logging
import os
import sqlite3
from datetime import datetime
from typing import TypedDict, Union, List, cast, Any

from dotenv import load_dotenv

class SummaryRecord(TypedDict):
    id: int
    source_url: str
    summary_text: Union[str, List[str]]
    style: str
    language: str
    created_at: str

# Load environment variables from .env file, which may contain DATABASE_FILE
load_dotenv()

# --- Configuration Loading ---


def get_db_config() -> dict:
    """Load database configuration from `config.json`.

    The configuration file is expected in the project root.

    Returns:
        dict: A dictionary with database configuration.

    Raises:
        FileNotFoundError: If config.json is not found.
        json.JSONDecodeError: If config.json is not valid JSON.
    """
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config.json"
    )
    try:
        with open(config_path) as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error(f"Configuration file 'config.json' not found at {config_path}")
        raise
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding 'config.json': {e}")
        raise


# --- Database Initialization ---


def get_db_connection() -> sqlite3.Connection:
    """Establish a connection to the SQLite database.

    The database file path is determined by the `DATABASE_FILE` environment
    variable, falling back to the `database_file` in `config.json`,
    and finally to a default of 'summaries.db'.

    Returns:
        sqlite3.Connection: A connection object to the database.
    """
    config = get_db_config()
    db_file = os.getenv("DATABASE_FILE", config.get("database_file", "summaries.db"))
    logging.info(f"Connecting to database: {db_file}")
    try:
        conn = sqlite3.connect(db_file, timeout=10)
        return conn
    except sqlite3.Error as e:
        logging.error(f"Failed to connect to database '{db_file}': {e}")
        raise


def create_summary_table() -> None:
    """Create the summary table if it doesn't exist, using names from config.

    Raises:
        ValueError: If the configuration is missing required column mappings.
    """
    config = get_db_config()
    table_name = config.get("table_name", "summaries")
    cols = config.get("columns", {})

    required_cols = [
        "id",
        "source_url",
        "summary_text",
        "style",
        "language",
        "created_at",
    ]
    if not all(key in cols for key in required_cols):
        msg = "Config file is missing one or more required column mappings."
        logging.error(msg)
        raise ValueError(msg)

    create_table_sql = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        {cols['id']} INTEGER PRIMARY KEY AUTOINCREMENT,
        {cols['source_url']} TEXT NOT NULL,
        {cols['summary_text']} TEXT NOT NULL,
        {cols['style']} TEXT,
        {cols['language']} TEXT,
        {cols['created_at']} TEXT NOT NULL
    );
    """

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(create_table_sql)
        conn.commit()
        logging.info(f"Table '{table_name}' is ready.")
    except sqlite3.Error as e:
        logging.error(f"Database error during table creation for '{table_name}': {e}")
    finally:
        if conn:
            conn.close()


# --- Data Insertion ---


def save_summary_to_db(summary_data: dict) -> None:
    """Save a summary record to the database.

    Args:
        summary_data (dict): A dictionary containing the summary info.
                             Keys should match the general purpose, e.g.,
                             'source_url', 'summary_text', etc.
    """
    config = get_db_config()
    table_name = config.get("table_name", "summaries")
    cols = config.get("columns", {})

    db_columns = [
        cols["source_url"],
        cols["summary_text"],
        cols["style"],
        cols["language"],
        cols["created_at"],
    ]
    placeholders = ", ".join(["?" for _ in db_columns])

    insert_sql = (
        f"INSERT INTO {table_name} ({ ', '.join(db_columns)}) VALUES ({placeholders})"
    )

    values = (
        summary_data.get("source_url"),
        json.dumps(summary_data.get("summary_text")),
        summary_data.get("style"),
        summary_data.get("language"),
        datetime.now().isoformat(),
    )

    conn = None
    try:
        conn = get_db_connection()
        create_summary_table()  # Ensure table exists
        cursor = conn.cursor()
        cursor.execute(insert_sql, values)
        conn.commit()
        logging.info(
            f"Summary for '{summary_data.get('source_url')}' saved to database."
        )
    except sqlite3.IntegrityError as e:
        logging.error(f"Database integrity error (e.g., duplicate entry): {e}")
    except sqlite3.Error as e:
        logging.error(f"A database error occurred: {e}")
    finally:
        if conn:
            conn.close()


# --- Data Retrieval ---


def get_summaries(
    limit: int | None = None, url_contains: str | None = None, style: str | None = None
) -> list[SummaryRecord]:
    """Retrieve summaries from the database based on optional filters.

    Args:
        limit (int, optional): Maximum number of summaries to retrieve.
        url_contains (str, optional): Filter for URLs containing this string.
        style (str, optional): Filter summaries by a specific style.

    Returns:
        list[dict]: A list of dictionaries, each representing a summary.
    """
    config = get_db_config()
    table_name = config.get("table_name", "summaries")
    cols = config.get("columns", {})

    query_parts = [
        f"SELECT {cols['id']}, {cols['source_url']}, {cols['summary_text']},",
        f"{cols['style']}, {cols['language']}, {cols['created_at']} FROM {table_name}",
    ]
    conditions, params = [], []

    if url_contains:
        conditions.append(f"{cols['source_url']} LIKE ?")
        params.append(f"%{url_contains}%")
    if style:
        conditions.append(f"{cols['style']} = ?")
        params.append(style)

    if conditions:
        query_parts.append("WHERE " + " AND ".join(conditions))

    query_parts.append(f"ORDER BY {cols['created_at']} DESC")

    if limit:
        query_parts.append("LIMIT ?")
        params.append(limit)

    select_sql = " ".join(query_parts)
    summaries: list[database.SummaryRecord] = []
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(select_sql, params)
        rows = cursor.fetchall()

        column_names = [description[0] for description in cursor.description]
        for row in rows:
            # Mypy struggles with dynamic dict creation and TypedDict.
            # We cast to dict[str, Any] to satisfy mypy, as the runtime type is correct.
            summary_dict: dict[str, Any] = dict(zip(column_names, row, strict=False))
            
            # Deserialize the JSON summary text
            try:
                summary_text_raw = summary_dict["summary_text"]
                if isinstance(summary_text_raw, str):
                    summary_dict["summary_text"] = json.loads(summary_text_raw)
                else:
                    logging.warning("summary_text is not a string, skipping JSON decode.")
            except (json.JSONDecodeError, TypeError):
                logging.warning("Could not decode summary_text for summary ID.")
                # Keep it as a raw string if it's not valid JSON
            
            # Cast to SummaryRecord before appending to satisfy mypy's list type
            summaries.append(cast(SummaryRecord, summary_dict))

    except sqlite3.Error as e:
        logging.error(f"Database error during retrieval: {e}")
    finally:
        if conn:
            conn.close()
    return summaries
