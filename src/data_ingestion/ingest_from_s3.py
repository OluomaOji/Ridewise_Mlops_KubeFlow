import boto3
import pandas as pd
import os
import sqlite3
from io import BytesIO

DB_TYPE = os.getenv("DB_TYPE", "sqlite")
BUCKET_NAME = "ridewisemlopskubeflow"

def download_csv_from_s3(s3_key):
    s3 = boto3.client("s3")
    obj = s3.get_object(Bucket=BUCKET_NAME, Key=s3_key)
    return pd.read_csv(BytesIO(obj['Body'].read()))

def insert_to_sqlite(table_name, df):
    conn = sqlite3.connect("db.sqlite3")
    df.to_sql(table_name, conn, if_exists="append", index=False)
    conn.close()

def load_table(table_name, s3_key):
    df = download_csv_from_s3(s3_key)
    insert_to_sqlite(table_name, df)
    print(f"Loaded {table_name} from {s3_key}")

if __name__ == "__main__":
    table_s3_map = {
        "riders": "raw/riders.csv",
        "drivers": "raw/drivers.csv",
        "trips": "raw/trips.csv",
        "promotions": "raw/promotions.csv",
        "sessions": "raw/sessions.csv"
    }

    for table, s3_key in table_s3_map.items():
        load_table(table, s3_key)
