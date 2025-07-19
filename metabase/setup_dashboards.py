import os
import requests

MB_HOST = os.environ.get('METABASE_HOST', 'http://localhost:3000')
MB_USER = os.environ.get('METABASE_USER', 'admin@example.com')
MB_PASS = os.environ.get('METABASE_PASSWORD', 'admin')

session = requests.Session()
resp = session.post(f"{MB_HOST}/api/session", json={"username": MB_USER, "password": MB_PASS})
resp.raise_for_status()
session.headers.update({'X-Metabase-Session': resp.json()['id']})

def get_database_id(name: str) -> int:
    resp = session.get(f"{MB_HOST}/api/database")
    resp.raise_for_status()
    for db in resp.json():
        if db.get('name') == name:
            return db['id']
    raise SystemExit(f"Database '{name}' not found")

def create_card(name: str, db_id: int, query: str) -> int:
    payload = {
        "name": name,
        "dataset_query": {"database": db_id, "native": {"query": query}},
        "display": "table",
    }
    resp = session.post(f"{MB_HOST}/api/card", json=payload)
    resp.raise_for_status()
    return resp.json()['id']

def create_dashboard(name: str) -> int:
    resp = session.post(f"{MB_HOST}/api/dashboard", json={"name": name})
    resp.raise_for_status()
    return resp.json()['id']

def add_card_to_dashboard(dashboard_id: int, card_id: int, col: int) -> None:
    payload = {"cardId": card_id, "sizeX": 4, "sizeY": 4, "col": col, "row": 0}
    resp = session.post(f"{MB_HOST}/api/dashboard/{dashboard_id}/cards", json=payload)
    resp.raise_for_status()

def main():
    db_id = get_database_id('coffee_olap')

    card_daily = create_card(
        "Daily Revenue",
        db_id,
        """
        SELECT dd.date AS day, SUM(fs.total) AS revenue
        FROM fact_sales fs
        JOIN dim_date dd ON fs.date_id = dd.id
        GROUP BY dd.date
        ORDER BY dd.date;
        """,
    )

    card_product = create_card(
        "Sales by Product",
        db_id,
        """
        SELECT dp.name AS product, SUM(fs.total) AS revenue
        FROM fact_sales fs
        JOIN dim_product dp ON fs.product_dim_id = dp.id
        GROUP BY dp.name
        ORDER BY revenue DESC;
        """,
    )

    card_customer = create_card(
        "Top Customers",
        db_id,
        """
        SELECT dc.name AS customer, SUM(fs.total) AS revenue
        FROM fact_sales fs
        JOIN dim_customer dc ON fs.customer_dim_id = dc.id
        GROUP BY dc.name
        ORDER BY revenue DESC
        LIMIT 10;
        """,
    )

    dashboard_id = create_dashboard("Coffee Shop Overview")
    add_card_to_dashboard(dashboard_id, card_daily, 0)
    add_card_to_dashboard(dashboard_id, card_product, 4)
    add_card_to_dashboard(dashboard_id, card_customer, 8)
    print(f"Created dashboard {dashboard_id}")

if __name__ == "__main__":
    main()
