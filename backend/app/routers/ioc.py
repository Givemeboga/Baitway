import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.schemas.ioc import LookupRequest
from app.services.ioc_detector import detect_ioc_type
from app.services.ioc_enrichment import enrich_indicator
from app.services.verdict import calculate_verdict
from app.models.ioc import IOCLookup

router = APIRouter(prefix="/ioc", tags=["ioc"])


# ---------------------------------------------------------
# 1. POST /ioc/lookup
# ---------------------------------------------------------

@router.post("/lookup")
def lookup(
    payload: LookupRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    indicator = payload.indicator.strip()

    if not indicator:
        raise HTTPException(status_code=400, detail="Empty indicator")

    try:
        ioc_type = detect_ioc_type(indicator)
    except ValueError:
        raise HTTPException(status_code=400, detail="Unrecognized indicator format")

    sources, enrichment = enrich_indicator(indicator, ioc_type)
    verdict, risk_score = calculate_verdict(sources)

    lookup_id = str(uuid.uuid4())
    looked_up_at = datetime.now(timezone.utc)

    db_lookup = IOCLookup(
        lookup_id=lookup_id,
        indicator=indicator,
        type=ioc_type,
        verdict=verdict,
        risk_score=risk_score,
        looked_up_at=looked_up_at,
        sources=sources,
        enrichment=enrichment,
    )

    db.add(db_lookup)
    db.commit()
    db.refresh(db_lookup)

    return {
        "lookup_id": lookup_id,
        "indicator": indicator,
        "type": ioc_type,
        "verdict": verdict,
        "risk_score": risk_score,
        "sources": sources,
        "enrichment": enrichment,
        "looked_up_at": looked_up_at.isoformat()
    }


# ---------------------------------------------------------
# 2. GET /ioc/history — REAL DB QUERY
# ---------------------------------------------------------

@router.get("/history")
def history(db: Session = Depends(get_db), user=Depends(get_current_user)):
    lookups = (
        db.query(IOCLookup)
        .order_by(IOCLookup.looked_up_at.desc())
        .all()
    )

    return [
        {
            "lookup_id": l.lookup_id,
            "indicator": l.indicator,
            "type": l.type,
            "verdict": l.verdict,
            "risk_score": l.risk_score,
            "looked_up_at": l.looked_up_at.isoformat(),
        }
        for l in lookups
    ]


# ---------------------------------------------------------
# 3. GET /ioc/lookups/{id} — REAL DB QUERY
# ---------------------------------------------------------

@router.get("/lookups/{lookup_id}")
def get_lookup(lookup_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    l = db.query(IOCLookup).filter(IOCLookup.lookup_id == lookup_id).first()

    if not l:
        raise HTTPException(status_code=404, detail="Lookup not found")

    return {
        "lookup_id": l.lookup_id,
        "indicator": l.indicator,
        "type": l.type,
        "verdict": l.verdict,
        "risk_score": l.risk_score,
        "sources": l.sources,
        "enrichment": l.enrichment,
        "looked_up_at": l.looked_up_at.isoformat(),
    }


# ---------------------------------------------------------
# 4. GET /ioc/export — REAL DB QUERY
# ---------------------------------------------------------

@router.get("/export")
def export(
    format: str = "csv",
    verdict: str = "malicious",
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    if format not in ["csv", "blocklist"]:
        raise HTTPException(status_code=400, detail="Format must be csv or blocklist")
    if verdict not in ["all", "malicious", "suspicious"]:
        raise HTTPException(status_code=400, detail="Verdict must be all, malicious or suspicious")

    query = db.query(IOCLookup)
    if verdict != "all":
        query = query.filter(IOCLookup.verdict == verdict)

    lookups = query.order_by(IOCLookup.looked_up_at.desc()).all()

    if format == "csv":
        lines = ["lookup_id,indicator,type,verdict,risk_score,looked_up_at"]
        for l in lookups:
            lines.append(f'{l.lookup_id},{l.indicator},{l.type},{l.verdict},{l.risk_score},{l.looked_up_at.isoformat()}')
        return PlainTextResponse(content="\n".join(lines), media_type="text/csv",
                                  headers={"Content-Disposition": "attachment; filename=ioc_export.csv"})

    lines = [l.indicator for l in lookups]
    return PlainTextResponse(content="\n".join(lines), media_type="text/plain",
                              headers={"Content-Disposition": "attachment; filename=ioc_blocklist.txt"})
