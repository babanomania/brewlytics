#!/bin/sh
set -e
DBT_PROFILES_DIR=${DBT_PROFILES_DIR:-/dbt}

dbt seed --profiles-dir "$DBT_PROFILES_DIR"
dbt run-operation load_static_data --profiles-dir "$DBT_PROFILES_DIR"
