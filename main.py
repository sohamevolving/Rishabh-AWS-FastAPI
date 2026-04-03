from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
import uuid

from database import engine, get_db, Base
from models import StoreItem
from schemas import ItemCreate, ItemUpdate, ItemResponse, MessageResponse

# Create tables on startup (safe to call repeatedly — skips existing tables)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MySQL Store API",
    description="FastAPI service that persists JSON key-value data in MySQL 8.0.",
    version="2.0.0",
)


# ─────────────────────────────────────────────
# Health
# ─────────────────────────────────────────────

@app.get("/", tags=["Health"])
def root():
    """Health check."""
    return {"status": "ok", "message": "MySQL Store API is running"}


@app.get("/health/db", tags=["Health"])
def db_health(db: Session = Depends(get_db)):
    """Verify the MySQL connection is alive."""
    try:
        db.execute(__import__("sqlalchemy").text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except OperationalError as e:
        raise HTTPException(status_code=503, detail=f"Database unavailable: {e}")


# ─────────────────────────────────────────────
# CREATE
# ─────────────────────────────────────────────

@app.post("/store", response_model=ItemResponse, status_code=201, tags=["Store"])
def store_item(item: ItemCreate, db: Session = Depends(get_db)):
    """
    Store a key-value pair in MySQL.
    - If `key` is omitted, a UUID is auto-generated.
    - If the key already exists, its value is **overwritten** (upsert behaviour).
    """
    key = item.key or str(uuid.uuid4())

    existing = db.get(StoreItem, key)
    if existing:
        existing.value = item.value
        db.commit()
        db.refresh(existing)
        return existing

    new_item = StoreItem(key=key, value=item.value)
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item


# ─────────────────────────────────────────────
# READ
# ─────────────────────────────────────────────

@app.get("/store", tags=["Store"])
def list_all(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """
    Return all stored items as JSON.
    Supports `skip` and `limit` for basic pagination.
    """
    items = db.query(StoreItem).offset(skip).limit(limit).all()
    return {item.key: item.value for item in items}


@app.get("/store/{key}", response_model=ItemResponse, tags=["Store"])
def get_item(key: str, db: Session = Depends(get_db)):
    """Retrieve a single item by key."""
    item = db.get(StoreItem, key)
    if not item:
        raise HTTPException(status_code=404, detail=f"Key '{key}' not found")
    return item


# ─────────────────────────────────────────────
# UPDATE
# ─────────────────────────────────────────────

@app.put("/store/{key}", response_model=ItemResponse, tags=["Store"])
def update_item(key: str, payload: ItemUpdate, db: Session = Depends(get_db)):
    """
    Update the value of an existing key.
    Returns 404 if the key does not exist (use POST /store to create).
    """
    item = db.get(StoreItem, key)
    if not item:
        raise HTTPException(status_code=404, detail=f"Key '{key}' not found")
    item.value = payload.value
    db.commit()
    db.refresh(item)
    return item


# ─────────────────────────────────────────────
# DELETE
# ─────────────────────────────────────────────

@app.delete("/store/{key}", response_model=MessageResponse, tags=["Store"])
def delete_item(key: str, db: Session = Depends(get_db)):
    """Delete a single item by key."""
    item = db.get(StoreItem, key)
    if not item:
        raise HTTPException(status_code=404, detail=f"Key '{key}' not found")
    db.delete(item)
    db.commit()
    return {"message": f"Key '{key}' deleted successfully"}


@app.delete("/store", response_model=MessageResponse, tags=["Store"])
def clear_store(db: Session = Depends(get_db)):
    """Delete every row in the store table."""
    deleted = db.query(StoreItem).delete()
    db.commit()
    return {"message": f"Store cleared — {deleted} item(s) removed"}