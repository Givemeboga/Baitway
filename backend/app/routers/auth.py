from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    """Cree un compte analyste.

    Les identifiants sont lus dans le corps de la requete : en parametres
    d'URL, le mot de passe se retrouverait dans les journaux d'acces.
    """
    email = payload.email
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(400, "Email already registered")

    user = User(email=email, hashed_password=hash_password(payload.password))
    db.add(user)
    db.commit()
    return {"message": "Account created"}


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """Authentifie un analyste et renvoie un jeton JWT."""
    user = db.query(User).filter(User.email == payload.email).first()
    # Meme message et meme code quel que soit le motif : ne pas indiquer si
    # l'adresse existe.
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(401, "Invalid credentials")

    token = create_access_token({"sub": user.email, "role": user.role.value})
    return TokenResponse(access_token=token)
