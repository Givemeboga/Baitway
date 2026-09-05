import httpx

from app.core.config import settings

ABUSEIPDB_API = "https://api.abuseipdb.com/api/v2/check"


def check_abuseipdb(indicator: str, ioc_type: str) -> dict:
    """
    Check an IP address against AbuseIPDB. Only meaningful for ioc_type == "ip".
    """
    if ioc_type != "ip":
        return {"name": "AbuseIPDB", "result": "unknown", "score": 0, "raw": {"note": "not applicable for this type"}}

    if not settings.abuseipdb_api_key:
        return {"name": "AbuseIPDB", "result": "unknown", "score": 0, "raw": {"error": "no api key configured"}}

    try:
        headers = {
            "Key": settings.abuseipdb_api_key,
            "Accept": "application/json",
        }
        params = {
            "ipAddress": indicator,
            "maxAgeInDays": 90,
        }
        response = httpx.get(ABUSEIPDB_API, headers=headers, params=params, timeout=10.0)
        response.raise_for_status()
        data = response.json()

        info = data.get("data", {})
        abuse_score = info.get("abuseConfidenceScore", 0)
        total_reports = info.get("totalReports", 0)
        country = info.get("countryCode")
        isp = info.get("isp")

        if abuse_score <= 30:
            result = "clean"
        elif abuse_score <= 70:
            result = "suspicious"
        else:
            result = "malicious"

        return {
            "name": "AbuseIPDB",
            "result": result,
            "score": abuse_score,
            "raw": {
                "abuseConfidenceScore": abuse_score,
                "totalReports": total_reports,
                "countryCode": country,
                "isp": isp,
            }
        }

    except Exception as e:
        return {"name": "AbuseIPDB", "result": "unknown", "score": 0, "raw": {"error": str(e)}}
