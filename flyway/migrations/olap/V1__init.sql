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

CREATE TABLE fact_inventory (
  id SERIAL PRIMARY KEY,
  product_dim_id INT REFERENCES dim_product(id),
  quantity_sold INT NOT NULL,
  date_id INT REFERENCES dim_date(id),
  recorded_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE fact_payments (
  id SERIAL PRIMARY KEY,
  customer_dim_id INT REFERENCES dim_customer(id),
  order_id INT NOT NULL,
  payment_amount NUMERIC NOT NULL,
  payment_method TEXT NOT NULL,
  date_id INT REFERENCES dim_date(id),
  recorded_at TIMESTAMPTZ NOT NULL
);

-- sample rows for validation
INSERT INTO dim_product (product_id, name, price) VALUES (1, 'Demo Product', 1.0);
INSERT INTO dim_customer (customer_id, name, email) VALUES (1, 'Demo Customer', 'demo@example.com');
INSERT INTO dim_date (date) VALUES ('2023-01-01');

INSERT INTO fact_inventory(product_dim_id, quantity_sold, date_id, recorded_at)
VALUES (1, 5, 1, CURRENT_TIMESTAMP);

INSERT INTO fact_payments(customer_dim_id, order_id, payment_amount, payment_method, date_id, recorded_at)
VALUES (1, 1, 5.0, 'cash', 1, CURRENT_TIMESTAMP);
