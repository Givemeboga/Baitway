"""Analyse du contenu : urgence, collecte d'identifiants, appats financiers.

Les motifs couvrent le francais et l'anglais : les campagnes visant la Tunisie
melangent frequemment les deux langues.
"""

import re

PATTERNS = {
    "content_urgency": (
        "Urgency pressure designed to prevent thinking",
        [
            r"\burgent\b", r"\bimmediat", r"\bimm[ée]diat", r"sous \d+ ?h",
            r"\bexpire", r"\bderni[eè]re? (chance|avertissement|rappel)",
            r"\bact now\b", r"\bwithin \d+ hours?\b", r"\bas soon as possible\b",
            r"\bd[eé]lai\b", r"\bsans tarder\b",
        ],
    ),
    "content_threat": (
        "Threat of suspension or penalty",
        [
            r"\bsuspend", r"\bsuspendu", r"\bdesactiv", r"\bd[ée]sactiv",
            r"\bblocked?\b", r"\bbloqu[ée]", r"\bcl[oô]tur", r"\bterminated\b",
            r"\bfermeture (de|du) (votre )?compte", r"\blegal action\b",
            r"\bpoursuites?\b", r"\bamende\b",
        ],
    ),
    "content_credentials": (
        "Request for credentials or personal data",
        [
            r"\bmot de passe\b", r"\bpassword\b", r"\bidentifiants?\b",
            r"\bcredentials?\b", r"\bv[ée]rifi(er|ez) votre compte\b",
            r"\bverify your account\b", r"\bconfirm your (identity|account)\b",
            r"\bconnectez[- ]vous\b", r"\bsign in to\b", r"\bmettre a jour vos informations\b",
            r"\bcode (de )?(v[ée]rification|otp|pin)\b",
        ],
    ),
    "content_money": (
        "Financial bait (invoice, payment, refund)",
        [
            r"\bfacture\b", r"\binvoice\b", r"\bpaiement\b", r"\bpayment\b",
            r"\bremboursement\b", r"\brefund\b", r"\bvirement\b", r"\bwire transfer\b",
            r"\bcarte bancaire\b", r"\bcredit card\b", r"\brib\b", r"\biban\b",
            r"\bimp[aâ]y[ée]", r"\boverdue\b", r"\bgagn[ée]\b", r"\bwinner\b",
        ],
    ),
    "content_generic_greeting": (
        "Generic greeting (no personalisation)",
        [
            r"\bcher (client|utilisateur|abonn[ée]|membre)\b",
            r"\bdear (customer|user|sir|madam|account holder)\b",
            r"\bbonjour cher\b", r"\bvalued customer\b",
        ],
    ),
}

COMPILED = {
    name: (reason, [re.compile(p, re.I) for p in patterns])
    for name, (reason, patterns) in PATTERNS.items()
}


def analyse_content(parsed):
    """Detecte les marqueurs de phishing dans le sujet et le corps du message."""
    haystack = " ".join(
        [
            parsed["subject"],
            parsed["body_text"],
            # Le HTML est nettoye de ses balises pour ne garder que le texte visible.
            re.sub(r"<[^>]+>", " ", parsed["body_html"]),
        ]
    )

    signals = []
    for name, (reason, regexes) in COMPILED.items():
        for regex in regexes:
            if regex.search(haystack):
                signals.append((name, reason))
                break
    return signals
