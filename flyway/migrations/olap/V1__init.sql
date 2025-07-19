-- OLAP star schema for Brewlytics
CREATE TABLE dim_customer (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER UNIQUE,
    name TEXT,
    email TEXT
);

CREATE TABLE dim_product (
    id SERIAL PRIMARY KEY,
    product_id INTEGER UNIQUE,
    name TEXT,
    price NUMERIC
);

CREATE TABLE dim_employee (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER UNIQUE,
    name TEXT
);

CREATE TABLE dim_date (
    id SERIAL PRIMARY KEY,
    date DATE UNIQUE
);

CREATE TABLE fact_sales (
    id SERIAL PRIMARY KEY,
    date_id INTEGER REFERENCES dim_date(id),
    customer_dim_id INTEGER REFERENCES dim_customer(id),
    product_dim_id INTEGER REFERENCES dim_product(id),
    employee_dim_id INTEGER REFERENCES dim_employee(id),
    quantity INTEGER,
    price NUMERIC,
    total NUMERIC,
    order_time TIMESTAMPTZ
);

