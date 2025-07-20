import time
import uuid

import pytest
import requests

from . import config


@pytest.fixture
def test_product():
    payload = {"name": f"Test Product {uuid.uuid4().hex[:8]}", "price": 3.5}
    resp = requests.post(f"{config.API_URL}/products/new", json=payload)
    assert resp.status_code == 200, f"Product creation failed: {resp.text}"
    return resp.json()


@pytest.fixture
def active_employee_id():
    resp = requests.get(f"{config.API_URL}/employees/active")
    assert resp.status_code == 200 and resp.json(), "Failed to fetch active employees"
    return resp.json()[0]["id"]


@pytest.fixture
def test_customer():
    payload = {
        "name": "PyTest User",
        "email": f"pytest_{int(time.time()*1000)}@example.com",
    }
    resp = requests.post(f"{config.API_URL}/customers/new", json=payload)
    assert resp.status_code == 200, f"Customer creation failed: {resp.text}"
    return resp.json()


@pytest.fixture
def test_order(test_product, test_customer, active_employee_id):
    payload = {
        "customer_id": test_customer["id"],
        "employee_id": active_employee_id,
        "items": [{"product_id": test_product["id"], "quantity": 1}],
    }
    resp = requests.post(f"{config.API_URL}/orders/new", json=payload)
    assert resp.status_code == 200, f"Order creation failed: {resp.text}"
    return resp.json()["order_id"]
