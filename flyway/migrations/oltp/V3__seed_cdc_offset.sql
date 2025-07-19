-- Seed initial row for cdc_offset table
INSERT INTO cdc_offset(table_name, last_id)
    VALUES ('cdc_orders', 0)
ON CONFLICT (table_name) DO NOTHING;
