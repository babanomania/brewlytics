# Metabase Dashboards

This folder contains a helper script to bootstrap example dashboards in Metabase.

## Usage

1. Start the Brewlytics stack with `docker-compose up` and finish the Metabase
   setup wizard (create an admin user and connect the `coffee_olap` database).
2. Run the setup script:

```bash
python metabase/setup_dashboards.py
```

The script uses the Metabase API to create a dashboard named **Coffee Shop
Overview** with the following cards:

- **Daily Revenue**
- **Sales by Product**
- **Top Customers**

You can customise credentials and host via the environment variables
`METABASE_HOST`, `METABASE_USER`, and `METABASE_PASSWORD`.
