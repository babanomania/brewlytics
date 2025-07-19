# TODO.md — Project Bootstrap Guide for Codex

This file lists all remaining tasks required to scaffold and complete the Brewlytics project, based on the definitions in `README.md` and `agent.md`.

All components must work together using Docker Compose. Prefer sensible defaults and generate dummy/sample data where needed.

---

## 1. Project Setup

- [x] Create `.gitignore` with standard Python, Node, and Airflow exclusions
- [x] Create `docker-compose.yml` to orchestrate all services:
  - backend-api
  - oltp-db
  - olap-db
  - airflow
  - k6
  - metabase
- [x] Create `.env` file for shared environment variables (e.g., DB creds, ports)

---

## 2. Backend API (FastAPI)

**Directory**: `backend-api/`

- [x] Create `main.py` using FastAPI
- [x] Implement endpoints:
  - [x] `POST /orders` — inserts into orders + order_items and logs to `cdc_orders`
  - [x] `POST /products` — inserts into products
  - [x] `POST /customers` — inserts into customers
- [x] Use PostgreSQL client (e.g., `asyncpg` or `psycopg2`)
- [x] Add `Dockerfile` to run FastAPI with Uvicorn
- [x] Add sample dummy data (orders, products, customers)

---

## 3. OLTP PostgreSQL

**Directory**: `flyway/migrations/oltp/`

- [x] Create `init.sql` with normalized schema:
  - customers, products, orders, order_items, employees, stores
  - cdc_orders (custom WAL-like table)
- [x] Add AFTER INSERT trigger on `orders` to write to `cdc_orders`
- [x] Insert 5–10 rows of sample data

---

## 4. OLAP PostgreSQL (Star Schema)

**Directory**: `flyway/migrations/olap/`

- [x] Create `init.sql` with star schema:
  - fact_sales
  - dim_customer, dim_product, dim_employee, dim_date, dim_store
- [x] Add constraints and foreign keys
- [x] Insert a few placeholder rows for testing

---

## 5. Airflow DAGs

**Directory**: `airflow-pipeline/dags/`

- [x] Create a DAG file: `cdc_to_star.py`
- [x] DAG should:
  - [x] Poll `cdc_orders` for unprocessed records
  - [x] Parse `payload` JSON
  - [x] Join with product/customer tables if needed
  - [x] Insert into `fact_sales` in OLAP DB
  - [x] Mark CDC record as processed (or use last_id tracking)

---

## 6. K6 Load Testing

**Directory**: `k6-loadtest/`

- [x] Create `load-test.js` that:
  - [x] Hits `POST /orders` with random payloads
  - [x] Simulates 10–100 virtual users
  - [x] Runs with Docker CLI: `docker-compose run k6`

---

## 7. Metabase

**Directory**: `metabase/`

- [x] Ensure Metabase container connects to OLAP DB
- [x] Document login steps
- [x] Optionally generate sample dashboards:
  - Daily revenue
  - Sales by category
  - Top customers

---

## 8. Integration Tests

- [x] Add a basic test to verify that:
  - [x] API inserts order and logs to CDC
  - [x] Airflow DAG processes that record
  - [x] OLAP contains the expected `fact_sales` entry

---

## 9. Documentation

- [x] Confirm all paths match those described in `README.md` and `agent.md`
- [x] Add brief instructions to `README.md` for:
  - Running load tests
  - Triggering Airflow manually
  - Accessing Metabase dashboards

---

## 10. Stretch Goals

- [x] Add a `cdc_offset` table for multi-table tracking
- [x] Add dbt models for transformations (optional)
- [x] Add support for `DELETE` and `UPDATE` events in CDC

---

## 11. Additional Features

- [ ] Secure `docker-compose.yml` by moving all passwords into `.env.sample`
- [ ] Expand load testing with variations:
  - randomize customers and products
  - occasionally create new customers and products during tests
- [ ] Refactor backend into microservices for separate order, product, and customer APIs
- [x] Use Flyway to manage and deploy database schema changes
- [x] Configure `docker-compose.yml` to scale services:
  - `order-api` runs 3 instances
  - other API services run 1 instance

Once all tasks are complete, the project should simulate a full real-time analytics pipeline from transactional input to BI visualization.

