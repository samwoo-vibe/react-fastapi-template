import os

from dotenv import load_dotenv
from fastapi import FastAPI
from sqlalchemy import func, select
from sqlalchemy.orm import Session

load_dotenv()

from app.db import engine
from app.models import Visit


app = FastAPI(title="Samwoo AX Citizen Portal", version="0.1.0")


@app.get("/health")
def health():
    with engine.connect() as connection:
        connection.exec_driver_sql("SELECT 1")
    return {"status": "ok", "database": "connected"}


@app.get("/overview")
def overview():
    with Session(engine) as session:
        session.add(Visit())
        session.commit()
        visits = session.scalar(select(func.count()).select_from(Visit))
    return {
        "environment": os.getenv("APP_ENV", "unknown"),
        "database": "연결됨",
        "visits": visits,
        "services": 12,
        "deployments_this_week": 28,
    }
