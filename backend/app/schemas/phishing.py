from typing import Literal, Optional
from pydantic import BaseModel

Verdict = Literal["clean", "suspicious", "malicious"]
SubmissionStatus = Literal["pending", "reviewed", "resolved"]


class AnalyzeRequest(BaseModel):
    raw_email: str


class SubmissionUpdate(BaseModel):
    verdict: Optional[Verdict] = None
    status: Optional[SubmissionStatus] = None
    notes: Optional[str] = None
