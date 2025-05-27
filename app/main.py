# app/main.py

from fastapi import FastAPI
from app.routers import coleta, indicadores,score

app = FastAPI(
    title="BTC Turbo API",
    description="Sistema de análise de indicadores BTC",
    version="1.0.1"
)

app.include_router(coleta.router, prefix="/api/v1", tags=["API v1"])
app.include_router(indicadores.router, prefix="/api/v1", tags=["API v1"])
app.include_router(score.router, prefix="/api/v1", tags=["API v1"])