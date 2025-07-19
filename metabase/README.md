# Metabase Dashboards

This folder contains a helper script to bootstrap example dashboards in Metabase.

## Usage

1. Start the Brewlytics stack with `docker-compose up` and finish the Metabase
   setup wizard (create an admin user and connect the `coffee_olap` database).
2. (Optional) edit `dashboard.json` to customise the dashboard name and SQL
   queries.
3. Run the script:

```bash
python metabase/dashboard_from_config.py
```

The script reads the configuration from `dashboard.json` (or the path specified
in the `DASHBOARD_CONFIG` environment variable) and creates the dashboard using
the Metabase API. The environment variables `METABASE_HOST`, `METABASE_USER`,
and `METABASE_PASSWORD` can be used to override the defaults.
