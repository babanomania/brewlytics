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
    # create a product first
    prod_payload = {"name": "Test Coffee", "price": 3.5}
    resp = requests.post(f"{API_URL}/products", json=prod_payload)
    assert resp.status_code == 200
    product_id = resp.json()["id"]

    # then create a customer
    cust_payload = {"name": "PyTest User", "email": "pytest@example.com"}
    resp = requests.post(f"{API_URL}/customers", json=cust_payload)
    assert resp.status_code == 200
    customer_id = resp.json()["id"]

    # finally create the order using the above entities
    order_payload = {
        "customer_id": customer_id,
        "items": [{"product_id": product_id, "quantity": 1}],
    }
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
            cur.execute(
                """
                SELECT fs.quantity, dp.product_id, dc.customer_id
                FROM fact_sales fs
                JOIN dim_customer dc ON fs.customer_dim_id = dc.id
                JOIN dim_product dp ON fs.product_dim_id = dp.id
                WHERE dc.customer_id=%s AND dp.product_id=%s
                ORDER BY fs.id DESC LIMIT 1
                """,
                (customer_id, product_id),
            )
            row = cur.fetchone()
            assert row is not None
            assert row[0] == 1
