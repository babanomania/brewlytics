import os
from datetime import datetime
from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import create_engine, text

DB_HOST = os.environ.get('OLTP_HOST', 'oltp-db')
DB_PORT = os.environ.get('OLTP_PORT', '5432')
DB_USER = os.environ.get('OLTP_USER', 'brew')
DB_PASSWORD = os.environ.get('OLTP_PASSWORD', 'brew')
DB_NAME = os.environ.get('OLTP_DB', 'coffee_oltp')

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)

app = FastAPI(title="Brewlytics API")


class OrderItem(BaseModel):
    product_id: int
    quantity: int

class Order(BaseModel):
    customer_id: int
    employee_id: int | None = None
    items: list[OrderItem]


@app.post("/orders")
def create_order(order: Order):
    with engine.begin() as conn:
        result = conn.execute(
            text("INSERT INTO orders(customer_id, employee_id, order_time) VALUES (:customer_id, :employee_id, :order_time) RETURNING id"),
            {
                "customer_id": order.customer_id,
                "employee_id": order.employee_id or 1,
                "order_time": datetime.utcnow(),
            },
        )
        order_id = result.scalar()
        for item in order.items:
            conn.execute(
                text(
                    "INSERT INTO order_items(order_id, product_id, quantity, price) "
                    "VALUES (:order_id, :product_id, :quantity, (SELECT price FROM products WHERE id=:product_id))"
                ),
                {
                    "order_id": order_id,
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                },
            )
    return {"order_id": order_id}
