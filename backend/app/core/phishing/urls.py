"""Analyse des URLs : extraction, defang, raccourcisseurs, typosquatting."""

import ipaddress
import re

URL_RE = re.compile(r"https?://[^\s<>\"'\)\]]+", re.I)
HREF_RE = re.compile(r"href\s*=\s*[\"']([^\"']+)[\"']", re.I)

SHORTENERS = {
    "bit.ly", "tinyurl.com", "goo.gl", "t.co", "ow.ly", "is.gd", "buff.ly",
    "cutt.ly", "rebrand.ly", "shorturl.at", "tiny.cc", "rb.gy", "lnkd.in",
}

# Marques frequemment usurpees (contexte international + tunisien).
WATCHED_DOMAINS = {
    "microsoft.com", "outlook.com", "office365.com", "google.com", "gmail.com",
    "apple.com", "paypal.com", "amazon.com", "facebook.com", "instagram.com",
    "netflix.com", "linkedin.com", "dropbox.com", "docusign.com",
    "ooredoo.tn", "orange.tn", "topnet.tn", "biat.com.tn", "poste.tn", "esprim.tn",
}

CREDENTIAL_PATHS = (
    "login", "signin", "verify", "account", "secure", "update", "confirm",
    "password", "billing", "invoice", "webmail", "auth",
)

SUSPICIOUS_TLDS = {
    ".zip", ".mov", ".tk", ".ml", ".ga", ".cf", ".gq", ".xyz", ".top", ".click",
    ".link", ".work", ".fit", ".rest",
}

# Substitutions visuelles courantes utilisees pour imiter un domaine.
HOMOGLYPHS = str.maketrans({"0": "o", "1": "l", "3": "e", "4": "a", "5": "s", "7": "t", "$": "s"})


def defang(url):
    """Neutralise une URL pour qu'elle ne soit pas cliquable dans l'interface."""
    return url.replace("http://", "hxxp://").replace("https://", "hxxps://").replace(".", "[.]")


def extract_urls(parsed):
    """Extrait les URLs uniques du corps texte et HTML, dans l'ordre d'apparition."""
    found = []
    for raw in URL_RE.findall(parsed["body_text"]):
        found.append(raw.rstrip(".,;:!?"))
    for href in HREF_RE.findall(parsed["body_html"]):
        if href.lower().startswith(("http://", "https://")):
            found.append(href.rstrip(".,;:!?"))
    for raw in URL_RE.findall(re.sub(r"<[^>]+>", " ", parsed["body_html"])):
        found.append(raw.rstrip(".,;:!?"))

    seen = set()
    unique = []
    for url in found:
        if url not in seen:
            seen.add(url)
            unique.append(url)
    return unique


def host_of(url):
    without_scheme = re.sub(r"^https?://", "", url, flags=re.I)
    host = without_scheme.split("/")[0].split("?")[0]
    # Astuce "user@host" : seul ce qui suit le @ est le vrai hote.
    if "@" in host:
        host = host.split("@")[-1]
    return host.split(":")[0].lower()


def registered_domain(host):
    """Approximation du domaine enregistrable (gere les suffixes composes .co.uk, .com.tn)."""
    parts = host.split(".")
    if len(parts) < 3:
        return host
    if parts[-2] in {"com", "co", "org", "net", "gov", "edu"} and len(parts[-1]) == 2:
        return ".".join(parts[-3:])
    return ".".join(parts[-2:])


def _levenshtein(a, b):
    if a == b:
        return 0
    previous = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        current = [i]
        for j, cb in enumerate(b, 1):
            current.append(min(previous[j] + 1, current[j - 1] + 1, previous[j - 1] + (ca != cb)))
        previous = current
    return previous[-1]


def detect_typosquat(host):
    """Detecte un domaine sosie d'une marque surveillee.

    Renvoie le domaine imite, ou None.
    """
    domain = registered_domain(host)
    if domain in WATCHED_DOMAINS:
        return None

    normalised = domain.translate(HOMOGLYPHS)
    for watched in WATCHED_DOMAINS:
        if normalised == watched:
            return watched
        watched_name = watched.split(".")[0]
        domain_name = domain.split(".")[0]
        # Marque presente dans un domaine tiers : micros0ft-verify.com, paypal.security.xyz
        # La comparaison se fait sur la forme normalisee, sinon les substitutions
        # visuelles (0 pour o, 1 pour l) font echouer la detection.
        if watched_name in normalised and domain != watched and len(watched_name) > 4:
            return watched
        # Faute de frappe proche : rnicrosoft.com, gogle.com
        if len(domain_name) > 4 and _levenshtein(normalised.split(".")[0], watched_name) == 1:
            return watched
    return None


def analyse_url(url):
    """Analyse une URL et renvoie son entree de contrat + ses signaux."""
    host = host_of(url)
    flags = []
    signals = []

    if host in SHORTENERS or registered_domain(host) in SHORTENERS:
        flags.append("shortener")
        signals.append(("url_shortener", f"URL shortener ({host})"))

    is_ip = False
    try:
        ipaddress.ip_address(host)
        is_ip = True
    except ValueError:
        pass
    if is_ip:
        flags.append("ip_based")
        signals.append(("url_ip_based", f"URL pointing to a raw IP ({host})"))

    imitated = detect_typosquat(host) if not is_ip else None
    if imitated:
        flags.append("typosquat")
        signals.append(("url_typosquat", f"{host} imitates {imitated}"))

    lowered = url.lower()
    if any(word in lowered for word in CREDENTIAL_PATHS):
        flags.append("credential_harvest")
        signals.append(("url_credential_path", f"Credential-harvesting path ({host})"))

    if host.startswith("xn--") or ".xn--" in host:
        flags.append("punycode")
        signals.append(("url_punycode", f"Punycode domain ({host})"))

    if any(host.endswith(tld) for tld in SUSPICIOUS_TLDS):
        flags.append("suspicious_tld")
        signals.append(("url_suspicious_tld", f"Risky TLD ({host})"))

    if "@" in re.sub(r"^https?://", "", url).split("/")[0]:
        flags.append("at_obfuscation")
        signals.append(("url_at_trick", "URL hiding its real host with an @"))

    if url.lower().startswith("http://"):
        flags.append("no_tls")

    # Reputation locale, deduite des signaux (pas d'appel externe a ce stade).
    strong = {"typosquat", "ip_based", "punycode", "at_obfuscation"}
    if strong & set(flags):
        reputation = "malicious"
    elif flags and flags != ["no_tls"]:
        reputation = "suspicious"
    elif flags:
        reputation = "unknown"
    else:
        reputation = "unknown"

    return {
        "url": url,
        "defanged": defang(url),
        "reputation": reputation,
        "flags": flags,
    }, signals


def analyse_urls(parsed):
    """Analyse toutes les URLs du message."""
    entries = []
    signals = []
    for url in extract_urls(parsed):
        entry, url_signals = analyse_url(url)
        entries.append(entry)
        signals.extend(url_signals)
    return entries, signals
