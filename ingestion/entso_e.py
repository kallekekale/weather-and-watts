import requests
from lxml import etree
from datetime import datetime, timedelta
import psycopg2
import psycopg2.extras
from config import DB_DSN, ENTSO_E_API_KEY
from ingestion import blob

BASE_URL = "https://web-api.tp.entsoe.eu/api"
FINLAND = "10YFI-1--------U"
NS = {"ns": "urn:iec62325.351:tc57wg16:451-3:publicationdocument:7:3"}


def fetch_prices(start_time, end_time):
    params = {
        "securityToken": ENTSO_E_API_KEY,
        "documentType": "A44",
        "in_Domain": FINLAND,
        "out_Domain": FINLAND,
        "periodStart": start_time.strftime("%Y%m%d%H%M"),
        "periodEnd": end_time.strftime("%Y%m%d%H%M"),
    }
    res = requests.get(BASE_URL, params=params)
    res.raise_for_status()
    return res.content


def ingest(start_time, end_time):
    """Fetch, archive the raw response to blob, parse, and load to Postgres."""
    xml = fetch_prices(start_time, end_time)
    blob.upload_raw("entso_e", xml, "xml")
    rows = parse_prices(xml)
    save_to_postgres(rows)
    return len(rows)


def parse_prices(xml_bytes):
    root = etree.fromstring(xml_bytes)
    rows = []
    for period in root.findall(".//ns:Period", NS):
        start = period.findtext("ns:timeInterval/ns:start", namespaces=NS)
        end = period.findtext("ns:timeInterval/ns:end", namespaces=NS)
        step = _parse_resolution(period.findtext("ns:resolution", namespaces=NS))
        period_start = datetime.fromisoformat(start.replace("Z", "+00:00"))
        period_end = datetime.fromisoformat(end.replace("Z", "+00:00"))
        total_slots = round((period_end - period_start) / step)

        # ENTSO-E uses variable-sized blocks: a point's price is valid from its
        # position until the next listed position. Read the points, then
        # forward-fill every slot to produce a regular grid.
        points = sorted(
            (int(p.findtext("ns:position", namespaces=NS)),
             float(p.findtext("ns:price.amount", namespaces=NS)))
            for p in period.findall("ns:Point", NS)
        )
        for i, (position, price) in enumerate(points):
            next_position = points[i + 1][0] if i + 1 < len(points) else total_slots + 1
            for slot in range(position, next_position):
                rows.append({
                    "time": period_start + (slot - 1) * step,
                    "price": price,
                })
    return rows


def _parse_resolution(resolution):
    if resolution == "PT60M":
        return timedelta(hours=1)
    if resolution == "PT15M":
        return timedelta(minutes=15)
    raise ValueError(f"Unsupported resolution: {resolution}")


def save_to_postgres(rows):
    if not rows:
        return
    with psycopg2.connect(DB_DSN) as con:
        with con.cursor() as cur:
            psycopg2.extras.execute_values(cur, """
                INSERT INTO prices (time, price)
                VALUES %s
                ON CONFLICT (time) DO NOTHING
            """, [(r["time"], r["price"]) for r in rows])
