#!/bin/sh
set -e
DBT_PROFILES_DIR=${DBT_PROFILES_DIR:-/dbt}
DBT_PROFILE=${DBT_PROFILE:-oltp}
DBT_TARGET=${DBT_TARGET:-dev}

dbt seed --profiles-dir "$DBT_PROFILES_DIR" --profile "$DBT_PROFILE" --target "$DBT_TARGET"
dbt run-operation load_static_data --profiles-dir "$DBT_PROFILES_DIR" --profile "$DBT_PROFILE" --target "$DBT_TARGET"
# Insert a sample order so OLTP has data to replicate
dbt run-operation insert_sample_orders --profiles-dir "$DBT_PROFILES_DIR" --profile "$DBT_PROFILE" --target "$DBT_TARGET"
