import sqlite3 
import os

def execute_schema(db_path: str = "ridewise.db", schema_file: str = "database/schema.sql"):
    """Executes the schema.sql file to create tables in the SQLite DB."""
    # Connect to SQLite DB 
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Read the schema file
    with open(schema_file, 'r') as f:
        schema_sql = f.read()

    # Execute the script
    try:
        cursor.executescript(schema_sql)
        conn.commit()
        print("Schema executed successfully.")
    except Exception as e:
        print(f"Error executing schema: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    execute_schema()
