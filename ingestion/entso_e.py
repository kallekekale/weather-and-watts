import requests
from lxml import etree
from datetime import timedelta
import psycopg2
import psycopg2.extras
from config import DB_DSN, ENTSO_E_API_KEY

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


def parse_prices(xml_bytes):
    root = etree.fromstring(xml_bytes)
    rows = []
    for period in root.findall(".//ns:Period", NS):
        start = period.findtext("ns:timeInterval/ns:start", namespaces=NS)
        resolution = period.findtext("ns:resolution", namespaces=NS)
        step = _parse_resolution(resolution)
        from datetime import datetime
        period_start = datetime.fromisoformat(start.replace("Z", "+00:00"))
        for point in period.findall("ns:Point", NS):
            position = int(point.findtext("ns:position", namespaces=NS))
            price = point.findtext("ns:price.amount", namespaces=NS)
            time = period_start + (position - 1) * step
            rows.append({"time": time, "price": float(price)})
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
