import time
import psycopg2

from . import config


def test_cdc_entry_exists(test_order):
    time.sleep(2)
    with psycopg2.connect(config.OLTP_DSN) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT payload FROM cdc_orders WHERE payload->>'order_id'=%s",
                (str(test_order),),
            )
            row = cur.fetchone()
    assert row is not None, "CDC entry should exist for the created order"
