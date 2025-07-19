# Agent Project Context: Brewlytics

## Goal

Simulate a real-time coffee shop analytics stack. Users place orders via an API, data is inserted into an OLTP PostgreSQL database with CDC logging. Airflow picks up changes and replicates them into an OLAP PostgreSQL star schema. Metabase visualizes the data. K6 simulates user load.

## Components

### 1. `backend-api/` (FastAPI)
- Exposes REST endpoints:
  - `POST /orders`
  - `POST /products`
  - `POST /customers`
- Writes to OLTP database (`coffee_oltp`)
- Triggers write to `cdc_orders` table

### 2. `postgres-oltp/`
- Normalized schema:
  - `orders`, `order_items`, `products`, `customers`, `employees`
  - `cdc_orders` logs inserts (and optionally updates)

### 3. `airflow-pipeline/`
- DAG reads from `cdc_orders`
- Transforms JSON payload into `fact_sales`
- Loads into OLAP DB (`coffee_olap`)
- Located in `dags/cdc_to_star.py`

### 4. `postgres-olap/`
- Star schema:
  - `fact_sales`, `dim_customer`, `dim_product`, `dim_employee`, `dim_date`
- Ingested by Airflow

### 5. `k6-loadtest/`
- K6 script targets `POST /orders`
- Simulates 10–100 VUs
- Used to populate OLTP with test data

### 6. `metabase/`
- Visualizes OLAP schema
- Sample dashboards: revenue by day, sales by category, top customers

## Shared Services

### PostgreSQL Instances:
- `coffee_oltp`: for transactional writes and CDC
- `coffee_olap`: for analytical reads

## Dev Environment

- All services run via Docker Compose
- Each component should auto-initialize on `docker-compose up`
- Environment variables defined in `.env` or inside `docker-compose.yml`

## Coding Conventions

- All services must be stateless
- Timestamps in UTC
- CDC payloads are `JSONB`
- Airflow DAGs must be idempotent (no duplicate loads)

## Suggested Enhancements

- Add `cdc_offset` tracking table to avoid missing records
- Add monitoring dashboard for DAG success/failure counts
- Add dbt transformations post-load into `fact_sales`

