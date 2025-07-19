import os
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

class Customer(BaseModel):
    name: str
    email: str


@app.post("/customers")
def create_customer(customer: Customer):
    with engine.begin() as conn:
        result = conn.execute(
            text("INSERT INTO customers(name, email) VALUES (:name, :email) RETURNING id"),
            {"name": customer.name, "email": customer.email},
        )
        cid = result.scalar()
    return {"id": cid, **customer.dict()}

