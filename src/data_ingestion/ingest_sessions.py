from src.utils.db_utils import get_connection, create_table
from src.utils.s3_utils import read_csv_from_s3

bucket = "ridewisemlopskubeflow"
key = "raw/sessions.csv"

create_sql = """
CREATE TABLE IF NOT EXISTS sessions (
    session_id VARCHAR(64) PRIMARY KEY,
    rider_id VARCHAR(64) REFERENCES riders(user_id),
    session_time TIMESTAMP,
    time_on_app INTEGER,
    pages_visited INTEGER,
    converted BOOLEAN,
    city TEXT,
    loyalty_status TEXT
);
"""

if __name__ == "__main__":
    conn = get_connection()
    create_table(conn, create_sql)

    df = read_csv_from_s3(bucket, key)
    df.to_sql("sessions", conn, if_exists="replace", index=False)
    print("Sessions data ingested.")
