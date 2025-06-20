from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import (coleta, indicadores, score, dashboards)

app = FastAPI(
    title="BTC Turbo API",
    description="Sistema de análise de indicadores BTC",
    version="5.3.16"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ou específico: ["https://btcturbo-frontend.vercel.app"]
    allow_methods=["GET", "POST"],
    allow_headers=["*"]
)

# ==========================================
# APIs QUE ESTÃO SENDO USADOS
# ==========================================
app.include_router(coleta.router, prefix="/api/v1", tags=["📥 Coleta"]) # coleta indicadores (ciclos, riscos, momentum e tecnico)
app.include_router(indicadores.router, prefix="/api/v1", tags=["📊 Indicadores"])  # obtem os indicadores (ciclos, riscos, momentum e tecnico)
app.include_router(score.router, prefix="/api/v1", tags=["🎯 Scores"]) # calcula scores e retona indicadores  (ciclos, riscos, momentum e tecnico)
app.include_router(dashboards.router, prefix="/api/v1/", tags=["📊 dashboards"]) 
