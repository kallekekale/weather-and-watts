# weather-and-watts

> **Status: early development** — Ingestion is working. Everything else is in progress or planned. The architecture and scope reflect the current direction, but may change as the project goes on.

Correlates Finnish electricity spot prices, power generation, and weather observations. As a bonus layer, a simple ML model forecasts wind power production using capacity weighted wind speed observations from stations near major wind farm regions.

## Architecture

```
ENTSO-E (XML)       Fingrid (JSON)       FMI (WFS/XML)
     |                    |                    |
     +--------------------+--------------------+
                          |
              Python + Azure Functions
              (scheduled ingestion)
                          |
              +-----------+-----------+
              |                       |
    Azure Blob Storage         Azure PostgreSQL
    (raw files as-is)          (raw rows, bronze)
                                       |
                              dbt transformations
                              (silver: cleaned,
                               timezone-harmonised)
                                       |
                              dbt star schema
                              (gold: facts + dims)
                                       |
                         +-------------+-------------+
                         |                           |
                   Streamlit dashboard         scikit-learn
                   (prices, generation,        (wind production
                    weather, correlations)      forecast vs. Fingrid)
```

## Data Sources

| Source                                                           | Data                                   | Format  | Update frequency    | License                    |
| ---------------------------------------------------------------- | -------------------------------------- | ------- | ------------------- | -------------------------- |
| [ENTSO-E Transparency Platform](https://transparency.entsoe.eu/) | Day-ahead spot prices (FI)             | XML     | Once/day ~15:00 CET | Free, API key required     |
| [Fingrid Open Data](https://data.fingrid.fi/)                    | Generation, consumption, wind forecast | JSON    | Every 3 min         | CC BY 4.0                  |
| [FMI Open Data](https://en.ilmatieteenlaitos.fi/open-data)       | Weather observations by station        | WFS/XML | Every 10 min        | Open data, no key required |

## Tech Stack

| Layer            | Tool                          |
| ---------------- | ----------------------------- |
| Ingestion        | Python, Azure Functions       |
| Raw storage      | Azure Blob Storage            |
| Database         | Azure Database for PostgreSQL |
| Transformation   | dbt                           |
| Orchestration    | Prefect                       |
| CI/CD            | GitHub Actions                |
| Containerisation | Docker                        |
| Dashboard        | Streamlit                     |
| ML               | scikit-learn                  |

## Roadmap

- [x] FMI weather ingestion
- [x] Fingrid generation ingestion
- [x] ENTSO-E spot price ingestion
- [x] Azure Blob Storage raw file backup (bronze)
- [x] dbt silver layer (cleaning, timezone harmonisation)
- [ ] dbt gold layer (star schema)
- [ ] Streamlit dashboard
- [ ] Prefect orchestration
- [ ] Azure Functions deployment
- [ ] GitHub Actions CI/CD
- [ ] ML wind production forecast
