# Agent Project Context: Brewlytics

## Goal

Brewlytics simulates a real-time analytics pipeline for a coffee shop. Users place orders via a REST API, which inserts into an OLTP PostgreSQL database. A custom CDC mechanism logs changes into a `cdc_orders` table. Airflow DAGs extract and transform this data into a star schema in an OLAP PostgreSQL instance. Metabase provides business-friendly dashboards, while K6 simulates real-time load on the API.

---

## Core Components

-### 1. Microservices (FastAPI)
-Directories:
  - `order-api/`
  - `product-api/`
  - `customer-api/`
-Each service exposes its own endpoint set, e.g. `POST /orders` from order-api.
- Uses PostgreSQL client (`psycopg2`)
- On order creation, inserts into `orders` and `order_items`, and logs a JSONB payload to `cdc_orders`
- Containerized with Uvicorn in Docker
- Dummy data generation is pending
- Services are split into microservices (order, customer, product)

---

### 2. `flyway/migrations/oltp/`
- Standard normalized schema includes:
  - `orders`, `order_items`, `products`, `customers`, `employees`, `stores`
- CDC implementation:
  - Trigger on `orders` inserts into `cdc_orders`
  - `cdc_orders` acts as a WAL-like journal for Airflow
- Managed with Flyway migrations in `migrations/`

---

### 3. `airflow-pipeline/`
- Airflow DAG `cdc_to_star.py` polls `cdc_orders` for new entries
- Transforms payloads into fact and dimension entries
- Loads data into `fact_sales` and maintains idempotency (no duplicate inserts)
- Supports join enrichment with `products`, `customers`, etc.
- Potential enhancement: add `cdc_offset` table for checkpoint tracking across multiple tables

---

### 4. `flyway/migrations/olap/`
- Implements a simplified star schema:
  - `fact_sales`
  - Dimensions: `dim_customer`, `dim_product`, `dim_employee`, `dim_date`, `dim_store`
- Seeded with sample data for demo use
- Managed with Flyway migrations (optionally dbt later)

---

### 5. `k6-loadtest/`
- Load test script hits `POST /orders`
- Uses randomized payloads with predefined customers/products
- Simulates 10–100 concurrent users
- Future improvement: expand to occasionally create new customers/products mid-test

---

### 6. `metabase/`
- Connects to `coffee_olap` (OLAP DB)
- Dashboards are user-configurable
- Current focus: revenue by day, sales by category, top customers
- Future enhancement: include default dashboards and visual templates

---

## Shared Infrastructure

### Databases
- **OLTP**: `coffee_oltp` (transactional writes, normalized)
- **OLAP**: `coffee_olap` (analytics, star schema)

### Orchestration
- Managed via `docker-compose.yml`
- All services are stateless
- Secrets and ports are defined via `.env` (plan to extract from Compose into `.env.sample`)

---

## Conventions and Best Practices

- UTC timestamps across all services
- CDC events use `JSONB` payloads
- Airflow DAGs must be idempotent and support eventual consistency
- All services communicate via internal Docker network

---

## Future Enhancements

- [x] Replace raw SQL with **Flyway** for both OLTP and OLAP schema migrations
- [ ] Add **`cdc_offset`** table for precise incremental CDC checkpointing
- [ ] Implement **support for `UPDATE` and `DELETE`** CDC events
- [ ] Expand **K6 test coverage** to simulate more realistic customer behavior
- [ ] Introduce **dbt** for OLAP transformations and post-load validation
- [x] Refactor backend into modular **microservices** with isolated data ownership
- [ ] Scale services in Docker Compose (e.g., `order-api` with 3 replicas)

---

## Developer Workflow Summary

1. Launch the stack:
   ```bash
   docker-compose up --build
````

2. Use `/orders` API to generate transactions (or run K6 test)
3. Watch Airflow DAG process CDC into `fact_sales`
4. Open Metabase and view analytical dashboards

---

This file is intended to help Codex, developers, and collaborators understand the architecture, responsibilities, and goals of each component. Follow the `TODO.md` to scaffold or extend the project incrementally.
