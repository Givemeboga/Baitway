from sqlalchemy import Column, Integer, String, Enum
import enum
from app.core.database import Base

class Role(str, enum.Enum):
    analyste = "analyste"
    admin = "admin"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(Role), default=Role.analyste, nullable=False)