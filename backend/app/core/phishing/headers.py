"""Analyse des en-têtes : authentification SPF/DKIM/DMARC, usurpation, IP d'origine."""

import ipaddress
import re

AUTH_RE = {
    "spf": re.compile(r"\bspf\s*=\s*(\w+)", re.I),
    "dkim": re.compile(r"\bdkim\s*=\s*(\w+)", re.I),
    "dmarc": re.compile(r"\bdmarc\s*=\s*(\w+)", re.I),
}

IP_RE = re.compile(r"\[?(\d{1,3}(?:\.\d{1,3}){3})\]?")
# Un resultat d'authentification qui n'est ni pass ni none est traite comme fail.
PASS_VALUES = {"pass"}
NONE_VALUES = {"none", "neutral", "policy", "unknown", "temperror", "permerror"}


def _normalise(value):
    value = (value or "").lower()
    if value in PASS_VALUES:
        return "pass"
    if value in NONE_VALUES:
        return "none"
    return "fail"


def extract_auth(parsed):
    """Extrait spf / dkim / dmarc des en-têtes d'authentification."""
    blob = " ".join(parsed["auth_results"])
    results = {}
    for name, regex in AUTH_RE.items():
        match = regex.search(blob)
        results[name] = _normalise(match.group(1)) if match else "none"

    # Repli sur Received-SPF si Authentication-Results ne dit rien du SPF.
    if results["spf"] == "none" and parsed["received_spf"]:
        first = parsed["received_spf"][0].strip().split()[0] if parsed["received_spf"][0].strip() else ""
        results["spf"] = _normalise(first)

    return results


# Plages internes a ignorer. Volontairement plus etroit que `is_private` :
# Python classe les plages de documentation (RFC 5737, ex. 203.0.113.0/24)
# comme privees alors qu'elles servent justement d'IP d'origine en demo.
INTERNAL_NETWORKS = tuple(
    ipaddress.ip_network(cidr)
    for cidr in ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16", "127.0.0.0/8", "169.254.0.0/16")
)


def is_internal(ip):
    return any(ip in network for network in INTERNAL_NETWORKS)


def extract_origin_ip(parsed):
    """IP d'origine : premiere IP externe trouvee dans le dernier Received."""
    for header in reversed(parsed["received"]):
        for candidate in IP_RE.findall(header):
            try:
                ip = ipaddress.ip_address(candidate)
            except ValueError:
                continue
            if not is_internal(ip):
                return str(ip)
    return ""


def domain_of(address):
    return address.split("@")[-1].lower() if "@" in address else ""


def analyse_headers(parsed):
    """Renvoie le bloc `headers` du contrat + les signaux detectes."""
    auth = extract_auth(parsed)
    origin_ip = extract_origin_ip(parsed)

    signals = []
    for mechanism in ("spf", "dkim", "dmarc"):
        if auth[mechanism] == "fail":
            signals.append((f"auth_{mechanism}_fail", f"{mechanism.upper()} en echec"))
        elif auth[mechanism] == "none":
            signals.append((f"auth_{mechanism}_none", f"{mechanism.upper()} absent"))

    from_domain = domain_of(parsed["from_addr"])
    reply_domain = domain_of(parsed["reply_to"])
    if reply_domain and from_domain and reply_domain != from_domain:
        signals.append(
            ("reply_to_mismatch", f"Reply-To ({reply_domain}) different du From ({from_domain})")
        )

    # Nom d'affichage contenant une adresse differente de l'expediteur reel.
    display = parsed["from_display"] or ""
    display_match = re.search(r"[\w.+-]+@([\w.-]+)", display)
    if display_match and from_domain and display_match.group(1).lower() != from_domain:
        signals.append(
            ("display_name_spoof", f"Nom d'affichage usurpe ({display_match.group(1)})")
        )

    block = {
        "spf": auth["spf"],
        "dkim": auth["dkim"],
        "dmarc": auth["dmarc"],
        "from": parsed["from_addr"],
        "reply_to": parsed["reply_to"],
        "origin_ip": origin_ip,
    }
    return block, signals
