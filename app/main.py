# app/main.py

from fastapi import FastAPI
from app.routers import analise_btc, analise_ciclo, test_endpoint_notion, obter_indicadores

app = FastAPI(
    title="BTC Turbo API",
    description="Sistema de análise de indicadores BTC",
    version="1.0.0"
)

# APIs principais - Versão 1
app.include_router(analise_ciclo.router, prefix="/api/v1", tags=["API v1"])
app.include_router(analise_btc.router, prefix="/api/v1", tags=["API v1"])
app.include_router(obter_indicadores.router, prefix="/api/v1", tags=["API v1"])

# Debug endpoints (sem versão)
app.include_router(test_endpoint_notion.router, prefix="/debug", tags=["Debug"])