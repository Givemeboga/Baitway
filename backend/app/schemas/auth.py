from pydantic import BaseModel, Field, field_validator

# Les identifiants transitent dans le corps de la requete, jamais en parametres
# d'URL : une URL se retrouve dans les journaux du serveur, l'historique du
# navigateur et les proxies intermediaires.

# bcrypt ne prend en compte que les 72 premiers octets d'un mot de passe.
PASSWORD_MIN = 8
PASSWORD_MAX = 72

# Verification de forme volontairement permissive : un SOC travaille sur des
# domaines internes (test.local, soc.internal, esprim.tn...). Une validation
# stricte facon email-validator rejette les TLD a usage reserve (RFC 6761) et
# interdirait des adresses parfaitement legitimes en interne.
EMAIL_SHAPE = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


class RegisterRequest(BaseModel):
    email: str = Field(min_length=3, max_length=254, pattern=EMAIL_SHAPE)
    password: str = Field(min_length=PASSWORD_MIN, max_length=PASSWORD_MAX)

    @field_validator("email")
    @classmethod
    def normalise(cls, v):
        return v.strip().lower()


class LoginRequest(BaseModel):
    # Aucune validation de forme ici : la connexion doit pouvoir retrouver un
    # compte deja cree, quelle que soit l'adresse enregistree. Verifier le
    # format a la connexion revient a verrouiller des comptes existants.
    email: str = Field(min_length=1, max_length=254)
    password: str = Field(min_length=1, max_length=PASSWORD_MAX)

    @field_validator("email")
    @classmethod
    def normalise(cls, v):
        return v.strip().lower()


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
