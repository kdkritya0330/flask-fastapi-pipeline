import os
from typing import Iterator

import dlt
import httpx

MOCK_SERVER_URL = os.getenv("MOCK_SERVER_URL", "http://mock-server:5000")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/customer_db")


def fetch_all_customers() -> list[dict]:
    """Fetch all customers from the Flask mock server, handling pagination."""
    all_customers = []
    page = 1
    limit = 10

    with httpx.Client(timeout=30) as client:
        while True:
            resp = client.get(
                f"{MOCK_SERVER_URL}/api/customers",
                params={"page": page, "limit": limit},
            )
            resp.raise_for_status()
            payload = resp.json()

            data = payload.get("data", [])
            all_customers.extend(data)

            total = payload.get("total", 0)
            if len(all_customers) >= total or not data:
                break
            page += 1

    return all_customers


@dlt.resource(
    name="customers",
    write_disposition="merge",
    primary_key="customer_id",
)
def customers_resource() -> Iterator[dict]:
    """dlt resource: yields all customers fetched from the mock server."""
    for customer in fetch_all_customers():
        yield customer


def run_ingestion_pipeline() -> int:
    pipeline = dlt.pipeline(
        pipeline_name="customer_pipeline",
        destination=dlt.destinations.postgres(DATABASE_URL),
        dataset_name="public",
        dev_mode=False,
    )

    pipeline.run(customers_resource())

    try:
        metrics = pipeline.last_trace.last_normalize_info
        records = sum(v for v in metrics.row_counts.values())
    except Exception:
        records = len(fetch_all_customers())

    return records