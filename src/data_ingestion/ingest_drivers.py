from src.utils.db_utils import get_connection, create_table
from src.utils.s3_utils import read_csv_from_s3

bucket = "ridewisemlopskubeflow"
key = "raw/drivers.csv"

create_sql = """
CREATE TABLE IF NOT EXISTS drivers (
    driver_id VARCHAR(64) PRIMARY KEY,
    rating FLOAT,
    vehicle_type TEXT,
    signup_date DATE,
    last_active DATE,
    city TEXT,
    acceptance_rate FLOAT
);
"""

if __name__ == "__main__":
    conn = get_connection()
    create_table(conn, create_sql)

    df = read_csv_from_s3(bucket, key)
    df.to_sql("drivers", conn, if_exists="replace", index=False)
    print("Drivers data ingested.")
