def calculate_verdict(sources: list) -> tuple[str, int]:
    """
    Aggregate individual source scores into one overall verdict + risk_score.
    Ignores sources with result == "unknown" (no data).
    Uses the highest score among applicable sources, since a single strong
    signal (e.g. MalwareBazaar match) should not be diluted by unrelated
    "not applicable" sources.
    """
    applicable_scores = [
        s["score"] for s in sources
        if s.get("result") != "unknown"
    ]

    if not applicable_scores:
        return "clean", 0

    risk_score = max(applicable_scores)

    if risk_score <= 30:
        verdict = "clean"
    elif risk_score <= 70:
        verdict = "suspicious"
    else:
        verdict = "malicious"

    return verdict, risk_score
