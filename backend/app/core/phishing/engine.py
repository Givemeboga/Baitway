"""Orchestrateur du moteur d'analyse phishing.

Enchaine parseur -> en-têtes -> URLs -> pieces jointes -> contenu -> scoring,
et renvoie un resultat directement exploitable par la couche API.
"""

from app.core.phishing.attachments import analyse_attachments
from app.core.phishing.content import analyse_content
from app.core.phishing.headers import analyse_headers
from app.core.phishing.parser import parse_email
from app.core.phishing.scoring import score_signals, severity_from_weight, verdict_from_score
from app.core.phishing.urls import host_of


def _build_indicators(header_block, url_entries, attachment_entries, header_signals):
    """Construit la liste d'IOC extraits (type / value / severity / reason)."""
    indicators = []

    origin_ip = header_block.get("origin_ip")
    if origin_ip:
        auth_failed = any(name.endswith("_fail") for name, _ in header_signals)
        indicators.append(
            {
                "type": "ip",
                "value": origin_ip,
                "severity": "medium" if auth_failed else "low",
                "reason": "Originating IP of the message"
                + (" (authentication failed)" if auth_failed else ""),
            }
        )

    for entry in url_entries:
        if entry["reputation"] not in ("malicious", "suspicious"):
            continue
        severity = "high" if entry["reputation"] == "malicious" else "medium"
        if "typosquat" in entry["flags"]:
            indicators.append(
                {
                    "type": "domain",
                    "value": host_of(entry["url"]),
                    "severity": severity,
                    "reason": "Lookalike of a known brand domain (typosquatting)",
                }
            )
        else:
            indicators.append(
                {
                    "type": "url",
                    "value": entry["url"],
                    "severity": severity,
                    "reason": "Suspicious URL: " + ", ".join(entry["flags"]),
                }
            )

    for entry in attachment_entries:
        if not entry["flags"]:
            continue
        indicators.append(
            {
                "type": "hash",
                "value": entry["sha256"],
                "severity": "high" if entry["reputation"] == "malicious" else "medium",
                "reason": f"Attachment {entry['filename']}: " + ", ".join(entry["flags"]),
            }
        )

    return indicators


def analyse_raw_email(raw_email):
    """Analyse un e-mail brut (.eml) et renvoie le resultat complet.

    Le dict renvoye contient les blocs du contrat d'API (headers, urls,
    attachments, indicators, verdict, risk_score) ainsi que subject / sender
    pour la persistance et la file de triage, et breakdown pour la
    decomposition du score.
    """
    parsed = parse_email(raw_email)

    header_block, header_signals = analyse_headers(parsed)
    url_entries, url_signals = analyse_urls_safe(parsed)
    attachment_entries, attachment_signals = analyse_attachments(parsed)
    content_signals = analyse_content(parsed)

    signals = header_signals + url_signals + attachment_signals + content_signals
    risk_score, breakdown = score_signals(signals)

    return {
        "subject": parsed["subject"],
        "sender": parsed["from_addr"],
        "verdict": verdict_from_score(risk_score),
        "risk_score": risk_score,
        "headers": header_block,
        "urls": url_entries,
        "attachments": attachment_entries,
        "indicators": _build_indicators(
            header_block, url_entries, attachment_entries, header_signals
        ),
        "breakdown": breakdown,
    }


def analyse_urls_safe(parsed):
    """Isole l'analyse des URLs : une URL exotique ne doit pas casser l'analyse."""
    from app.core.phishing.urls import analyse_urls

    try:
        return analyse_urls(parsed)
    except Exception:
        return [], []
