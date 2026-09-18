"""Routage des sources du Module B — quelles sources sont interrogees pour
quel type d'indicateur, sans aucun appel reseau."""

import httpx
import pytest

from app.services.enrichment import urlhaus
from app.services.ioc_enrichment import enrich_indicator
from app.services.verdict import calculate_verdict


@pytest.fixture(autouse=True)
def reseau_coupe(monkeypatch):
    """Aucun test de ce fichier ne doit sortir sur le reseau."""
    def refuse(*args, **kwargs):
        raise RuntimeError("appel reseau interdit dans les tests")

    monkeypatch.setattr(httpx, "post", refuse)
    monkeypatch.setattr(httpx, "get", refuse)


# --- Routage des sources ----------------------------------------------------


@pytest.mark.parametrize(
    "ioc_type,attendu",
    [
        ("ip", {"VirusTotal", "AbuseIPDB", "URLhaus"}),
        ("domain", {"VirusTotal", "URLhaus", "WHOIS"}),
        ("url", {"VirusTotal", "URLhaus"}),
        ("hash", {"VirusTotal", "MalwareBazaar"}),
    ],
)
def test_sources_interrogees_par_type(ioc_type, attendu):
    sources, _ = enrich_indicator("x", ioc_type)
    assert {s["name"] for s in sources} == attendu


def test_sources_hors_perimetre_absentes_du_resultat():
    # Une source qui ne couvre pas le type ne doit pas apparaitre a l'analyste.
    sources, _ = enrich_indicator("x", "hash")
    assert "AbuseIPDB" not in {s["name"] for s in sources}
    assert all(
        s.get("raw", {}).get("note") != "not applicable for this type"
        for s in sources
    )


# --- Lecture de l'endpoint /host/ d'URLhaus ---------------------------------


def test_hote_servant_une_charge_en_ligne_est_malveillant():
    data = {"query_status": "ok", "url_count": "3",
            "urls": [{"url_status": "online"}, {"url_status": "offline"}]}
    r = urlhaus._verdict_from_host(data)
    assert r["result"] == "malicious"
    assert r["raw"]["online_urls"] == 1


def test_hote_dont_les_urls_sont_hors_ligne_est_suspect():
    data = {"query_status": "ok", "url_count": "2",
            "urls": [{"url_status": "offline"}]}
    assert urlhaus._verdict_from_host(data)["result"] == "suspicious"


def test_hote_sans_url_connue_est_propre():
    data = {"query_status": "ok", "url_count": "0", "urls": []}
    assert urlhaus._verdict_from_host(data)["result"] == "clean"


def test_urlhaus_refuse_les_types_non_couverts():
    r = urlhaus.check_urlhaus("abc", "hash")
    assert r["raw"]["note"] == "not applicable for this type"


# --- WHOIS ne pese pas sur la note ------------------------------------------


def test_whois_ne_deplace_pas_le_verdict():
    # RDAP renseigne sur l'enregistrement, pas sur la reputation : la source
    # doit etre visible sans jamais modifier le score.
    sans = [{"name": "VirusTotal", "result": "suspicious", "score": 45}]
    avec = sans + [{"name": "WHOIS", "result": "clean", "score": 0}]
    assert calculate_verdict(sans) == calculate_verdict(avec)


def test_whois_seule_source_reste_propre():
    assert calculate_verdict([{"name": "WHOIS", "result": "clean", "score": 0}]) == ("clean", 0)
