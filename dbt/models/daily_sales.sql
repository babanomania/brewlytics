{{ config(materialized='table') }}

select
    dd.date as sale_date,
    sum(fs.total) as total_revenue
from fact_sales fs
join dim_date dd on fs.date_id = dd.id
group by dd.date
order by sale_date
