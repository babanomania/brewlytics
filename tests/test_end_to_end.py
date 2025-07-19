import os
import time
import requests
import psycopg2

API_URL = os.getenv("API_URL", "http://localhost:8000")
OLTP_DSN = os.getenv(
    "OLTP_DSN",
    "dbname=coffee_oltp user=brew password=brew host=localhost port=5432",
)
OLAP_DSN = os.getenv(
    "OLAP_DSN",
    "dbname=coffee_olap user=brew password=brew host=localhost port=5433",
)

def test_order_flow():
    order_payload = {"customer_id": 1, "items": [{"product_id": 1, "quantity": 1}]}
    resp = requests.post(f"{API_URL}/orders", json=order_payload)
    assert resp.status_code == 200
    order_id = resp.json()["order_id"]

    with psycopg2.connect(OLTP_DSN) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT payload FROM cdc_orders WHERE payload->>'order_id'=%s",
                (str(order_id),),
            )
            assert cur.fetchone() is not None

    # Wait a bit for the DAG to process
    time.sleep(5)

    with psycopg2.connect(OLAP_DSN) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM fact_sales WHERE order_time IS NOT NULL")
            assert cur.fetchone()[0] > 0
