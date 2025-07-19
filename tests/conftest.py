import time
import uuid

import pytest
import requests

from . import config


@pytest.fixture
def test_product():
    payload = {"name": f"Test Product {uuid.uuid4().hex[:8]}", "price": 3.5}
    resp = requests.post(f"{config.API_URL}/products", json=payload)
    assert resp.status_code == 200, f"Product creation failed: {resp.text}"
    return resp.json()


@pytest.fixture
def test_customer():
    payload = {
        "name": "PyTest User",
        "email": f"pytest_{int(time.time()*1000)}@example.com",
    }
    resp = requests.post(f"{config.API_URL}/customers", json=payload)
    assert resp.status_code == 200, f"Customer creation failed: {resp.text}"
    return resp.json()


@pytest.fixture
def test_order(test_product, test_customer):
    payload = {
        "customer_id": test_customer["id"],
        "items": [{"product_id": test_product["id"], "quantity": 1}],
    }
    resp = requests.post(f"{config.API_URL}/orders", json=payload)
    assert resp.status_code == 200, f"Order creation failed: {resp.text}"
    return resp.json()["order_id"]
