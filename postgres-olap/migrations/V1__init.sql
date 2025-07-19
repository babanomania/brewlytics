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

INSERT INTO dim_customer(customer_id, name, email) VALUES
    (1, 'Alice', 'alice@example.com');
INSERT INTO dim_product(product_id, name, price) VALUES
    (1, 'Espresso', 3.00);
INSERT INTO dim_employee(employee_id, name) VALUES
    (1, 'System');
INSERT INTO dim_date(date) VALUES ('2023-01-01');

INSERT INTO fact_sales(date_id, customer_dim_id, product_dim_id, employee_dim_id, quantity, price, total, order_time)
SELECT dd.id, dc.id, dp.id, de.id, 1, 3.00, 3.00, '2023-01-01'
FROM dim_date dd, dim_customer dc, dim_product dp, dim_employee de
WHERE dd.date='2023-01-01' AND dc.customer_id=1 AND dp.product_id=1 AND de.employee_id=1;
