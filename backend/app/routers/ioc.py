from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.schemas.ioc import LookupRequest
from app.services.ioc_detector import detect_ioc_type

router = APIRouter(prefix="/ioc", tags=["ioc"])


# ---------------------------------------------------------
# Mock data
# ---------------------------------------------------------

MOCK_LOOKUPS = [
    {
        "lookup_id": "mock-001",
        "indicator": "8.8.8.8",
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
    },
    {
        "lookup_id": "mock-002",
        "indicator": "example.com",
        "type": "domain",
        "verdict": "clean",
        "risk_score": 10,
        "sources": [
            {
                "name": "MockSource",
                "result": "clean",
                "score": 10,
                "raw": {}
            }
        ],
        "enrichment": {
            "geolocation": None,
            "asn": None,
            "domain_age_days": 1000,
            "registrar": "Example Registrar",
            "blacklisted": False
        },
        "looked_up_at": "2026-09-05T00:05:00Z"
    }
]


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
        raise HTTPException(
            status_code=400,
            detail="Empty indicator"
        )

    try:
        ioc_type = detect_ioc_type(indicator)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Unrecognized indicator format"
        )

    # Temporary mock response — type is now real, rest still hardcoded
    return {
        "lookup_id": "mock-003",
        "indicator": indicator,
        "type": ioc_type,
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
        "looked_up_at": datetime.now(timezone.utc).isoformat()
    }


# ---------------------------------------------------------
# 2. GET /ioc/history
# ---------------------------------------------------------

@router.get("/history")
def history(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return [
        {
            "lookup_id": lookup["lookup_id"],
            "indicator": lookup["indicator"],
            "type": lookup["type"],
            "verdict": lookup["verdict"],
            "risk_score": lookup["risk_score"],
            "looked_up_at": lookup["looked_up_at"]
        }
        for lookup in MOCK_LOOKUPS
    ]


# ---------------------------------------------------------
# 3. GET /ioc/lookups/{id}
# ---------------------------------------------------------

@router.get("/lookups/{lookup_id}")
def get_lookup(
    lookup_id: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    for lookup in MOCK_LOOKUPS:
        if lookup["lookup_id"] == lookup_id:
            return lookup

    raise HTTPException(
        status_code=404,
        detail="Lookup not found"
    )


# ---------------------------------------------------------
# 4. GET /ioc/export
# ---------------------------------------------------------

@router.get("/export")
def export(
    format: str = "csv",
    verdict: str = "malicious",
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    if format not in ["csv", "blocklist"]:
        raise HTTPException(
            status_code=400,
            detail="Format must be csv or blocklist"
        )

    if verdict not in ["all", "malicious", "suspicious"]:
        raise HTTPException(
            status_code=400,
            detail="Verdict must be all, malicious or suspicious"
        )

    filtered = MOCK_LOOKUPS

    if verdict != "all":
        filtered = [
            lookup
            for lookup in MOCK_LOOKUPS
            if lookup["verdict"] == verdict
        ]

    if format == "csv":
        lines = [
            "lookup_id,indicator,type,verdict,risk_score,looked_up_at"
        ]

        for lookup in filtered:
            lines.append(
                f'{lookup["lookup_id"]},'
                f'{lookup["indicator"]},'
                f'{lookup["type"]},'
                f'{lookup["verdict"]},'
                f'{lookup["risk_score"]},'
                f'{lookup["looked_up_at"]}'
            )

        return PlainTextResponse(
            content="\n".join(lines),
            media_type="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=ioc_export.csv"
            }
        )

    lines = []

    for lookup in filtered:
        lines.append(lookup["indicator"])

    return PlainTextResponse(
        content="\n".join(lines),
        media_type="text/plain",
        headers={
            "Content-Disposition": "attachment; filename=ioc_blocklist.txt"
        }
    )