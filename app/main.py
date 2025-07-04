from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import (coleta, indicadores, score, dashboards, tendencia, decisao_estrategica)  # ← NOVO IMPORT

app = FastAPI(
    title="BTC Turbo API",
    description="Sistema de análise de indicadores BTC",
    version="1.9.0"  # ← ATUALIZADO
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
app.include_router(coleta.router, prefix="/api/v1", tags=["📥 Coleta"]) 
app.include_router(indicadores.router, prefix="/api/v1", tags=["📊 Indicadores"])  
app.include_router(score.router, prefix="/api/v1", tags=["🎯 Scores"]) 
app.include_router(dashboards.router, prefix="/api/v1", tags=["📊 dashboards"]) 
app.include_router(tendencia.router, prefix="/api/v1", tags=["📊 tendencia"]) 
app.include_router(decisao_estrategica.router, prefix="/api/v1", tags=["🎯 Decisão Estratégica"])  # ← NOVO