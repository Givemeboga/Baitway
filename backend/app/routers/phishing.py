"""Routes du module Phishing (Module A).

Les soumissions sont analysees par le moteur (app.core.phishing) puis
persistees en base (table phishing_submissions). Les schemas de reponse
respectent docs/api-contract.md.
"""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.phishing import analyse_raw_email
from app.models.phishing import PhishingSubmission
from app.schemas.phishing import AnalyzeRequest, SubmissionUpdate

router = APIRouter(prefix="/phishing", tags=["phishing"])


def iso_utc(value):
    """Horodatage ISO 8601 UTC, format impose par le contrat d'API."""
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# --- Serialisation ----------------------------------------------------------

# Le contrat ne prevoit que ces champs pour une piece jointe ; md5 et size sont
# calcules et stockes, mais pas exposes tant que le contrat n'a pas evolue.
ATTACHMENT_FIELDS = ("filename", "sha256", "reputation", "flags")


def to_contract_attachment(entry):
    return {field: entry.get(field) for field in ATTACHMENT_FIELDS}


def to_analysis(submission):
    """Reponse d'analyse, strictement limitee aux champs du contrat d'API."""
    return {
        "submission_id": submission.submission_id,
        "verdict": submission.verdict.value,
        "risk_score": submission.risk_score,
        "headers": submission.headers,
        "urls": submission.urls,
        "attachments": [to_contract_attachment(a) for a in submission.attachments],
        "indicators": submission.indicators,
        "analyzed_at": iso_utc(submission.analyzed_at),
    }


def to_detail(submission):
    """Detail complet : analyse enrichie du suivi analyste."""
    detail = to_analysis(submission)
    detail["subject"] = submission.subject
    detail["status"] = submission.status.value
    detail["notes"] = submission.notes
    return detail


def to_queue_item(submission):
    """Ligne de la file de triage (vue allegee)."""
    return {
        "submission_id": submission.submission_id,
        "subject": submission.subject,
        "from": submission.sender,
        "verdict": submission.verdict.value,
        "risk_score": submission.risk_score,
        "status": submission.status.value,
        "analyzed_at": iso_utc(submission.analyzed_at),
    }


def get_submission_or_404(db, submission_id):
    submission = (
        db.query(PhishingSubmission)
        .filter(PhishingSubmission.submission_id == submission_id)
        .first()
    )
    if not submission:
        raise HTTPException(404, "Soumission introuvable")
    return submission


# --- Routes -----------------------------------------------------------------

@router.post("/analyze")
def analyze_email(
    payload: AnalyzeRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Soumet un e-mail brut (.eml) pour analyse et enregistre le resultat."""
    if not payload.raw_email.strip():
        raise HTTPException(400, "E-mail vide")

    try:
        analysis = analyse_raw_email(payload.raw_email)
    except Exception:
        raise HTTPException(400, "E-mail illisible")

    # La decomposition du score n'est pas encore prevue par le contrat d'API.
    analysis.pop("breakdown", None)

    submission = PhishingSubmission(
        submission_id="sub_" + uuid.uuid4().hex[:8],
        submitted_by=user["email"],
        analyzed_at=datetime.now(timezone.utc),
        **analysis,
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)

    return to_analysis(submission)


@router.get("/submissions")
def list_submissions(db: Session = Depends(get_db), user=Depends(get_current_user)):
    """File de triage, triee par risque decroissant."""
    submissions = (
        db.query(PhishingSubmission)
        .order_by(PhishingSubmission.risk_score.desc(), PhishingSubmission.analyzed_at.desc())
        .all()
    )
    return {"submissions": [to_queue_item(s) for s in submissions]}


@router.get("/submissions/{submission_id}")
def get_submission(
    submission_id: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Detail complet d'une soumission (analyse + suivi analyste)."""
    return to_detail(get_submission_or_404(db, submission_id))


@router.patch("/submissions/{submission_id}")
def update_submission(
    submission_id: str,
    payload: SubmissionUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Met a jour le verdict / statut / notes d'une soumission."""
    submission = get_submission_or_404(db, submission_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(submission, field, value)
    db.commit()
    db.refresh(submission)
    return to_detail(submission)
