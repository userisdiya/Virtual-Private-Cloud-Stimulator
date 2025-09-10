import sqlite3

def get_db_connection():
    conn = sqlite3.connect('vpc_simulator.db')  # Path to your SQLite database
    conn.row_factory = sqlite3.Row  # This allows accessing rows by column name (as a dictionary)
    return conn
