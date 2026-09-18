import httpx

from app.core.config import settings

URLHAUS_URL_API = "https://urlhaus-api.abuse.ch/v1/url/"
URLHAUS_HOST_API = "https://urlhaus-api.abuse.ch/v1/host/"

# URLhaus answers on two endpoints: /url/ for a full URL, /host/ for the
# domain or IP that hosts it. A known malicious URL served from a host is
# evidence about that host, so domains and IPs are worth querying too.
SUPPORTED_TYPES = ("url", "domain", "ip")


def _unknown(raw: dict) -> dict:
    return {"name": "URLhaus", "result": "unknown", "score": 0, "raw": raw}


def _verdict_from_url(data: dict) -> dict:
    """Read a /url/ response: the status of that single URL."""
    url_status = data.get("url_status", "")
    threat = data.get("threat", "")
    raw = {"url_status": url_status, "threat": threat}

    if url_status == "online":
        return {"name": "URLhaus", "result": "malicious", "score": 90, "raw": raw}
    if url_status == "offline":
        return {"name": "URLhaus", "result": "suspicious", "score": 60, "raw": raw}
    return _unknown({"url_status": url_status})


def _verdict_from_host(data: dict) -> dict:
    """
    Read a /host/ response: every malicious URL ever seen on this host.
    A host still serving a live payload is rated harder than one whose
    known URLs are all offline.
    """
    urls = data.get("urls") or []
    online = sum(1 for u in urls if u.get("url_status") == "online")
    raw = {
        "url_count": data.get("url_count"),
        "online_urls": online,
        "firstseen": data.get("firstseen"),
        "blacklists": data.get("blacklists"),
    }

    if online:
        return {"name": "URLhaus", "result": "malicious", "score": 90, "raw": raw}
    if urls:
        return {"name": "URLhaus", "result": "suspicious", "score": 60, "raw": raw}
    return {"name": "URLhaus", "result": "clean", "score": 0, "raw": raw}


def check_urlhaus(indicator: str, ioc_type: str) -> dict:
    """
    Check a URL, domain or IP against URLhaus.
    """
    if ioc_type not in SUPPORTED_TYPES:
        return _unknown({"note": "not applicable for this type"})

    if not settings.abusech_auth_key:
        return _unknown({"error": "no auth key configured"})

    try:
        headers = {"Auth-Key": settings.abusech_auth_key}
        if ioc_type == "url":
            endpoint, payload = URLHAUS_URL_API, {"url": indicator}
        else:
            endpoint, payload = URLHAUS_HOST_API, {"host": indicator}

        response = httpx.post(endpoint, data=payload, headers=headers, timeout=10.0)
        response.raise_for_status()
        data = response.json()

        query_status = data.get("query_status")

        if query_status == "no_results":
            return {"name": "URLhaus", "result": "clean", "score": 0, "raw": {"query_status": query_status}}

        if query_status != "ok":
            return _unknown({"query_status": query_status})

        if ioc_type == "url":
            return _verdict_from_url(data)
        return _verdict_from_host(data)

    except Exception as e:
        return _unknown({"error": str(e)})
