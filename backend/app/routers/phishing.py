"""Routes du module Phishing (Module A).

MOCK : les reponses sont pour l'instant simulees en memoire. Le moteur
d'analyse .eml et la persistance en base arriveront aux etapes suivantes ;
les schemas de reponse respectent deja docs/api-contract.md.
"""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException

from app.core.deps import get_current_user
from app.schemas.phishing import AnalyzeRequest, SubmissionUpdate

router = APIRouter(prefix="/phishing", tags=["phishing"])


def now_iso():
    """Horodatage ISO 8601 UTC, format impose par le contrat d'API."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def verdict_from_score(score):
    """Echelle commune aux deux modules : 0-30 clean, 31-70 suspicious, 71+ malicious."""
    if score <= 30:
        return "clean"
    if score <= 70:
        return "suspicious"
    return "malicious"


# --- Donnees simulees -------------------------------------------------------
# Remplacees par la base de donnees a l'etape "modele + migration".
MOCK_SUBMISSIONS = {
    "sub_001": {
        "submission_id": "sub_001",
        "subject": "Votre compte Microsoft sera suspendu sous 24h",
        "verdict": "malicious",
        "risk_score": 87,
        "status": "pending",
        "notes": "",
        "analyzed_at": "2026-08-14T09:12:00Z",
        "headers": {
            "spf": "fail",
            "dkim": "fail",
            "dmarc": "fail",
            "from": "security@micros0ft-verify.com",
            "reply_to": "collect@mail.ru",
            "origin_ip": "203.0.113.44",
        },
        "urls": [
            {
                "url": "http://micros0ft-verify.com/login",
                "defanged": "hxxp://micros0ft-verify[.]com/login",
                "reputation": "malicious",
                "flags": ["typosquat", "credential_harvest"],
            },
            {
                "url": "http://bit.ly/3xK9pQr",
                "defanged": "hxxp://bit[.]ly/3xK9pQr",
                "reputation": "suspicious",
                "flags": ["shortener"],
            },
        ],
        "attachments": [
            {
                "filename": "facture_urgente.pdf.exe",
                "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                "reputation": "malicious",
                "flags": ["dangerous_extension", "double_extension"],
            }
        ],
        "indicators": [
            {
                "type": "domain",
                "value": "micros0ft-verify.com",
                "severity": "high",
                "reason": "Domaine sosie de microsoft.com (typosquatting)",
            },
            {
                "type": "ip",
                "value": "203.0.113.44",
                "severity": "high",
                "reason": "IP d'origine signalee pour envoi de spam",
            },
        ],
    },
    "sub_002": {
        "submission_id": "sub_002",
        "subject": "Facture en attente de reglement",
        "verdict": "suspicious",
        "risk_score": 54,
        "status": "reviewed",
        "notes": "A confirmer avec le service comptabilite.",
        "analyzed_at": "2026-08-14T11:47:00Z",
        "headers": {
            "spf": "pass",
            "dkim": "none",
            "dmarc": "none",
            "from": "compta@fournisseur-express.net",
            "reply_to": "compta@fournisseur-express.net",
            "origin_ip": "198.51.100.17",
        },
        "urls": [
            {
                "url": "http://198.51.100.17/facture",
                "defanged": "hxxp://198[.]51[.]100[.]17/facture",
                "reputation": "suspicious",
                "flags": ["ip_based"],
            }
        ],
        "attachments": [],
        "indicators": [
            {
                "type": "url",
                "value": "http://198.51.100.17/facture",
                "severity": "medium",
                "reason": "URL pointant directement sur une adresse IP",
            }
        ],
    },
    "sub_003": {
        "submission_id": "sub_003",
        "subject": "Compte rendu de reunion hebdomadaire",
        "verdict": "clean",
        "risk_score": 8,
        "status": "resolved",
        "notes": "Faux positif signale par l'utilisateur.",
        "analyzed_at": "2026-08-15T08:03:00Z",
        "headers": {
            "spf": "pass",
            "dkim": "pass",
            "dmarc": "pass",
            "from": "direction@esprim.tn",
            "reply_to": "direction@esprim.tn",
            "origin_ip": "192.0.2.10",
        },
        "urls": [],
        "attachments": [
            {
                "filename": "compte_rendu.pdf",
                "sha256": "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08",
                "reputation": "clean",
                "flags": [],
            }
        ],
        "indicators": [],
    },
}

# Champs exposes dans la file de triage (liste allegee).
QUEUE_FIELDS = ("submission_id", "subject", "verdict", "risk_score", "status", "analyzed_at")


def to_queue_item(submission):
    item = {field: submission[field] for field in QUEUE_FIELDS}
    item["from"] = submission["headers"]["from"]
    return item


# Champs hors analyse : suivi analyste (status/notes) et champ propre a la file (subject).
NON_ANALYSIS_FIELDS = ("status", "notes", "subject")


def analysis_payload(submission):
    """Reponse d'analyse, strictement limitee aux champs du contrat d'API."""
    return {k: v for k, v in submission.items() if k not in NON_ANALYSIS_FIELDS}


def get_submission_or_404(submission_id):
    submission = MOCK_SUBMISSIONS.get(submission_id)
    if not submission:
        raise HTTPException(404, "Soumission introuvable")
    return submission


# --- Routes -----------------------------------------------------------------

@router.post("/analyze")
def analyze_email(payload: AnalyzeRequest, user=Depends(get_current_user)):
    """Soumet un e-mail brut (.eml) pour analyse.

    MOCK : renvoie une analyse simulee tant que le moteur n'est pas branche.
    """
    if not payload.raw_email.strip():
        raise HTTPException(400, "E-mail vide")

    submission_id = "sub_" + uuid.uuid4().hex[:8]
    submission = dict(MOCK_SUBMISSIONS["sub_001"])
    submission["submission_id"] = submission_id
    submission["analyzed_at"] = now_iso()
    submission["status"] = "pending"
    submission["notes"] = ""
    MOCK_SUBMISSIONS[submission_id] = submission

    return analysis_payload(submission)


@router.get("/submissions")
def list_submissions(user=Depends(get_current_user)):
    """File de triage, triee par risque decroissant."""
    items = [to_queue_item(s) for s in MOCK_SUBMISSIONS.values()]
    items.sort(key=lambda s: s["risk_score"], reverse=True)
    return {"submissions": items}


@router.get("/submissions/{submission_id}")
def get_submission(submission_id: str, user=Depends(get_current_user)):
    """Detail complet d'une soumission (analyse + suivi analyste)."""
    return get_submission_or_404(submission_id)


@router.patch("/submissions/{submission_id}")
def update_submission(
    submission_id: str,
    payload: SubmissionUpdate,
    user=Depends(get_current_user),
):
    """Met a jour le verdict / statut / notes d'une soumission."""
    submission = get_submission_or_404(submission_id)
    submission.update(payload.model_dump(exclude_unset=True))
    return submission
