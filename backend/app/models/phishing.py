from sqlalchemy import Column, Integer, String, Text, Enum, DateTime
from sqlalchemy.dialects.postgresql import JSONB
import enum
from app.core.database import Base


class Verdict(str, enum.Enum):
    clean = "clean"
    suspicious = "suspicious"
    malicious = "malicious"


class SubmissionStatus(str, enum.Enum):
    pending = "pending"
    reviewed = "reviewed"
    resolved = "resolved"


class PhishingSubmission(Base):
    """Soumission d'e-mail analysee (Module A).

    Les blocs imbriques de l'analyse (headers, urls, attachments, indicators)
    sont stockes en JSONB : ils sont toujours lus en entier et leur forme est
    fixee par docs/api-contract.md. Les champs filtres ou tries (risk_score,
    verdict, status) restent des colonnes a part entiere.
    """

    __tablename__ = "phishing_submissions"

    id = Column(Integer, primary_key=True, index=True)
    # Identifiant public expose par l'API (le contrat impose une chaine).
    submission_id = Column(String, unique=True, index=True, nullable=False)

    subject = Column(String, nullable=False, default="")
    # "from" est un mot-cle Python : stocke en base sous le nom "sender",
    # serialise en "from" dans les reponses de l'API.
    sender = Column(String, nullable=False, default="")

    verdict = Column(Enum(Verdict), nullable=False, default=Verdict.clean)
    risk_score = Column(Integer, nullable=False, default=0)
    status = Column(Enum(SubmissionStatus), nullable=False, default=SubmissionStatus.pending)
    notes = Column(Text, nullable=False, default="")

    # E-mail de l'analyste ayant soumis (issu du JWT, pas de jointure).
    submitted_by = Column(String, nullable=True, index=True)
    analyzed_at = Column(DateTime(timezone=True), nullable=False)

    headers = Column(JSONB, nullable=False, default=dict)
    urls = Column(JSONB, nullable=False, default=list)
    attachments = Column(JSONB, nullable=False, default=list)
    indicators = Column(JSONB, nullable=False, default=list)
