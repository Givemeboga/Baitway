"""Moteur de scoring pondere : signaux -> score 0-100 -> verdict.

L'echelle de verdict est commune aux deux modules (docs/api-contract.md) :
0-30 clean, 31-70 suspicious, 71-100 malicious.
"""

WEIGHTS = {
    # Authentification
    "auth_spf_fail": 15,
    "auth_dkim_fail": 12,
    "auth_dmarc_fail": 15,
    "auth_spf_none": 5,
    "auth_dkim_none": 4,
    "auth_dmarc_none": 5,
    "reply_to_mismatch": 12,
    "display_name_spoof": 15,
    # URLs
    "url_typosquat": 30,
    "url_ip_based": 20,
    "url_punycode": 20,
    "url_at_trick": 20,
    "url_credential_path": 12,
    "url_shortener": 10,
    "url_suspicious_tld": 10,
    # Pieces jointes
    "attachment_dangerous": 30,
    "attachment_double_extension": 25,
    "attachment_macro": 18,
    "attachment_archive": 8,
    # Contenu
    "content_credentials": 12,
    "content_threat": 10,
    "content_urgency": 8,
    "content_money": 8,
    "content_generic_greeting": 4,
}

# Un meme type de signal repete (plusieurs URLs douteuses) ne doit pas faire
# exploser le score : la 2e occurrence compte a moitie, au-dela plus rien.
REPEAT_FACTORS = (1.0, 0.5)

CLEAN_MAX = 30
SUSPICIOUS_MAX = 70


def verdict_from_score(score):
    if score <= CLEAN_MAX:
        return "clean"
    if score <= SUSPICIOUS_MAX:
        return "suspicious"
    return "malicious"


def severity_from_weight(weight):
    if weight >= 20:
        return "high"
    if weight >= 10:
        return "medium"
    return "low"


def score_signals(signals):
    """Additionne les poids des signaux et renvoie (score, decomposition).

    `signals` est une liste de tuples (identifiant, raison lisible).
    """
    counts = {}
    breakdown = []
    total = 0.0

    for name, reason in signals:
        weight = WEIGHTS.get(name, 0)
        if not weight:
            continue
        seen = counts.get(name, 0)
        factor = REPEAT_FACTORS[seen] if seen < len(REPEAT_FACTORS) else 0.0
        counts[name] = seen + 1
        points = weight * factor
        if points:
            total += points
            breakdown.append(
                {
                    "signal": name,
                    "reason": reason,
                    "points": round(points),
                    "severity": severity_from_weight(weight),
                }
            )

    score = max(0, min(100, round(total)))
    return score, breakdown
