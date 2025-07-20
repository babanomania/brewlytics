{% macro load_static_data() %}
insert into {{ target.schema }}.customers (name, email)
select name, email from {{ ref('seed_customers') }}
on conflict do nothing;

insert into {{ target.schema }}.products (name, price)
select name, price from {{ ref('seed_products') }}
on conflict do nothing;

insert into {{ target.schema }}.employees (name, active)
select name, active from {{ ref('seed_employees') }}
on conflict do nothing;
{% endmacro %}
