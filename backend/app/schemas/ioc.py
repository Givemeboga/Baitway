from typing import Literal
from pydantic import BaseModel


Verdict = Literal["clean", "suspicious", "malicious"]
IOCType = Literal["ip", "domain", "url", "hash"]


class LookupRequest(BaseModel):
    indicator: str