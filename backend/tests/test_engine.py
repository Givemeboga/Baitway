"""Moteur d'analyse .eml (Module A) — tests unitaires, sans base de donnees."""

import pytest

from app.core.phishing import analyse_raw_email
from app.core.phishing.attachments import analyse_attachment
from app.core.phishing.headers import extract_origin_ip, is_internal
from app.core.phishing.scoring import score_signals, verdict_from_score
from app.core.phishing.urls import defang, detect_typosquat, host_of

# --- Echelle de verdict (contrat d'API, commune aux deux modules) -----------


@pytest.mark.parametrize(
    "score,expected",
    [(0, "clean"), (30, "clean"), (31, "suspicious"), (70, "suspicious"),
     (71, "malicious"), (100, "malicious")],
)
def test_verdict_respecte_les_bornes_du_contrat(score, expected):
    assert verdict_from_score(score) == expected


# --- Neutralisation des URLs ------------------------------------------------


def test_defang_rend_l_url_non_cliquable():
    assert defang("http://0oredoo.tn/login") == "hxxp://0oredoo[.]tn/login"
    assert defang("https://a.b/c") == "hxxps://a[.]b/c"


def test_host_of_ignore_le_leurre_arobase():
    # http://confiance.tn@mechant.tn : le vrai hote est celui apres le @
    assert host_of("http://confiance.tn@mechant.tn/x") == "mechant.tn"


# --- Typosquatting ----------------------------------------------------------


def test_typosquat_detecte_la_substitution_visuelle():
    # Regression : la comparaison doit porter sur la forme normalisee, sinon
    # le zero de "0oredoo" empeche toute correspondance.
    assert detect_typosquat("0oredoo.tn") == "ooredoo.tn"
    assert detect_typosquat("micros0ft-verify.com") == "microsoft.com"


def test_typosquat_ne_signale_pas_le_domaine_legitime():
    assert detect_typosquat("ooredoo.tn") is None
    assert detect_typosquat("microsoft.com") is None


# --- Pieces jointes ---------------------------------------------------------


def test_double_extension_est_malveillante():
    entry, signals = analyse_attachment(
        {"filename": "facture.pdf.exe", "payload": b"MZ", "size": 2}
    )
    assert entry["reputation"] == "malicious"
    assert "dangerous_extension" in entry["flags"]
    assert "double_extension" in entry["flags"]
    assert entry["sha256"] and entry["md5"]


def test_piece_jointe_benigne_n_est_pas_signalee():
    entry, _ = analyse_attachment(
        {"filename": "compte_rendu.pdf", "payload": b"%PDF-1.4", "size": 8}
    )
    assert entry["flags"] == []


# --- Adresse IP d'origine ---------------------------------------------------


def test_plages_de_documentation_ne_sont_pas_traitees_comme_internes():
    # Regression : ipaddress classe 203.0.113.0/24 (RFC 5737) comme privee,
    # ce qui vidait origin_ip sur tous les jeux d'essai.
    import ipaddress

    assert not is_internal(ipaddress.ip_address("203.0.113.44"))
    assert is_internal(ipaddress.ip_address("192.168.1.1"))
    assert is_internal(ipaddress.ip_address("10.0.0.1"))


def test_origin_ip_lue_dans_le_dernier_received():
    parsed = {"received": ["from x (203.0.113.44) by mx.esprim.tn"]}
    assert extract_origin_ip(parsed) == "203.0.113.44"


# --- Pondération ------------------------------------------------------------


def test_rendements_decroissants_sur_signal_repete():
    once = score_signals([("url_shortener", "r")])[0]
    twice = score_signals([("url_shortener", "r"), ("url_shortener", "r")])[0]
    many = score_signals([("url_shortener", "r")] * 6)[0]
    assert twice > once           # la 2e occurrence compte
    assert twice < once * 2       # ... mais a moitie
    assert many == twice          # au-dela, plus rien


def test_score_plafonne_a_100():
    # Il faut des signaux de types differents : les rendements decroissants
    # empechent un seul type de depasser une fois et demie son poids.
    signals = [
        ("url_typosquat", "r"),            # 30
        ("attachment_dangerous", "r"),     # 30
        ("attachment_double_extension", "r"),  # 25
        ("auth_spf_fail", "r"),            # 15
        ("auth_dmarc_fail", "r"),          # 15
    ]                                      # total brut : 115
    score, breakdown = score_signals(signals)
    assert sum(b["points"] for b in breakdown) > 100
    assert score == 100


# --- Analyse de bout en bout ------------------------------------------------

PHISHING = """From: "Ooredoo" <billing@0oredoo.tn>
Reply-To: recouvrement@mail.ru
Subject: URGENT - Votre facture est impayee
Authentication-Results: mx.esprim.tn; spf=fail; dkim=fail; dmarc=fail
Received: from unknown (HELO x) (45.133.1.87) by mx.esprim.tn
Content-Type: text/html

<html><body><p>Cher client, votre ligne sera suspendue sous 24h.
Verifiez votre compte immediatement.</p>
<a href="http://0oredoo.tn/login/verify">Payer</a></body></html>
"""

LEGITIME = """From: Direction <direction@esprim.tn>
Subject: Compte rendu de reunion
Authentication-Results: mx.esprim.tn; spf=pass; dkim=pass; dmarc=pass
Received: from mail.esprim.tn (192.0.2.10) by mx.esprim.tn
Content-Type: text/plain

Bonjour, le compte rendu est sur https://www.esprim.tn/intranet
"""


def test_phishing_reel_est_malveillant():
    r = analyse_raw_email(PHISHING)
    assert r["verdict"] == "malicious"
    assert r["risk_score"] >= 71
    assert r["headers"]["spf"] == "fail"
    assert r["headers"]["origin_ip"] == "45.133.1.87"
    assert any("typosquat" in u["flags"] for u in r["urls"])
    assert any(i["type"] == "domain" for i in r["indicators"])


def test_message_legitime_reste_propre():
    # Un outil qui signale le courrier legitime cesse d'etre utilise.
    r = analyse_raw_email(LEGITIME)
    assert r["verdict"] == "clean"
    assert r["risk_score"] <= 30


def test_authentification_absente_ne_suffit_pas_a_alerter():
    # Regression observee sur un vrai courrier commercial : sans en-tetes
    # d'authentification le score monte, mais doit rester "clean".
    r = analyse_raw_email("From: a@b.tn\nSubject: bonjour\n\ntexte neutre\n")
    assert r["verdict"] == "clean"


def test_email_malforme_ne_leve_pas():
    for raw in ["", "n'importe quoi", "\x00\x01\x02", "From: sans corps"]:
        r = analyse_raw_email(raw)
        assert r["verdict"] in ("clean", "suspicious", "malicious")


def test_piece_jointe_jamais_ecrite_sur_disque(tmp_path, monkeypatch):
    # Garde-fou : l'analyse ne doit ouvrir aucun fichier en ecriture.
    import builtins

    real_open = builtins.open

    def guarded(file, mode="r", *a, **k):
        assert "w" not in mode and "a" not in mode and "x" not in mode, (
            f"ecriture interdite pendant l'analyse : {file!r} en mode {mode!r}"
        )
        return real_open(file, mode, *a, **k)

    monkeypatch.setattr(builtins, "open", guarded)
    analyse_raw_email(PHISHING)
