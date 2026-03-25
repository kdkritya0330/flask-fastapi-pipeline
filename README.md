# Backend Developer Technical Assessment

A data pipeline with 3 Docker services: Flask mock server → FastAPI ingestion pipeline → PostgreSQL.

## Project Structure

```
project-root/
├── docker-compose.yml
├── README.md
├── mock-server/
│   ├── app.py
│   ├── data/customers.json
│   ├── Dockerfile
│   └── requirements.txt
└── pipeline-service/
    ├── main.py
    ├── models/customer.py
    ├── services/ingestion.py
    ├── database.py
    ├── Dockerfile
    └── requirements.txt
```

## Prerequisites

- Docker Desktop (running)
- Docker Compose v2+

## Quick Start

```bash
# Start all services
docker-compose up -d

# Wait ~10 seconds for services to become healthy, then verify:
curl http://localhost:5000/api/health
curl http://localhost:8000/api/health
```

## Testing

### Flask Mock Server (port 5000)

```bash
# Health check
curl http://localhost:5000/api/health

# Paginated customer list
curl "http://localhost:5000/api/customers?page=1&limit=5"

# Single customer
curl http://localhost:5000/api/customers/CUST-001

# 404 example
curl http://localhost:5000/api/customers/CUST-999
```

### FastAPI Pipeline (port 8000)

```bash
# Ingest all data from Flask into PostgreSQL
curl -X POST http://localhost:8000/api/ingest

# Get paginated customers from DB
curl "http://localhost:8000/api/customers?page=1&limit=5"

# Get a single customer from DB
curl http://localhost:8000/api/customers/CUST-001
```

## Architecture

```
Flask (port 5000)        FastAPI (port 8000)       PostgreSQL (port 5432)
──────────────────       ───────────────────        ──────────────────────
GET /api/customers  ──►  POST /api/ingest      ──►  customers table
GET /api/customers/{id}  GET /api/customers
GET /api/health          GET /api/customers/{id}
                         GET /api/health
```

## Response Format

```json
{
  "data": [...],
  "total": 22,
  "page": 1,
  "limit": 10
}
```

## Services

| Service          | Port | Description                        |
|------------------|------|------------------------------------|
| mock-server      | 5000 | Flask API serving customer JSON    |
| pipeline-service | 8000 | FastAPI ingestion + query API      |
| postgres         | 5432 | PostgreSQL database                |

## Notes

- `POST /api/ingest` uses upsert logic — safe to run multiple times
- Flask automatically handles pagination when fetching all records
- Health checks ensure services start in the correct order
