"""Fixtures partagees.

Les tests s'executent contre une base PostgreSQL dediee (jamais la base de
developpement) : le schema utilise des colonnes JSONB, que SQLite ne sait pas
reproduire. La base de test est creee automatiquement si elle n'existe pas.
"""

import os
import uuid

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Base de test derivee de DATABASE_URL, ou surchargee par TEST_DATABASE_URL.
DEFAULT_TEST_URL = settings.database_url.rsplit("/", 1)[0] + "/baitway_test"
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", DEFAULT_TEST_URL)


def _ensure_database_exists(url):
    """Cree la base de test si besoin, en se connectant a la base 'postgres'."""
    base, name = url.rsplit("/", 1)
    admin = create_engine(base + "/postgres", isolation_level="AUTOCOMMIT")
    with admin.connect() as conn:
        exists = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :n"), {"n": name}
        ).scalar()
        if not exists:
            conn.execute(text(f'CREATE DATABASE "{name}"'))
    admin.dispose()


@pytest.fixture(scope="session", autouse=True)
def _database():
    """Prepare le schema une fois pour toute la session de test."""
    _ensure_database_exists(TEST_DATABASE_URL)

    engine = create_engine(TEST_DATABASE_URL)

    # Les modeles doivent etre importes pour etre enregistres sur Base.metadata.
    from app.core.database import Base
    from app.models import user, phishing, ioc  # noqa: F401

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()


@pytest.fixture()
def client(_database):
    """Client HTTP de test, branche sur la base de test."""
    from fastapi.testclient import TestClient

    from app.core.database import get_db
    from app.main import app

    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=_database)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def account(client):
    """Compte analyste unique, cree via l'API publique."""
    creds = {
        "email": f"test-{uuid.uuid4().hex[:8]}@soc.local",
        "password": "MotDePasseSolide9",
    }
    r = client.post("/auth/register", json=creds)
    assert r.status_code == 200, r.text
    return creds


@pytest.fixture()
def auth(client, account):
    """En-tete Authorization pret a l'emploi."""
    r = client.post("/auth/login", json=account)
    assert r.status_code == 200, r.text
    return {"Authorization": "Bearer " + r.json()["access_token"]}
