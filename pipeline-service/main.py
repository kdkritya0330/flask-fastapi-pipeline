from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import init_db, get_db
from models.customer import Customer
from services.ingestion import run_ingestion_pipeline


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Customer Pipeline Service", lifespan=lifespan)


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "pipeline-service"}


@app.post("/api/ingest")
def ingest():
    """Fetch all data from Flask mock server and upsert into PostgreSQL via dlt."""
    try:
        count = run_ingestion_pipeline()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion pipeline failed: {str(e)}")

    return {"status": "success", "records_processed": count}


@app.get("/api/customers")
def list_customers(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Records per page"),
    db: Session = Depends(get_db),
):
    """Return paginated customers from the database."""
    total = db.query(Customer).count()
    offset = (page - 1) * limit
    customers = db.query(Customer).offset(offset).limit(limit).all()

    return {
        "data": [c.to_dict() for c in customers],
        "total": total,
        "page": page,
        "limit": limit,
    }


@app.get("/api/customers/{customer_id}")
def get_customer(customer_id: str, db: Session = Depends(get_db)):
    """Return a single customer by ID or 404."""
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"data": customer.to_dict()}
