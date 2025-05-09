from src.utils.db_utils import get_connection, create_table
from src.utils.s3_utils import read_csv_from_s3

bucket = "ridewisemlopskubeflow"
key = "raw/riders.csv"

create_sql = """
CREATE TABLE IF NOT EXISTS riders (
    user_id TEXT PRIMARY KEY,
    signup_date TEXT,
    loyalty_status TEXT,
    age INTEGER,
    country TEXT,
    referred_by TEXT
);
"""

if __name__ == "__main__":
    conn = get_connection()
    create_table(conn, create_sql)

    df = read_csv_from_s3(bucket, key)
    df.to_sql("riders", conn, if_exists="replace", index=False)
    print("Riders data ingested.")
