import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

API_URL = os.getenv("API_URL", "http://localhost:8000")

OLTP_DSN = os.getenv(
    "OLTP_DSN",
    f"dbname={os.getenv('OLTP_DB', 'coffee_oltp')} "
    f"user={os.getenv('DB_USER', 'brew')} "
    f"password={os.getenv('DB_PASSWORD', 'brew')} "
    f"host={os.getenv('OLTP_HOST', 'localhost')} "
    f"port={os.getenv('OLTP_PORT', '5432')}",
)

OLAP_DSN = os.getenv(
    "OLAP_DSN",
    f"dbname={os.getenv('OLAP_DB', 'coffee_olap')} "
    f"user={os.getenv('DB_USER', 'brew')} "
    f"password={os.getenv('DB_PASSWORD', 'brew')} "
    f"host={os.getenv('OLAP_HOST', 'localhost')} "
    f"port={os.getenv('OLAP_PORT', '5433')}",
)
