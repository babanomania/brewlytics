import time
import uuid
import random

import pytest
import requests

from . import config


def _generate_product():
    product_base_names = [
        "Espresso",
        "Latte",
        "Cappuccino",
        "Flat White",
        "Mocha",
        "Cold Brew",
        "Chai Latte",
        "Americano",
        "Cortado",
        "Macchiato",
    ]
    product_sizes = ["Small", "Medium", "Large"]
    size = random.choice(product_sizes)
    base = random.choice(product_base_names)
    price = round(random.uniform(2, 7), 2)
    return {"name": f"{size} {base}", "price": price}


@pytest.fixture
def test_product():
    payload = _generate_product()
    resp = requests.post(f"{config.API_URL}/products/new", json=payload)
    assert resp.status_code == 200, f"Product creation failed: {resp.text}"
    return resp.json()


@pytest.fixture
def active_employee_id():
    resp = requests.get(f"{config.API_URL}/employees/active")
    assert resp.status_code == 200 and resp.json(), "Failed to fetch active employees"
    return resp.json()[0]["id"]


def _generate_customer():
    first_names = [
        "Alice",
        "Bob",
        "Priya",
        "John",
        "Maria",
        "Wei",
        "Ahmed",
        "Olivia",
        "Carlos",
        "Nina",
    ]
    last_names = [
        "Smith",
        "Patel",
        "Garcia",
        "Jones",
        "Khan",
        "Kim",
        "Chen",
        "Brown",
        "Singh",
        "Davis",
    ]
    first = random.choice(first_names)
    last = random.choice(last_names)
    return {
        "name": f"{first} {last}",
        "email": f"{first.lower()}.{last.lower()}_{int(time.time()*1000)}@example.com",
    }


@pytest.fixture
def test_customer():
    payload = _generate_customer()
    resp = requests.post(f"{config.API_URL}/customers/new", json=payload)
    assert resp.status_code == 200, f"Customer creation failed: {resp.text}"
    return resp.json()


@pytest.fixture
def test_order(test_product, test_customer, active_employee_id):
    payload = {
        "customer_id": test_customer["id"],
        "employee_id": active_employee_id,
        "items": [
            {
                "product_id": test_product["id"],
                "quantity": random.randint(1, 5),
            }
        ],
    }
    resp = requests.post(f"{config.API_URL}/orders/new", json=payload)
    assert resp.status_code == 200, f"Order creation failed: {resp.text}"
    return resp.json()["order_id"]
