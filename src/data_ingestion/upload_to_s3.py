import boto3
import os

BUCKET_NAME = "ridewisemlopskubeflow"

def upload_file(local_path, s3_path):
    s3 = boto3.client("s3")
    s3.upload_file(local_path, BUCKET_NAME, s3_path)
    print(f"Uploaded {local_path} to s3://{BUCKET_NAME}/{s3_path}")

if __name__ == "__main__":
    files = {
        "data/raw/riders.csv": "raw/riders.csv",
        "data/raw/drivers.csv": "raw/drivers.csv",
        "data/raw/trips.csv": "raw/trips.csv",
        "data/raw/promotions.csv": "raw/promotions.csv",
        "data/raw/sessions.csv": "raw/sessions.csv"
    }

    for local, s3_key in files.items():
        upload_file(local, s3_key)
