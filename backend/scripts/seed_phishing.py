"""Insere des soumissions de demonstration dans phishing_submissions.

Utile tant que le moteur d'analyse .eml n'est pas branche : fournit des donnees
realistes couvrant les trois verdicts pour developper l'interface.

Lancement (depuis backend/, venv actif) :
    python -m scripts.seed_phishing

Le script est idempotent : une soumission deja presente est ignoree.
"""

from datetime import datetime, timezone

from app.core.database import SessionLocal
from app.models.phishing import PhishingSubmission, SubmissionStatus, Verdict

SEED = [
    {
        "submission_id": "sub_001",
        "subject": "Your Microsoft account will be suspended within 24h",
        "sender": "security@micros0ft-verify.com",
        "verdict": Verdict.malicious,
        "risk_score": 87,
        "status": SubmissionStatus.pending,
        "notes": "",
        "submitted_by": "demo@baitway.local",
        "analyzed_at": datetime(2026, 8, 14, 9, 12, tzinfo=timezone.utc),
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
                "filename": "urgent_invoice.pdf.exe",
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
                "reason": "Lookalike of microsoft.com (typosquatting)",
            },
            {
                "type": "ip",
                "value": "203.0.113.44",
                "severity": "high",
                "reason": "Originating IP reported for sending spam",
            },
        ],
    },
    {
        "submission_id": "sub_002",
        "subject": "Invoice awaiting payment",
        "sender": "compta@fournisseur-express.net",
        "verdict": Verdict.suspicious,
        "risk_score": 54,
        "status": SubmissionStatus.reviewed,
        "notes": "To be confirmed with the accounting department.",
        "submitted_by": "demo@baitway.local",
        "analyzed_at": datetime(2026, 8, 14, 11, 47, tzinfo=timezone.utc),
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
                "reason": "URL pointing directly at an IP address",
            }
        ],
    },
    {
        "submission_id": "sub_003",
        "subject": "Weekly meeting minutes",
        "sender": "direction@esprim.tn",
        "verdict": Verdict.clean,
        "risk_score": 8,
        "status": SubmissionStatus.resolved,
        "notes": "False positive reported by the user.",
        "submitted_by": "demo@baitway.local",
        "analyzed_at": datetime(2026, 8, 15, 8, 3, tzinfo=timezone.utc),
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
                "filename": "meeting_minutes.pdf",
                "sha256": "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08",
                "reputation": "clean",
                "flags": [],
            }
        ],
        "indicators": [],
    },
]


def main():
    db = SessionLocal()
    created = 0
    try:
        for row in SEED:
            exists = (
                db.query(PhishingSubmission)
                .filter(PhishingSubmission.submission_id == row["submission_id"])
                .first()
            )
            if exists:
                print(f"  = {row['submission_id']} already present, skipped")
                continue
            db.add(PhishingSubmission(**row))
            created += 1
            print(f"  + {row['submission_id']} ({row['verdict'].value}, {row['risk_score']})")
        db.commit()
    finally:
        db.close()
    print(f"\n{created} submission(s) created.")


if __name__ == "__main__":
    main()
