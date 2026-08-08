from fastapi import FastAPI

app = FastAPI(title="BaitWay API")

@app.get("/health")
def health_check():
    return {"status": "ok", "app": "BaitWay"}