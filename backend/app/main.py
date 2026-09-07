from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import auth, phishing, ioc

app = FastAPI(title="BaitWay API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(phishing.router)
app.include_router(ioc.router)


@app.get("/health")
def health_check():
    return {"status": "ok", "app": "BaitWay"}
