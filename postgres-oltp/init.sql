-- OLTP schema for Brewlytics
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL
);
INSERT INTO customers(name, email) VALUES
    ('Alice', 'alice@example.com'),
    ('Bob', 'bob@example.com');

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    price NUMERIC NOT NULL
);
INSERT INTO products(name, price) VALUES
    ('Espresso', 3.00),
    ('Latte', 4.50),
    ('Croissant', 2.50);

CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);
INSERT INTO employees(name) VALUES ('System');

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    employee_id INTEGER REFERENCES employees(id),
    order_time TIMESTAMPTZ NOT NULL
);

CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id),
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER NOT NULL,
    price NUMERIC NOT NULL
);

CREATE TABLE cdc_orders (
    id SERIAL PRIMARY KEY,
    payload JSONB NOT NULL,
    processed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE OR REPLACE FUNCTION log_order_item_cdc() RETURNS TRIGGER AS $$
DECLARE
    o orders%ROWTYPE;
BEGIN
    SELECT * INTO o FROM orders WHERE id = NEW.order_id;
    INSERT INTO cdc_orders(payload)
    VALUES (
        jsonb_build_object(
            'order_id', o.id,
            'customer_id', o.customer_id,
            'employee_id', o.employee_id,
            'order_time', o.order_time,
            'product_id', NEW.product_id,
            'quantity', NEW.quantity,
            'price', NEW.price
        )
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_order_item_cdc
AFTER INSERT ON order_items
FOR EACH ROW EXECUTE PROCEDURE log_order_item_cdc();

CREATE OR REPLACE FUNCTION log_order_cdc() RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO cdc_orders(payload)
    VALUES (
        jsonb_build_object(
            'order_id', NEW.id,
            'customer_id', NEW.customer_id,
            'employee_id', NEW.employee_id,
            'order_time', NEW.order_time
        )
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_order_cdc
AFTER INSERT ON orders
FOR EACH ROW EXECUTE PROCEDURE log_order_cdc();
