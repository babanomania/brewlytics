#!/bin/sh
set -e
DBT_PROFILES_DIR=${DBT_PROFILES_DIR:-/dbt}
DBT_TARGET=${DBT_TARGET:-oltp}

dbt seed --profiles-dir "$DBT_PROFILES_DIR" --target "$DBT_TARGET"
dbt run-operation load_static_data --profiles-dir "$DBT_PROFILES_DIR" --target "$DBT_TARGET"
