"""Conformite des reponses au contrat d'API partage (docs/api-contract.md).

Ces tests protegent l'interface entre les deux modules : ils echouent des
qu'une reponse s'ecarte de la forme convenue avec le binome.
"""

import re

ISO_Z = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")

PHISHING_EML = """From: "Ooredoo" <billing@0oredoo.tn>
Reply-To: recouvrement@mail.ru
Subject: URGENT - Votre facture est impayee
Authentication-Results: mx.esprim.tn; spf=fail; dkim=fail; dmarc=fail
Received: from unknown (HELO x) (45.133.1.87) by mx.esprim.tn
Content-Type: text/html

<html><body><p>Cher client, votre ligne sera suspendue sous 24h.
Verifiez votre compte immediatement.</p>
<a href="http://0oredoo.tn/login/verify">Payer</a></body></html>
"""

ANALYSE_FIELDS = {
    "submission_id", "verdict", "risk_score", "headers",
    "urls", "attachments", "indicators", "analyzed_at",
}
QUEUE_FIELDS = {
    "submission_id", "subject", "from", "verdict",
    "risk_score", "status", "analyzed_at",
}
ATTACHMENT_FIELDS = {"filename", "sha256", "reputation", "flags"}


# --- Module A ---------------------------------------------------------------


def test_analyse_respecte_les_champs_du_contrat(client, auth):
    r = client.post("/phishing/analyze", json={"raw_email": PHISHING_EML}, headers=auth)
    assert r.status_code == 200
    body = r.json()
    assert set(body) == ANALYSE_FIELDS
    assert body["verdict"] in {"clean", "suspicious", "malicious"}
    assert isinstance(body["risk_score"], int)
    assert ISO_Z.match(body["analyzed_at"]), body["analyzed_at"]
    assert set(body["headers"]) == {"spf", "dkim", "dmarc", "from", "reply_to", "origin_ip"}
    for a in body["attachments"]:
        assert set(a) == ATTACHMENT_FIELDS


def test_file_de_triage_triee_par_risque(client, auth):
    for _ in range(2):
        client.post("/phishing/analyze", json={"raw_email": PHISHING_EML}, headers=auth)
    r = client.get("/phishing/submissions", headers=auth)
    assert r.status_code == 200
    items = r.json()["submissions"]
    assert items, "la file ne doit pas etre vide"
    assert set(items[0]) == QUEUE_FIELDS
    scores = [i["risk_score"] for i in items]
    assert scores == sorted(scores, reverse=True)


def test_detail_et_mise_a_jour_du_verdict(client, auth):
    sub = client.post(
        "/phishing/analyze", json={"raw_email": PHISHING_EML}, headers=auth
    ).json()["submission_id"]

    detail = client.get(f"/phishing/submissions/{sub}", headers=auth)
    assert detail.status_code == 200
    assert {"status", "notes", "subject"} <= set(detail.json())

    patched = client.patch(
        f"/phishing/submissions/{sub}",
        json={"status": "resolved", "notes": "confirme"},
        headers=auth,
    )
    assert patched.status_code == 200
    assert patched.json()["status"] == "resolved"
    assert patched.json()["notes"] == "confirme"


def test_verdict_hors_vocabulaire_refuse(client, auth):
    sub = client.post(
        "/phishing/analyze", json={"raw_email": PHISHING_EML}, headers=auth
    ).json()["submission_id"]
    r = client.patch(
        f"/phishing/submissions/{sub}", json={"verdict": "dangerous"}, headers=auth
    )
    assert r.status_code == 422


def test_soumission_introuvable(client, auth):
    assert client.get("/phishing/submissions/inexistant", headers=auth).status_code == 404


def test_email_vide_refuse(client, auth):
    assert client.post("/phishing/analyze", json={"raw_email": "   "}, headers=auth).status_code == 400


def test_email_trop_volumineux_refuse(client, auth):
    r = client.post(
        "/phishing/analyze", json={"raw_email": "A" * (11 * 1024 * 1024)}, headers=auth
    )
    assert r.status_code == 422


# --- Module B ---------------------------------------------------------------


def test_historique_ioc_utilise_l_enveloppe_du_contrat(client, auth):
    # Regression : la route renvoyait un tableau nu au lieu de { lookups: [...] }.
    r = client.get("/ioc/history", headers=auth)
    assert r.status_code == 200
    body = r.json()
    assert isinstance(body, dict), "le contrat impose un objet, pas un tableau"
    assert "lookups" in body
    for row in body["lookups"]:
        assert isinstance(row["risk_score"], int)
        assert ISO_Z.match(row["looked_up_at"]), row["looked_up_at"]


def test_indicateur_non_reconnu_refuse(client, auth):
    r = client.post("/ioc/lookup", json={"indicator": "pas un indicateur !!"}, headers=auth)
    assert r.status_code == 400


def test_recherche_introuvable(client, auth):
    assert client.get("/ioc/lookups/inexistant", headers=auth).status_code == 404


def test_export_renvoie_un_fichier(client, auth):
    csv = client.get("/ioc/export", headers=auth)
    assert csv.status_code == 200
    assert "text/csv" in csv.headers["content-type"]
    assert csv.text.splitlines()[0].startswith("lookup_id,indicator")

    blocklist = client.get("/ioc/export?format=blocklist", headers=auth)
    assert blocklist.status_code == 200

    assert client.get("/ioc/export?format=xml", headers=auth).status_code == 400


# --- Socle ------------------------------------------------------------------


def test_sante(client):
    r = client.get("/health")
    assert r.status_code == 200 and r.json()["status"] == "ok"


def test_tous_les_endpoints_du_contrat_sont_montes(client):
    paths = set(client.get("/openapi.json").json()["paths"])
    attendus = {
        "/health", "/auth/register", "/auth/login",
        "/phishing/analyze", "/phishing/submissions",
        "/phishing/submissions/{submission_id}",
        "/ioc/lookup", "/ioc/history", "/ioc/lookups/{lookup_id}", "/ioc/export",
    }
    assert attendus <= paths, attendus - paths
