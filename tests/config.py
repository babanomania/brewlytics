import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

API_URL = os.getenv("API_URL", "http://gateway")

# Required database configuration values
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
OLTP_DB = os.getenv("OLTP_DB")
OLAP_DB = os.getenv("OLAP_DB")

if not all([DB_USER, DB_PASSWORD, OLTP_DB, OLAP_DB]):
    raise RuntimeError(
        "DB_USER, DB_PASSWORD, OLTP_DB and OLAP_DB must be provided in the .env file"
    )

OLTP_DSN = os.getenv(
    "OLTP_DSN",
    f"dbname={os.getenv('OLTP_DB')} "
    f"user={os.getenv('DB_USER')} "
    f"password={os.getenv('DB_PASSWORD')} "
    f"host={os.getenv('OLTP_HOST', 'oltp-db')} "
    f"port={os.getenv('OLTP_PORT', 5432)}",
)

OLAP_DSN = os.getenv(
    "OLAP_DSN",
    f"dbname={os.getenv('OLAP_DB')} "
    f"user={os.getenv('DB_USER')} "
    f"password={os.getenv('DB_PASSWORD')} "
    f"host={os.getenv('OLAP_HOST', 'olap-db')} "
    f"port={os.getenv('OLAP_PORT', 5432)}",
)
