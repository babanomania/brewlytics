{% macro insert_sample_orders() %}
insert into {{ target.schema }}.orders (customer_id, employee_id, order_time)
values (1, 1, now());
insert into {{ target.schema }}.order_items (order_id, product_id, quantity, price)
select currval(pg_get_serial_sequence('{{ target.schema }}.orders','id')),
       1, 1,
       price from {{ target.schema }}.products limit 1;
{% endmacro %}
