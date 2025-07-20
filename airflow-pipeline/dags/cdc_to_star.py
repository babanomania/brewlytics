from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import json
import os
import psycopg2

def etl_cdc_to_star():
    oltp = psycopg2.connect(
        host=os.environ.get('OLTP_HOST', 'oltp-db'),
        database=os.environ.get('OLTP_DB'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASSWORD'),
    )
    olap = psycopg2.connect(
        host=os.environ.get('OLAP_HOST', 'olap-db'),
        database=os.environ.get('OLAP_DB'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASSWORD'),
    )
    oltp.autocommit = True
    olap.autocommit = True

    src = oltp.cursor()
    dst = olap.cursor()

    # fetch last processed id from offset table
    src.execute("SELECT last_id FROM cdc_offset WHERE table_name='cdc_orders'")
    row = src.fetchone()
    last_id = row[0] if row else 0
    if row is None:
        src.execute("INSERT INTO cdc_offset(table_name, last_id) VALUES ('cdc_orders', 0)")

    src.execute("SELECT id, payload, op FROM cdc_orders WHERE id > %s ORDER BY id", (last_id,))
    rows = src.fetchall()
    for row_id, payload, op in rows:
        order = payload
        product_name = None
        if 'product_id' in order:
            src.execute("SELECT name FROM products WHERE id=%s", (order['product_id'],))
            prod = src.fetchone()
            product_name = prod[0] if prod else None
        if op == 'DELETE':
            src.execute("UPDATE cdc_orders SET processed=true WHERE id=%s", (row_id,))
            src.execute("UPDATE cdc_offset SET last_id=%s WHERE table_name='cdc_orders'", (row_id,))
            continue
        # rows logged from the orders table won't contain product info
        if 'product_id' not in order:
            # still make sure basic dimensions exist
            src.execute("SELECT name, email FROM customers WHERE id=%s", (order['customer_id'],))
            cust = src.fetchone() or (None, None)
            dst.execute(
                """
                INSERT INTO dim_customer (customer_id, name, email)
                VALUES (%s, %s, %s)
                ON CONFLICT (customer_id)
                DO UPDATE SET name=EXCLUDED.name, email=EXCLUDED.email
                """,
                (order['customer_id'], cust[0], cust[1]),
            )
            src.execute("SELECT name FROM employees WHERE id=%s", (order['employee_id'],))
            emp = src.fetchone()
            dst.execute(
                """
                INSERT INTO dim_employee (employee_id, name)
                VALUES (%s, %s)
                ON CONFLICT (employee_id)
                DO UPDATE SET name=EXCLUDED.name
                """,
                (order['employee_id'], emp[0] if emp else None),
            )
            dst.execute(
                "INSERT INTO dim_date (date) VALUES (%s::date) ON CONFLICT (date) DO NOTHING",
                (order['order_time'],),
            )
            src.execute("UPDATE cdc_orders SET processed=true WHERE id=%s", (row_id,))
            src.execute(
                "UPDATE cdc_offset SET last_id=%s WHERE table_name='cdc_orders'",
                (row_id,),
            )
            continue
        # dimensions
        src.execute("SELECT name, email FROM customers WHERE id=%s", (order['customer_id'],))
        cust = src.fetchone() or (None, None)
        dst.execute(
            """
            INSERT INTO dim_customer (customer_id, name, email)
            VALUES (%s, %s, %s)
            ON CONFLICT (customer_id)
            DO UPDATE SET name=EXCLUDED.name, email=EXCLUDED.email
            RETURNING id
            """,
            (order['customer_id'], cust[0], cust[1]),
        )
        customer_dim = dst.fetchone()[0]
        src.execute("SELECT name FROM employees WHERE id=%s", (order['employee_id'],))
        emp = src.fetchone()
        dst.execute(
            """
            INSERT INTO dim_employee (employee_id, name)
            VALUES (%s, %s)
            ON CONFLICT (employee_id)
            DO UPDATE SET name=EXCLUDED.name
            RETURNING id
            """,
            (order['employee_id'], emp[0] if emp else None),
        )
        employee_dim = dst.fetchone()[0]
        dst.execute(
            """
            INSERT INTO dim_product (product_id, name, price)
            VALUES (%s, %s, %s)
            ON CONFLICT (product_id)
            DO UPDATE SET name=EXCLUDED.name, price=EXCLUDED.price
            RETURNING id
            """,
            (order['product_id'], product_name, order['price']),
        )
        product_dim = dst.fetchone()[0]
        dst.execute(
            """
            INSERT INTO dim_date (date)
            VALUES (%s::date)
            ON CONFLICT (date) DO UPDATE SET date=EXCLUDED.date
            RETURNING id
            """,
            (order['order_time'],),
        )
        date_dim = dst.fetchone()[0]
        dst.execute(
            """
            INSERT INTO fact_sales(date_id, customer_dim_id, product_dim_id, employee_dim_id, quantity, price, total, order_time)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                date_dim,
                customer_dim,
                product_dim,
                employee_dim,
                order['quantity'],
                order['price'],
                order['quantity'] * order['price'],
                order['order_time'],
            ),
        )
        src.execute("UPDATE cdc_orders SET processed=true WHERE id=%s", (row_id,))
        src.execute(
            "UPDATE cdc_offset SET last_id=%s WHERE table_name='cdc_orders'",
            (row_id,)
        )
    src.close()
    dst.close()
    oltp.close()
    olap.close()

default_args = {
    'owner': 'brewlytics',
    'start_date': datetime(2023, 1, 1),
}

with DAG(
    'cdc_to_star',
    default_args=default_args,
    schedule_interval='*/5 * * * *',
    catchup=False,
    tags=['brewlytics'],
) as dag:
    PythonOperator(task_id='etl_cdc_to_star', python_callable=etl_cdc_to_star)

