from fastapi import FastAPI
from app.api import router
from app.database import Base, engine
import app.models

Base.metadata.create_all(bind=engine)
app = FastAPI(title="SubLedger", version="1.0.0")
app.include_router(router)

@app.get('/health')
def health():
    return {"status": "ok"}
