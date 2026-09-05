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

router = APIRouter(prefix="/ioc", tags=["ioc"])


# ---------------------------------------------------------
# Mock data (still used for history/detail/export for now)
# ---------------------------------------------------------

MOCK_LOOKUPS = [
    {
        "lookup_id": "mock-001",
        "indicator": "8.8.8.8",
        "type": "ip",
        "verdict": "suspicious",
        "risk_score": 50,
        "sources": [
            {"name": "MockSource", "result": "suspicious", "score": 50, "raw": {}}
        ],
        "enrichment": {
            "geolocation": None, "asn": None, "domain_age_days": None,
            "registrar": None, "blacklisted": False
        },
        "looked_up_at": "2026-09-05T00:00:00Z"
    },
    {
        "lookup_id": "mock-002",
        "indicator": "example.com",
        "type": "domain",
        "verdict": "clean",
        "risk_score": 10,
        "sources": [
            {"name": "MockSource", "result": "clean", "score": 10, "raw": {}}
        ],
        "enrichment": {
            "geolocation": None, "asn": None, "domain_age_days": 1000,
            "registrar": "Example Registrar", "blacklisted": False
        },
        "looked_up_at": "2026-09-05T00:05:00Z"
    }
]


# ---------------------------------------------------------
# 1. POST /ioc/lookup — NOW REAL ENRICHMENT
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

    return {
        "lookup_id": "real-001",  # placeholder until DB save (next phase)
        "indicator": indicator,
        "type": ioc_type,
        "verdict": verdict,
        "risk_score": risk_score,
        "sources": sources,
        "enrichment": enrichment,
        "looked_up_at": datetime.now(timezone.utc).isoformat()
    }


# ---------------------------------------------------------
# 2. GET /ioc/history (still mock)
# ---------------------------------------------------------

@router.get("/history")
def history(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return [
        {
            "lookup_id": l["lookup_id"], "indicator": l["indicator"], "type": l["type"],
            "verdict": l["verdict"], "risk_score": l["risk_score"], "looked_up_at": l["looked_up_at"]
        }
        for l in MOCK_LOOKUPS
    ]


# ---------------------------------------------------------
# 3. GET /ioc/lookups/{id} (still mock)
# ---------------------------------------------------------

@router.get("/lookups/{lookup_id}")
def get_lookup(lookup_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    for l in MOCK_LOOKUPS:
        if l["lookup_id"] == lookup_id:
            return l
    raise HTTPException(status_code=404, detail="Lookup not found")


# ---------------------------------------------------------
# 4. GET /ioc/export (still mock)
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

    filtered = MOCK_LOOKUPS
    if verdict != "all":
        filtered = [l for l in MOCK_LOOKUPS if l["verdict"] == verdict]

    if format == "csv":
        lines = ["lookup_id,indicator,type,verdict,risk_score,looked_up_at"]
        for l in filtered:
            lines.append(f'{l["lookup_id"]},{l["indicator"]},{l["type"]},{l["verdict"]},{l["risk_score"]},{l["looked_up_at"]}')
        return PlainTextResponse(content="\n".join(lines), media_type="text/csv",
                                  headers={"Content-Disposition": "attachment; filename=ioc_export.csv"})

    lines = [l["indicator"] for l in filtered]
    return PlainTextResponse(content="\n".join(lines), media_type="text/plain",
                              headers={"Content-Disposition": "attachment; filename=ioc_blocklist.txt"})
