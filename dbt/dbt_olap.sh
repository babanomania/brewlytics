#!/bin/sh
set -e
DBT_PROFILES_DIR=${DBT_PROFILES_DIR:-/dbt}
DBT_PROFILE=${DBT_PROFILE:-olap}
DBT_TARGET=${DBT_TARGET:-dev}

dbt run --profiles-dir "$DBT_PROFILES_DIR" --profile "$DBT_PROFILE" --target "$DBT_TARGET"
