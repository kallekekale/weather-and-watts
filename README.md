# weather-and-watts

> **Status: early development** — Ingestion is working. Everything else is in progress or planned. The architecture and scope reflect the current direction, but may change as the project goes on.

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

## Roadmap

- [x] FMI weather ingestion
- [x] Fingrid generation ingestion
- [x] ENTSO-E spot price ingestion
- [x] Azure Blob Storage raw file backup (bronze)
- [x] dbt silver layer (cleaning, timezone harmonisation)
- [ ] dbt gold layer (star schema)
- [ ] Streamlit dashboard
- [ ] Airflow orchestration (local, astro CLI)
- [ ] Azure Database for PostgreSQL deployment
- [ ] GitHub Actions CI/CD
- [ ] ML wind production forecast (optional bonus)
