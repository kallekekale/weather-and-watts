import json
import requests
import psycopg2
import psycopg2.extras
from config import DB_DSN, FINGRID_API_KEY
from ingestion import blob

DATASETS = {
    75: "wind_production",
    193: "total_consumption",
    245: "wind_forecast",
}

BASE_URL = "https://data.fingrid.fi/api/datasets/{dataset_id}/data"


def fetch_data(dataset_id, start_time, end_time):
    url = BASE_URL.format(dataset_id=dataset_id)
    headers = {"x-api-key": FINGRID_API_KEY}
    params = {
        "startTime": start_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "endTime": end_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "format": "json",
        "pageSize": 10000,
    }

    records = []
    page = 1
    while True:
        res = requests.get(url, headers=headers, params={**params, "page": page})
        res.raise_for_status()
        body = res.json()
        records.extend(body["data"])
        if page >= body["pagination"]["lastPage"]:
            break
        page += 1

    return records


def ingest(dataset_id, start_time, end_time):
    """Fetch, archive the raw response to blob, parse, and load to Postgres."""
    records = fetch_data(dataset_id, start_time, end_time)
    blob.upload_raw("fingrid", json.dumps(records), "json")
    rows = parse_data(records, dataset_id)
    save_to_postgres(rows)
    return len(rows)


def parse_data(records, dataset_id):
    return [
        {
            "dataset_id": dataset_id,
            "start_time": r["startTime"],
            "end_time": r["endTime"],
            "value": r["value"],
        }
        for r in records
    ]


def save_to_postgres(rows):
    if not rows:
        return
    with psycopg2.connect(DB_DSN) as con:
        with con.cursor() as cur:
            psycopg2.extras.execute_values(cur, """
                INSERT INTO generation (dataset_id, start_time, end_time, value)
                VALUES %s
                ON CONFLICT (dataset_id, start_time) DO NOTHING
            """, [(r["dataset_id"], r["start_time"], r["end_time"], r["value"]) for r in rows])
