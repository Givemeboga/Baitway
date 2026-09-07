from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from app.core.database import Base


class IOCLookup(Base):
    __tablename__ = "ioc_lookups"

    id = Column(Integer, primary_key=True, index=True)

    lookup_id = Column(String, unique=True, nullable=False, index=True)

    indicator = Column(String, nullable=False, index=True)

    type = Column(String, nullable=False)

    verdict = Column(String, nullable=False)

    risk_score = Column(Float, nullable=False)

    sources = Column(JSONB, nullable=False, default=list)

    enrichment = Column(JSONB, nullable=False, default=dict)

    looked_up_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )