from sqlalchemy import Column, String, JSON, DateTime, func
from database import Base


class StoreItem(Base):
    __tablename__ = "store_items"

    key = Column(String(255), primary_key=True, index=True, nullable=False)
    value = Column(JSON, nullable=False)               # native MySQL 8.0 JSON type
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )