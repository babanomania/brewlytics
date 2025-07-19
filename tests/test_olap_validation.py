import time
import psycopg2

from . import config


def test_olap_fact_sales_entry(test_order, test_customer, test_product):
    time.sleep(5)
    with psycopg2.connect(config.OLAP_DSN) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT fs.quantity
                FROM fact_sales fs
                JOIN dim_customer dc ON fs.customer_dim_id = dc.id
                JOIN dim_product dp ON fs.product_dim_id = dp.id
                WHERE dc.customer_id=%s AND dp.product_id=%s
                ORDER BY fs.id DESC LIMIT 1
                """,
                (test_customer["id"], test_product["id"]),
            )
            row = cur.fetchone()
    assert row is not None, "fact_sales entry not found for the created order"
    assert row[0] == 1, "Quantity in fact_sales does not match"
