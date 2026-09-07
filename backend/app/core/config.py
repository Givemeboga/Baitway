import secrets
import sys

from pydantic_settings import BaseSettings

# Valeurs presentes dans .env.example : publiques, donc jamais utilisables
# comme secret reel.
PLACEHOLDER_SECRETS = {
    "",
    "change_moi_avant_prod",
    "remplace_par_une_cle_secrete",
    "replace_with_a_secret_key",
}


class Settings(BaseSettings):
    # La base est exposee sur le port 5433 (voir docker-compose.yml).
    database_url: str = "postgresql://baitway_admin:baitway_password@localhost:5433/baitway"

    # Aucun secret par defaut : une application qui demarre avec une cle
    # publiee dans le depot laisse forger n'importe quel jeton.
    jwt_secret: str = ""
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    # Origines autorisees par le CORS, separees par des virgules.
    cors_origins: str = "http://localhost:5173"

    # Cles des sources de renseignement (Module B). Vide = source "unknown".
    virustotal_api_key: str = ""
    abusech_auth_key: str = ""
    abuseipdb_api_key: str = ""

    class Config:
        env_file = ".env"

    @property
    def cors_origin_list(self):
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()

if settings.jwt_secret.strip() in PLACEHOLDER_SECRETS:
    # En developpement, une cle ephemere vaut mieux qu'un secret connu de tous :
    # les sessions sont perdues a chaque redemarrage, ce qui se remarque
    # immediatement, sans jamais exposer de cle publiee.
    settings.jwt_secret = secrets.token_urlsafe(32)
    print(
        "ATTENTION : JWT_SECRET absent ou laisse a sa valeur d'exemple.\n"
        "            Une cle ephemere a ete generee : les sessions seront perdues\n"
        "            a chaque redemarrage. Renseignez JWT_SECRET dans backend/.env\n"
        "            avant tout deploiement :\n"
        '              python -c "import secrets; print(secrets.token_urlsafe(32))"',
        file=sys.stderr,
    )
