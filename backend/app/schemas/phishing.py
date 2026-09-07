from typing import Literal, Optional

from pydantic import BaseModel, Field

Verdict = Literal["clean", "suspicious", "malicious"]
SubmissionStatus = Literal["pending", "reviewed", "resolved"]

# Un .eml est analyse entierement en memoire : on borne la taille acceptee.
# 10 Mo couvrent tres largement un message avec pieces jointes encodees.
RAW_EMAIL_MAX = 10 * 1024 * 1024
NOTES_MAX = 5000


class AnalyzeRequest(BaseModel):
    raw_email: str = Field(max_length=RAW_EMAIL_MAX)


class SubmissionUpdate(BaseModel):
    verdict: Optional[Verdict] = None
    status: Optional[SubmissionStatus] = None
    notes: Optional[str] = Field(default=None, max_length=NOTES_MAX)
