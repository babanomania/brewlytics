#!/bin/sh
set -e
DBT_PROFILES_DIR=${DBT_PROFILES_DIR:-/dbt}

dbt run --profiles-dir "$DBT_PROFILES_DIR" --target olap
