import os
import random
from datetime import datetime
from sqlalchemy import create_engine, text

DB_HOST = os.environ.get('OLTP_HOST', 'oltp-db')
DB_PORT = os.environ.get('OLTP_PORT', '5432')
DB_USER = os.environ.get('OLTP_USER', 'brew')
DB_PASSWORD = os.environ.get('OLTP_PASSWORD', 'brew')
DB_NAME = os.environ.get('OLTP_DB', 'coffee_oltp')

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)

CUSTOMERS = [
    {"name": "Charlie", "email": "charlie@example.com"},
    {"name": "Dana", "email": "dana@example.com"},
    {"name": "Eve", "email": "eve@example.com"},
]

PRODUCTS = [
    {"name": "Americano", "price": 3.5},
    {"name": "Cappuccino", "price": 4.0},
    {"name": "Muffin", "price": 2.75},
]


def seed_customers(conn):
    ids = []
    for cust in CUSTOMERS:
        result = conn.execute(
            text("INSERT INTO customers(name, email) VALUES (:name, :email) RETURNING id"),
            cust,
        )
        ids.append(result.scalar())
    return ids


def seed_products(conn):
    ids = []
    for prod in PRODUCTS:
        result = conn.execute(
            text("INSERT INTO products(name, price) VALUES (:name, :price) RETURNING id"),
            prod,
        )
        ids.append(result.scalar())
    return ids


def seed_orders(conn, customer_ids, product_ids):
    for _ in range(5):
        cid = random.choice(customer_ids)
        result = conn.execute(
            text(
                "INSERT INTO orders(customer_id, employee_id, order_time) VALUES (:cid, 1, :otime) RETURNING id"
            ),
            {"cid": cid, "otime": datetime.utcnow()},
        )
        order_id = result.scalar()
        for _ in range(random.randint(1, 3)):
            pid = random.choice(product_ids)
            qty = random.randint(1, 3)
            conn.execute(
                text(
                    "INSERT INTO order_items(order_id, product_id, quantity, price) VALUES (:oid, :pid, :qty, (SELECT price FROM products WHERE id=:pid))"
                ),
                {"oid": order_id, "pid": pid, "qty": qty},
            )


def main():
    with engine.begin() as conn:
        customer_ids = seed_customers(conn)
        product_ids = seed_products(conn)
        seed_orders(conn, customer_ids, product_ids)
    print("Sample data inserted")


if __name__ == "__main__":
    main()
