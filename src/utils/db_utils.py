import sqlite3

def get_connection(db_path="ridewise.db"):
    return sqlite3.connect(db_path)

def create_table(conn, create_sql):
    with conn:
        conn.execute(create_sql)
