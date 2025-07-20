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

class Employee(BaseModel):
    name: str
    active: bool | None = True



@app.get("/employees/active")
def get_active_employees():
    with engine.begin() as conn:
        result = conn.execute(
            text("SELECT id, name FROM employees WHERE active = true")
        )
        employees = [
            {"id": row.id, "name": row.name}
            for row in result
        ]
    return employees

