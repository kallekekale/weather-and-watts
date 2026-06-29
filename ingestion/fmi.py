import requests
from lxml import etree
import psycopg2
import psycopg2.extras
from config import DB_DSN
from ingestion import blob

# FMI weather stations to ingest, keyed by fmisid.
STATIONS = {
    100971: "Helsinki Kaisaniemi",
    100968: "Helsinki Vantaa Airport",
}


def fetch_observations(station_id, start_time, end_time):
    start_time = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    end_time = end_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    url = "https://opendata.fmi.fi/wfs"
    params = {
        "service": "WFS",
        "version": "2.0.0",
        "request": "GetFeature",
        "storedquery_id": "fmi::observations::weather::hourly::simple",
        "fmisid": station_id,
        "starttime": start_time,
        "endtime": end_time,
    }

    res = requests.get(url, params=params)
    res.raise_for_status()
    return res.content


def ingest(station_id, start_time, end_time):
    """Fetch, archive the raw response to blob, parse, and load to Postgres."""
    xml = fetch_observations(station_id, start_time, end_time)
    blob.upload_raw("fmi", xml, "xml")
    observations = parse_observations(xml, station_id)
    save_to_postgres(observations)
    return len(observations)


def parse_observations(xml_bytes, station_id):
    root = etree.fromstring(xml_bytes)
    ns = {
        "wfs": "http://www.opengis.net/wfs/2.0",
        "BsWfs": "http://xml.fmi.fi/schema/wfs/2.0",
    }
    parsed_observations = []
    members = root.findall("wfs:member", ns)
    for member in members:
        time = member.find(".//BsWfs:Time", ns)
        parameter_name = member.find(".//BsWfs:ParameterName", ns)
        parameter_value = member.find(".//BsWfs:ParameterValue", ns)
        if (
            time is not None
            and parameter_name is not None
            and parameter_value is not None
        ):
            value = parameter_value.text
            if value == "NaN":
                value = None
            else:
                value = float(value)

            entry = {
                "station_id": station_id,
                "time": time.text,
                "parameter_name": parameter_name.text,
                "parameter_value": value,
            }
            parsed_observations.append(entry)

    return parsed_observations


def save_to_postgres(observations):
    if not observations:
        return
    with psycopg2.connect(DB_DSN) as con:
        with con.cursor() as cur:
            psycopg2.extras.execute_values(
                cur,
                """
                INSERT INTO weather (station_id, time, parameter_name, parameter_value)
                VALUES %s
                ON CONFLICT (station_id, time, parameter_name) DO NOTHING
            """,
                [
                    (
                        o["station_id"],
                        o["time"],
                        o["parameter_name"],
                        o["parameter_value"],
                    )
                    for o in observations
                ],
            )
