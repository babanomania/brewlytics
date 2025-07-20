-- Ensure CDC entries always contain product_id by logging only from order_items

-- remove old trigger and function for orders table
DROP TRIGGER IF EXISTS trg_order_cdc ON orders;
DROP FUNCTION IF EXISTS log_order_cdc();

-- order_items trigger already captures product info; ensure table_name is 'orders'
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
    VALUES (data, TG_OP, 'orders');
    RETURN rec;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_order_item_cdc ON order_items;
CREATE TRIGGER trg_order_item_cdc
AFTER INSERT OR UPDATE OR DELETE ON order_items
FOR EACH ROW EXECUTE PROCEDURE log_order_item_cdc();
