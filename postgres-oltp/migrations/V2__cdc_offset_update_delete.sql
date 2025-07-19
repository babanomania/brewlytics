-- Add CDC offset table and support for UPDATE/DELETE events

-- table to track last processed id per CDC table
CREATE TABLE IF NOT EXISTS cdc_offset (
    table_name TEXT PRIMARY KEY,
    last_id INTEGER DEFAULT 0
);
INSERT INTO cdc_offset(table_name, last_id)
    VALUES ('cdc_orders', 0)
ON CONFLICT (table_name) DO NOTHING;

-- extend cdc_orders with operation and table name
ALTER TABLE cdc_orders ADD COLUMN IF NOT EXISTS op TEXT DEFAULT 'INSERT';
ALTER TABLE cdc_orders ADD COLUMN IF NOT EXISTS table_name TEXT DEFAULT 'orders';

-- unified function for orders
CREATE OR REPLACE FUNCTION log_order_cdc() RETURNS TRIGGER AS $$
DECLARE
    rec RECORD;
    data JSONB;
BEGIN
    IF TG_OP = 'DELETE' THEN
        rec := OLD;
    ELSE
        rec := NEW;
    END IF;
    data := jsonb_build_object(
        'order_id', rec.id,
        'customer_id', rec.customer_id,
        'employee_id', rec.employee_id,
        'order_time', rec.order_time
    );
    INSERT INTO cdc_orders(payload, op, table_name)
    VALUES (data, TG_OP, 'orders');
    RETURN rec;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_order_cdc ON orders;
CREATE TRIGGER trg_order_cdc
AFTER INSERT OR UPDATE OR DELETE ON orders
FOR EACH ROW EXECUTE PROCEDURE log_order_cdc();

-- unified function for order_items
CREATE OR REPLACE FUNCTION log_order_item_cdc() RETURNS TRIGGER AS $$
DECLARE
    ord orders%ROWTYPE;
    rec RECORD;
    data JSONB;
BEGIN
    IF TG_OP = 'DELETE' THEN
        rec := OLD;
    ELSE
        rec := NEW;
    END IF;
    SELECT * INTO ord FROM orders WHERE id = rec.order_id;
    data := jsonb_build_object(
        'order_id', ord.id,
        'customer_id', ord.customer_id,
        'employee_id', ord.employee_id,
        'order_time', ord.order_time,
        'product_id', rec.product_id,
        'quantity', rec.quantity,
        'price', rec.price
    );
    INSERT INTO cdc_orders(payload, op, table_name)
    VALUES (data, TG_OP, 'order_items');
    RETURN rec;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_order_item_cdc ON order_items;
CREATE TRIGGER trg_order_item_cdc
AFTER INSERT OR UPDATE OR DELETE ON order_items
FOR EACH ROW EXECUTE PROCEDURE log_order_item_cdc();
