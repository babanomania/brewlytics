{% macro load_static_data() %}
insert into {{ target.schema }}.customers (name, email)
select name, email from {{ ref('customers') }}
on conflict do nothing;

insert into {{ target.schema }}.products (name, price)
select name, price from {{ ref('products') }}
on conflict do nothing;
{% endmacro %}
