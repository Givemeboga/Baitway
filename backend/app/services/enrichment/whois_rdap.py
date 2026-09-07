from datetime import datetime, timezone

import httpx

RDAP_BASE = "https://rdap.org/domain/"


def check_whois_rdap(indicator: str, ioc_type: str) -> dict:
    """
    Look up domain age and registrar via RDAP. Only meaningful for ioc_type == "domain".
    Returns enrichment data, not a verdict — merge this into the enrichment block.
    """
    if ioc_type != "domain":
        return {"domain_age_days": None, "registrar": None}

    try:
        response = httpx.get(f"{RDAP_BASE}{indicator}", timeout=10.0, follow_redirects=True)
        response.raise_for_status()
        data = response.json()

        registrar = None
        for entity in data.get("entities", []):
            if "registrar" in entity.get("roles", []):
                vcard = entity.get("vcardArray", [])
                if len(vcard) > 1:
                    for field in vcard[1]:
                        if field[0] == "fn":
                            registrar = field[3]
                            break

        domain_age_days = None
        for event in data.get("events", []):
            if event.get("eventAction") == "registration":
                reg_date_str = event.get("eventDate")
                if reg_date_str:
                    reg_date = datetime.fromisoformat(reg_date_str.replace("Z", "+00:00"))
                    domain_age_days = (datetime.now(timezone.utc) - reg_date).days

        return {"domain_age_days": domain_age_days, "registrar": registrar}

    except Exception:
        return {"domain_age_days": None, "registrar": None}
