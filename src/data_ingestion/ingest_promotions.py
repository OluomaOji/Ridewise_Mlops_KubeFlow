from src.utils.db_utils import get_connection, create_table
from src.utils.s3_utils import read_csv_from_s3

bucket = "ridewisemlopskubeflow"
key = "raw/promotions.csv"

create_sql = """
CREATE TABLE IF NOT EXISTS promotions (
    promo_id TEXT,
    promo_name TEXT,
    promo_type TEXT,
    promo_value FLOAT,
    start_date DATE,
    end_date DATE,
    target_segment TEXT,
    city_scope TEXT,
    ab_test_groups TEXT, 
    test_allocation TEXT,
    success_metric TEXT
);
"""

if __name__ == "__main__":
    conn = get_connection()
    create_table(conn, create_sql)

    df = read_csv_from_s3(bucket, key)
    df.to_sql("promotions", conn, if_exists="replace", index=False)
    print("Promotions data ingested.")
