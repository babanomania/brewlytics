import json
import os
import sys
from typing import Any, Dict

import requests


def login(session: requests.Session, host: str, user: str, password: str) -> str:
    """Authenticate to Metabase and return the session token."""
    resp = session.post(f"{host}/api/session", json={"username": user, "password": password})
    try:
        resp.raise_for_status()
    except requests.HTTPError as exc:
        print(f"Failed to authenticate: {exc}\n{resp.text}", file=sys.stderr)
        sys.exit(1)
    return resp.json().get("id")


def get_database_id(session: requests.Session, host: str, name: str) -> int:
    """Return the database ID for the given name."""
    resp = session.get(f"{host}/api/database")
    try:
        resp.raise_for_status()
    except requests.HTTPError as exc:
        print(f"Failed to fetch databases: {exc}\n{resp.text}", file=sys.stderr)
        sys.exit(1)
    for db in resp.json():
        if db.get("name") == name:
            return db["id"]
    print(f"Database '{name}' not found", file=sys.stderr)
    sys.exit(1)


def create_dashboard(session: requests.Session, host: str, name: str) -> int:
    resp = session.post(f"{host}/api/dashboard", json={"name": name})
    try:
        resp.raise_for_status()
    except requests.HTTPError as exc:
        print(f"Failed to create dashboard: {exc}\n{resp.text}", file=sys.stderr)
        sys.exit(1)
    return resp.json()["id"]


def create_card(session: requests.Session, host: str, db_id: int, card: Dict[str, Any]) -> int:
    payload = {
        "name": card["name"],
        "dataset_query": {"database": db_id, "native": {"query": card["query"]}},
        "display": "table",
    }
    resp = session.post(f"{host}/api/card", json=payload)
    try:
        resp.raise_for_status()
    except requests.HTTPError as exc:
        print(f"Failed to create card '{card['name']}': {exc}\n{resp.text}", file=sys.stderr)
        sys.exit(1)
    return resp.json()["id"]


def add_card(session: requests.Session, host: str, dashboard_id: int, card_id: int, col: int) -> None:
    payload = {"cardId": card_id, "sizeX": 4, "sizeY": 4, "col": col, "row": 0}
    resp = session.post(f"{host}/api/dashboard/{dashboard_id}/cards", json=payload)
    try:
        resp.raise_for_status()
    except requests.HTTPError as exc:
        print(
            f"Failed to add card {card_id} to dashboard {dashboard_id}: {exc}\n{resp.text}",
            file=sys.stderr,
        )
        sys.exit(1)


def load_config(path: str) -> Dict[str, Any]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Config file '{path}' not found", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as exc:
        print(f"Invalid JSON in config file: {exc}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    host = os.environ.get("METABASE_HOST", "http://localhost:3000")
    user = os.environ.get("METABASE_USER", "admin@example.com")
    password = os.environ.get("METABASE_PASSWORD", "admin")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_config = os.path.join(script_dir, "dashboard.json")
    config_path = os.environ.get("DASHBOARD_CONFIG", default_config)

    config = load_config(config_path)

    session = requests.Session()
    token = login(session, host, user, password)
    session.headers.update({"X-Metabase-Session": token})

    db_id = get_database_id(session, host, "coffee_olap")
    dashboard_id = create_dashboard(session, host, config["dashboard_name"])

    for card in config.get("cards", []):
        card_id = create_card(session, host, db_id, card)
        add_card(session, host, dashboard_id, card_id, card.get("position", 0))

    print(f"Dashboard created successfully with ID {dashboard_id}")


if __name__ == "__main__":
    main()
