import os

API_URL = os.getenv("API_URL", "http://localhost:8000")
OLTP_DSN = os.getenv(
    "OLTP_DSN",
    "dbname=coffee_oltp user=brew password=brew host=localhost port=5432",
)
OLAP_DSN = os.getenv(
    "OLAP_DSN",
    "dbname=coffee_olap user=brew password=brew host=localhost port=5433",
)
