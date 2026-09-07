from app.services.enrichment.virustotal import check_virustotal
from app.services.enrichment.abuseipdb import check_abuseipdb
from app.services.enrichment.urlhaus import check_urlhaus
from app.services.enrichment.malwarebazaar import check_malwarebazaar
from app.services.enrichment.whois_rdap import check_whois_rdap


def enrich_indicator(indicator: str, ioc_type: str) -> tuple[list, dict]:
    """
    Calls all relevant enrichment sources for the given indicator/type.
    Returns (sources_list, enrichment_dict).
    """
    sources = []

    # VirusTotal applies to all types
    sources.append(check_virustotal(indicator, ioc_type))

    if ioc_type == "ip":
        sources.append(check_abuseipdb(indicator, ioc_type))

    if ioc_type == "url":
        sources.append(check_urlhaus(indicator, ioc_type))

    if ioc_type == "hash":
        sources.append(check_malwarebazaar(indicator, ioc_type))

    # Filter out "not applicable for this type" no-op results so they
    # do not pollute the sources list shown to the analyst
    sources = [
        s for s in sources
        if s.get("raw", {}).get("note") != "not applicable for this type"
    ]

    enrichment = {
        "geolocation": None,
        "asn": None,
        "domain_age_days": None,
        "registrar": None,
        "blacklisted": any(s["result"] == "malicious" for s in sources),
    }

    if ioc_type == "domain":
        whois_data = check_whois_rdap(indicator, ioc_type)
        enrichment["domain_age_days"] = whois_data.get("domain_age_days")
        enrichment["registrar"] = whois_data.get("registrar")

    if ioc_type == "ip":
        # AbuseIPDB result already fetched above; pull geolocation from its raw data
        abuseipdb_result = next((s for s in sources if s["name"] == "AbuseIPDB"), None)
        if abuseipdb_result:
            enrichment["geolocation"] = abuseipdb_result["raw"].get("countryCode")

    return sources, enrichment
