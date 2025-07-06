import sqlite3
import json
import os
from datetime import datetime

# --- Configuration Loading ---

def get_db_config():
    """Loads the database mapping configuration from config.json."""
    # Construct the path to the config file relative to this script's location
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.json')
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        raise ValueError("Configuration file config.json not found in the project root.")
    except json.JSONDecodeError:
        raise ValueError("Error decoding config.json. Please check for syntax errors.")

# --- Database Initialization ---

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    config = get_db_config()
    # Prioritize DATABASE_FILE from .env, otherwise use config.json, fallback to default
    db_file = os.getenv('DATABASE_FILE', config.get('database_file', 'summaries.db'))
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
    except sqlite3.Error as e:
        print(f"Database error during table creation: {e}")
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
        print(f"Summary for '{summary_data.get('source_url')}' successfully saved to database.")
    except sqlite3.Error as e:
        print(f"Database error during insert: {e}")
    finally:
        if conn:
            conn.close()
