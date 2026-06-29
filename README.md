# weather-and-watts

> **Status: in development.** The pipeline runs end to end: ingestion, bronze (Azure Blob), dbt silver, and a dbt gold star schema. Dashboard, orchestration, and cloud deployment are next.

Correlates Finnish electricity spot prices, power generation, and weather observations. As an optional bonus layer, a simple ML model forecasts wind power production using capacity weighted wind speed observations from stations near major wind farm regions.

## Architecture

```
ENTSO-E (XML)       Fingrid (JSON)       FMI (WFS/XML)
     |                    |                    |
     +--------------------+--------------------+
                          |
                  Python ingestion
                          |
              +-----------+-----------+
              |                       |
    Azure Blob Storage          PostgreSQL
    (raw files, bronze)         (raw rows)
                                       |
                              dbt transformations
                              (silver: cleaned,
                               timezone-harmonised)
                                       |
                              dbt star schema
                              (gold: facts + dims)
                                       |
                              Streamlit dashboard
                              (prices, generation,
                               weather, correlations)

Orchestration: Airflow (local).   CI/CD: GitHub Actions.
Optional: scikit-learn wind-production forecast.
```

## Data Sources

| Source                                                           | Data                                   | Format  | Update frequency    | License                    |
| ---------------------------------------------------------------- | -------------------------------------- | ------- | ------------------- | -------------------------- |
| [ENTSO-E Transparency Platform](https://transparency.entsoe.eu/) | Day-ahead spot prices (FI)             | XML     | Once/day ~15:00 CET | Free, API key required     |
| [Fingrid Open Data](https://data.fingrid.fi/)                    | Generation, consumption, wind forecast | JSON    | Every 3 min         | CC BY 4.0                  |
| [FMI Open Data](https://en.ilmatieteenlaitos.fi/open-data)       | Weather observations by station        | WFS/XML | Every 10 min        | Open data, no key required |

## Tech Stack

| Layer            | Tool                                                                    |
| ---------------- | ----------------------------------------------------------------------- |
| Ingestion        | Python                                                                  |
| Raw storage      | Azure Blob Storage (bronze)                                             |
| Database         | PostgreSQL (local Docker; Azure Database for PostgreSQL for deployment) |
| Transformation   | dbt                                                                     |
| Orchestration    | Airflow (local, astro CLI)                                              |
| CI/CD            | GitHub Actions                                                          |
| Containerisation | Docker                                                                  |
| Dashboard        | Streamlit                                                               |
| ML (optional)    | scikit-learn                                                            |

## Architectural Decisions

- **Medallion layering: keep raw data immutable and transform in dbt.** By storing every API response in Azure Blob before parsing, the pipeline has a proper bronze layer. Python only ingests data, while dbt handles all cleaning, pivoting, and timezone conversion in the silver and gold layers. If the transformation logic changes, there's no need to call the API again; the raw data is already there and can just be reprocessed.

- **Timestamps kept in UTC, with Helsinki local-time columns alongside.** Everything joins on UTC, which keeps the sources aligned and avoids the daylight saving time headaches. The `*_local` columns are just for reading the data in Finnish time.

- **Hourly data in the gold layer.** The three data sources update at different frequencies (15min prices, 3min consumption, hourly weather). The gold facts aggregate everything onto a common hourly grid so the three can be correlated easily.

## Roadmap

- [x] FMI weather ingestion
- [x] Fingrid generation ingestion
- [x] ENTSO-E spot price ingestion
- [x] Azure Blob Storage raw file backup (bronze)
- [x] dbt silver layer (cleaning, timezone harmonisation)
- [x] dbt gold layer (star schema)
- [ ] Streamlit dashboard
- [ ] Airflow orchestration (local, astro CLI)
- [ ] Azure Database for PostgreSQL deployment
- [ ] GitHub Actions CI/CD
- [ ] ML wind production forecast (optional bonus)
