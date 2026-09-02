from dotenv import load_dotenv
from fastapi import FastAPI
from sqlalchemy import func, select
from sqlalchemy.orm import Session

load_dotenv()

from app.db import engine
from app.models import Visit

app = FastAPI(
    title="Samwoo AX Citizen Portal",
    version="0.1.0",
    # Nginx and Vite preserve /api in forwarded requests. root_path removes the
    # prefix for route matching and keeps it in redirects and generated docs.
    root_path="/api",
)


@app.get("/health")
def health():
    with engine.connect() as connection:
        connection.exec_driver_sql("SELECT 1")
    # This endpoint is public and is polled by Coolify. Verify the dependency,
    # but do not disclose infrastructure details in the response.
    return {"status": "ok"}


@app.get("/overview")
def overview():
    with Session(engine) as session:
        visits = session.scalar(select(func.count()).select_from(Visit)) or 0
    return {
        "database": "연결됨",
        "visits": visits,
    }
