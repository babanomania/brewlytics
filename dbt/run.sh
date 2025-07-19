#!/bin/sh
set -e
DBT_PROFILES_DIR=${DBT_PROFILES_DIR:-/dbt}
DBT_TARGET=${DBT_TARGET:-olap}

dbt run --profiles-dir "$DBT_PROFILES_DIR" --target "$DBT_TARGET"
