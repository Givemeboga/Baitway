import base64
import httpx

from app.core.config import settings

VT_BASE_URL = "https://www.virustotal.com/api/v3"


def _vt_headers() -> dict:
    return {"x-apikey": settings.virustotal_api_key}


def _score_to_result(malicious: int, suspicious: int, total: int) -> tuple[str, int]:
    if total == 0:
        return "unknown", 0

    score = round(((malicious * 2) + suspicious) / (total * 2) * 100)
    score = min(score, 100)

    if score <= 30:
        result = "clean"
    elif score <= 70:
        result = "suspicious"
    else:
        result = "malicious"

    return result, score


def check_virustotal(indicator: str, ioc_type: str) -> dict:
    if not settings.virustotal_api_key:
        return {"name": "VirusTotal", "result": "unknown", "score": 0, "raw": {"error": "no api key configured"}}

    try:
        if ioc_type == "ip":
            url = f"{VT_BASE_URL}/ip_addresses/{indicator}"
        elif ioc_type == "domain":
            url = f"{VT_BASE_URL}/domains/{indicator}"
        elif ioc_type == "hash":
            url = f"{VT_BASE_URL}/files/{indicator}"
        elif ioc_type == "url":
            url_id = base64.urlsafe_b64encode(indicator.encode()).decode().strip("=")
            url = f"{VT_BASE_URL}/urls/{url_id}"
        else:
            return {"name": "VirusTotal", "result": "unknown", "score": 0, "raw": {"error": f"unsupported type {ioc_type}"}}

        response = httpx.get(url, headers=_vt_headers(), timeout=10.0)

        if response.status_code == 404:
            return {"name": "VirusTotal", "result": "unknown", "score": 0, "raw": {"note": "not found in VT"}}

        response.raise_for_status()
        data = response.json()

        stats = data["data"]["attributes"]["last_analysis_stats"]
        malicious = stats.get("malicious", 0)
        suspicious = stats.get("suspicious", 0)
        total = sum(stats.values())

        result, score = _score_to_result(malicious, suspicious, total)

        return {"name": "VirusTotal", "result": result, "score": score, "raw": stats}

    except httpx.HTTPStatusError as e:
        return {"name": "VirusTotal", "result": "unknown", "score": 0, "raw": {"error": str(e)}}
    except Exception as e:
        return {"name": "VirusTotal", "result": "unknown", "score": 0, "raw": {"error": str(e)}}
