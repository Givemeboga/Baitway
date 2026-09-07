"""Authentification : identifiants hors des URLs, validation, non-divulgation."""


def test_identifiants_dans_le_corps(client):
    r = client.post(
        "/auth/register",
        json={"email": "corps@soc.local", "password": "MotDePasseSolide9"},
    )
    assert r.status_code == 200
    assert r.json() == {"message": "Account created"}


def test_identifiants_refuses_en_parametres_d_url(client):
    # Regression : un mot de passe en query string finit dans les journaux
    # d'acces, l'historique du navigateur et les proxies.
    r = client.post("/auth/login?email=a@b.tn&password=MotDePasseSolide9")
    assert r.status_code == 422


def test_connexion_renvoie_un_jeton(client, account):
    r = client.post("/auth/login", json=account)
    assert r.status_code == 200
    body = r.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_domaine_interne_accepte(client):
    # Regression : EmailStr rejetait .local (TLD a usage reserve, RFC 6761),
    # ce qui verrouillait les comptes internes d'un SOC.
    creds = {"email": "analyste@test.local", "password": "MotDePasseSolide9"}
    assert client.post("/auth/register", json=creds).status_code == 200
    assert client.post("/auth/login", json=creds).status_code == 200


def test_adresse_normalisee(client):
    creds = {"email": "casse@soc.local", "password": "MotDePasseSolide9"}
    client.post("/auth/register", json=creds)
    r = client.post(
        "/auth/login",
        json={"email": "  CASSE@SOC.LOCAL  ", "password": creds["password"]},
    )
    assert r.status_code == 200


def test_adresse_mal_formee_refusee(client):
    for bad in ["pas-un-email", "a@b", "a b@c.tn", "@c.tn"]:
        r = client.post(
            "/auth/register", json={"email": bad, "password": "MotDePasseSolide9"}
        )
        assert r.status_code == 422, bad


def test_mot_de_passe_trop_court_refuse(client):
    r = client.post(
        "/auth/register", json={"email": "court@soc.local", "password": "abc"}
    )
    assert r.status_code == 422


def test_compte_inconnu_et_mauvais_mot_de_passe_indiscernables(client, account):
    # Ne pas permettre d'enumerer les comptes existants.
    inconnu = client.post(
        "/auth/login",
        json={"email": "personne@soc.local", "password": "MotDePasseSolide9"},
    )
    mauvais = client.post(
        "/auth/login", json={"email": account["email"], "password": "MauvaisMotDePasse1"}
    )
    assert inconnu.status_code == mauvais.status_code == 401
    assert inconnu.json()["detail"] == mauvais.json()["detail"]


def test_adresse_deja_utilisee(client, account):
    r = client.post("/auth/register", json=account)
    assert r.status_code == 400


def test_routes_de_module_protegees(client):
    for path in ["/phishing/submissions", "/ioc/history"]:
        assert client.get(path).status_code == 401, path
