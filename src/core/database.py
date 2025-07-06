import sqlite3
import json
import os
from datetime import datetime
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

# --- Configuration Loading ---

def get_db_config():
    """Loads the database mapping configuration from config.json."""
    # Construct the path to the config file relative to this script's location
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.json')
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error(f"Configuration file config.json not found at {config_path}.")
        raise ValueError("Configuration file config.json not found in the project root.")
    except json.JSONDecodeError:
        logging.error(f"Error decoding config.json. Please check for syntax errors in {config_path}.")
        raise ValueError("Error decoding config.json. Please check for syntax errors.")

# --- Database Initialization ---

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    config = get_db_config()
    # Prioritize DATABASE_FILE from .env, otherwise use config.json, fallback to default
    db_file = os.getenv('DATABASE_FILE', config.get('database_file', 'summaries.db'))
    logging.info(f"Connecting to database: {db_file}")
    conn = sqlite3.connect(db_file)
    return conn

def create_summary_table():
    """Creates the summary table if it doesn't exist, using names from config."""
    config = get_db_config()
    table_name = config.get('table_name', 'summaries')
    cols = config.get('columns', {})

    # Validate required columns are in config
    required_cols = ['id', 'source_url', 'summary_text', 'style', 'language', 'created_at']
    if not all(key in cols for key in required_cols):
        logging.error("Config file is missing one or more required column mappings.")
        raise ValueError("Config file is missing one or more required column mappings.")

    # Build the CREATE TABLE statement dynamically
    # Using TEXT for all fields for simplicity, as SQLite is flexible.
    # Using INTEGER PRIMARY KEY for the ID is standard practice.
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
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(create_table_sql)
        conn.commit()
        logging.info(f"Table '{table_name}' ensured to exist.")
    except sqlite3.Error as e:
        logging.error(f"Database error during table creation: {e}")
    finally:
        if conn:
            conn.close()

# --- Data Insertion ---

def save_summary_to_db(summary_data):
    """
    Saves a summary record to the database.
    :param summary_data: A dictionary containing the summary info, 
                         e.g., {'source_url': 'http://...', 'summary_text': '...', ...}
    """
    config = get_db_config()
    table_name = config.get('table_name', 'summaries')
    cols = config.get('columns', {})

    # Prepare column names and placeholders for the INSERT statement
    db_columns = [
        cols['source_url'], 
        cols['summary_text'], 
        cols['style'], 
        cols['language'], 
        cols['created_at']
    ]
    placeholders = ', '.join(['?' for _ in db_columns])
    
    insert_sql = f"INSERT INTO {table_name} ({', '.join(db_columns)}) VALUES ({placeholders})"

    # Prepare the values to be inserted
    values = (
        summary_data.get('source_url'),
        json.dumps(summary_data.get('summary_text')),
        summary_data.get('style'),
        summary_data.get('language'),
        datetime.now().isoformat() # Add a timestamp
    )

    conn = None
    try:
        conn = get_db_connection()
        # Ensure the table exists before trying to insert
        create_summary_table()
        
        cursor = conn.cursor()
        cursor.execute(insert_sql, values)
        conn.commit()
        logging.info(f"Summary for '{summary_data.get('source_url')}' successfully saved to database.")
    except sqlite3.Error as e:
        logging.error(f"Database error during insert: {e}")
    finally:
        if conn:
            conn.close()

# --- Data Retrieval ---

def get_summaries(limit=None, url_contains=None, style=None):
    """
    Retrieves summaries from the database based on filters.
    :param limit: Maximum number of summaries to retrieve.
    :param url_contains: Filter summaries where the source URL contains this string.
    :param style: Filter summaries by style.
    :return: A list of dictionaries, each representing a summary.
    """
    config = get_db_config()
    table_name = config.get('table_name', 'summaries')
    cols = config.get('columns', {})

    select_sql = f"SELECT {cols['id']}, {cols['source_url']}, {cols['summary_text']}, {cols['style']}, {cols['language']}, {cols['created_at']} FROM {table_name}"
    conditions = []
    params = []

    if url_contains:
        conditions.append(f"{cols['source_url']} LIKE ?")
        params.append(f'%{url_contains}%')
    if style:
        conditions.append(f"{cols['style']} = ?")
        params.append(style)

    if conditions:
        select_sql += " WHERE " + " AND ".join(conditions)

    select_sql += f" ORDER BY {cols['created_at']} DESC"

    if limit:
        select_sql += " LIMIT ?"
        params.append(limit)

    conn = None
    summaries = []
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(select_sql, params)
        rows = cursor.fetchall()

        for row in rows:
            summary_dict = {
                'id': row[0],
                'source_url': row[1],
                'summary_text': json.loads(row[2]), # Load JSON string back to dict
                'style': row[3],
                'language': row[4],
                'created_at': row[5]
            }
            summaries.append(summary_dict)
    except sqlite3.Error as e:
        logging.error(f"Database error during retrieval: {e}")
    finally:
        if conn:
            conn.close()
    return summaries