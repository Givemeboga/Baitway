from pydantic import BaseModel, EmailStr, Field

# Les identifiants transitent dans le corps de la requete, jamais en parametres
# d'URL : une URL se retrouve dans les journaux du serveur, l'historique du
# navigateur et les proxies intermediaires.

# bcrypt ne prend en compte que les 72 premiers octets d'un mot de passe.
PASSWORD_MIN = 8
PASSWORD_MAX = 72


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=PASSWORD_MIN, max_length=PASSWORD_MAX)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=PASSWORD_MAX)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
