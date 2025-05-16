from src.utils.db_utils import get_connection, create_table
from src.utils.s3_utils import read_csv_from_s3

bucket = "ridewisemlopskubeflow"
key = "raw/trips.csv"

create_sql = """
CREATE TABLE IF NOT EXISTS trips (
    trip_id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64) REFERENCES riders(user_id),
    driver_id VARCHAR(64) REFERENCES drivers(driver_id),
    fare FLOAT,
    surge_multiplier FLOAT,
    tip FLOAT,
    payment_type TEXT,
    pickup_time TIMESTAMP,
    dropoff_time TIMESTAMP,
    pickup_lat FLOAT,
    pickup_lng FLOAT,
    dropoff_lat FLOAT,
    dropoff_lng FLOAT,
    weather TEXT,
    city TEXT,
    loyalty_status TEXT
);
"""

if __name__ == "__main__":
    conn = get_connection()
    create_table(conn, create_sql)

    df = read_csv_from_s3(bucket, key)
    df.to_sql("trips", conn, if_exists="replace", index=False)
    print("Trips data ingested.")
