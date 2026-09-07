import httpx

from app.core.config import settings

URLHAUS_API = "https://urlhaus-api.abuse.ch/v1/url/"


def check_urlhaus(indicator: str, ioc_type: str) -> dict:
    """
    Check a URL against URLhaus. Only meaningful for ioc_type == "url".
    """
    if ioc_type != "url":
        return {"name": "URLhaus", "result": "unknown", "score": 0, "raw": {"note": "not applicable for this type"}}

    if not settings.abusech_auth_key:
        return {"name": "URLhaus", "result": "unknown", "score": 0, "raw": {"error": "no auth key configured"}}

    try:
        headers = {"Auth-Key": settings.abusech_auth_key}
        response = httpx.post(URLHAUS_API, data={"url": indicator}, headers=headers, timeout=10.0)
        response.raise_for_status()
        data = response.json()

        query_status = data.get("query_status")

        if query_status == "no_results":
            return {"name": "URLhaus", "result": "clean", "score": 0, "raw": {"query_status": query_status}}

        if query_status != "ok":
            return {"name": "URLhaus", "result": "unknown", "score": 0, "raw": {"query_status": query_status}}

        url_status = data.get("url_status", "")
        threat = data.get("threat", "")

        if url_status == "online":
            return {"name": "URLhaus", "result": "malicious", "score": 90, "raw": {"url_status": url_status, "threat": threat}}
        elif url_status == "offline":
            return {"name": "URLhaus", "result": "suspicious", "score": 60, "raw": {"url_status": url_status, "threat": threat}}
        else:
            return {"name": "URLhaus", "result": "unknown", "score": 0, "raw": {"url_status": url_status}}

    except Exception as e:
        return {"name": "URLhaus", "result": "unknown", "score": 0, "raw": {"error": str(e)}}
