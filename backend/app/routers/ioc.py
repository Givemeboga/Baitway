from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.schemas.ioc import LookupRequest

router = APIRouter(prefix="/ioc", tags=["ioc"])


@router.post("/lookup")
def lookup(
    payload: LookupRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    if not payload.indicator.strip():
        raise HTTPException(
            status_code=400,
            detail="Empty indicator"
        )

    # Temporary mock response
    return {
        "lookup_id": "mock-001",
        "indicator": payload.indicator.strip(),
        "type": "ip",
        "verdict": "suspicious",
        "risk_score": 50,
        "sources": [
            {
                "name": "MockSource",
                "result": "suspicious",
                "score": 50,
                "raw": {}
            }
        ],
        "enrichment": {
            "geolocation": None,
            "asn": None,
            "domain_age_days": None,
            "registrar": None,
            "blacklisted": False
        },
        "looked_up_at": "2026-09-05T00:00:00Z"
    }