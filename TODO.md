# TODO.md — Project Bootstrap Guide for Codex

This file lists all remaining tasks required to scaffold and complete the Brewlytics project, based on the definitions in `README.md` and `agent.md`.

All components must work together using Docker Compose. Prefer sensible defaults and generate dummy/sample data where needed.

---

## 1. Project Setup

- [ ] Create `.gitignore` with standard Python, Node, and Airflow exclusions
- [ ] Create `docker-compose.yml` to orchestrate all services:
  - backend-api
  - oltp-db
  - olap-db
  - airflow
  - k6
  - metabase
- [ ] Create `.env` file for shared environment variables (e.g., DB creds, ports)

---

## 2. Backend API (FastAPI)

**Directory**: `backend-api/`

- [ ] Create `main.py` using FastAPI
- [ ] Implement endpoints:
  - [ ] `POST /orders` — inserts into orders + order_items and logs to `cdc_orders`
  - [ ] `POST /products` — inserts into products
  - [ ] `POST /customers` — inserts into customers
- [ ] Use PostgreSQL client (e.g., `asyncpg` or `psycopg2`)
- [ ] Add `Dockerfile` to run FastAPI with Uvicorn
- [ ] Add sample dummy data (orders, products, customers)

---

## 3. OLTP PostgreSQL

**Directory**: `postgres-oltp/`

- [ ] Create `init.sql` with normalized schema:
  - customers, products, orders, order_items, employees, stores
  - cdc_orders (custom WAL-like table)
- [ ] Add AFTER INSERT trigger on `orders` to write to `cdc_orders`
- [ ] Insert 5–10 rows of sample data

---

## 4. OLAP PostgreSQL (Star Schema)

**Directory**: `postgres-olap/`

- [ ] Create `init.sql` with star schema:
  - fact_sales
  - dim_customer, dim_product, dim_employee, dim_date, dim_store
- [ ] Add constraints and foreign keys
- [ ] Insert a few placeholder rows for testing

---

## 5. Airflow DAGs

**Directory**: `airflow-pipeline/dags/`

- [ ] Create a DAG file: `cdc_to_star.py`
- [ ] DAG should:
  - [ ] Poll `cdc_orders` for unprocessed records
  - [ ] Parse `payload` JSON
  - [ ] Join with product/customer tables if needed
  - [ ] Insert into `fact_sales` in OLAP DB
  - [ ] Mark CDC record as processed (or use last_id tracking)

---

## 6. K6 Load Testing

**Directory**: `k6-loadtest/`

- [ ] Create `load-test.js` that:
  - [ ] Hits `POST /orders` with random payloads
  - [ ] Simulates 10–100 virtual users
  - [ ] Runs with Docker CLI: `docker-compose run k6`

---

## 7. Metabase

**Directory**: `metabase/`

- [ ] Ensure Metabase container connects to OLAP DB
- [ ] Document login steps
- [ ] Optionally generate sample dashboards:
  - Daily revenue
  - Sales by category
  - Top customers

---

## 8. Integration Tests

- [ ] Add a basic test to verify that:
  - [ ] API inserts order and logs to CDC
  - [ ] Airflow DAG processes that record
  - [ ] OLAP contains the expected `fact_sales` entry

---

## 9. Documentation

- [ ] Confirm all paths match those described in `README.md` and `agent.md`
- [ ] Add brief instructions to `README.md` for:
  - Running load tests
  - Triggering Airflow manually
  - Accessing Metabase dashboards

---

## 10. Stretch Goals

- [ ] Add a `cdc_offset` table for multi-table tracking
- [ ] Add dbt models for transformations (optional)
- [ ] Add support for `DELETE` and `UPDATE` events in CDC
- [ ] Deploy on Docker Swarm or Kubernetes

---

Once all tasks are complete, the project should simulate a full real-time analytics pipeline from transactional input to BI visualization.

