# app/main.py

from fastapi import FastAPI
from app.routers import analise_btc, analise_ciclo,  test_endpoint_notion

app = FastAPI(
    title="BTC Turbo API",
    description="Sistema de análise de indicadores BTC",
    version="1.0.0"
)

# Rotas principais
app.include_router(analise_ciclo.router, prefix="/analise-ciclo")
app.include_router(analise_btc.router, prefix="/analise-btc")

# Rota de teste (temporária)
app.include_router(test_endpoint_notion.router, prefix="/debug")