from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.v2 import dash_mercado as dash_mercado_v2 
from app.routers.v3 import (dash_main,analise_mercado as analise_mercado_v3, dash_mercado as dash_mercado_v3)
from app.routers import (coleta, indicadores, score, alertas_debug ,alertas)

app = FastAPI(
    title="BTC Turbo API",
    description="Sistema de análise de indicadores BTC",
    version="5.3.11"
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
app.include_router(dash_mercado_v2.router, prefix="/api/v2", tags=["📊 dash mercado "]) # dash mercado v2 - Usando apenas o post - reescrever na v3 e descontinuar
app.include_router(dash_mercado_v3.router, prefix="/api/v3", tags=["📊 dash mercado "]) # dash mercado v3 - usando apenas o GET - implementar o post e descontinuar v2
app.include_router(dash_main.router, prefix="/api/v3", tags=["📊 dash main "]) # dash main)
app.include_router(alertas_debug.router, prefix="/alertas-debug", tags=["alertas_debug"]) # retorna todos os alertas separados em categorias
app.include_router(alertas.router, prefix="/api/v1", tags=["alertas"])  # Busca os alertas por categorias ()
app.include_router(analise_mercado_v3.router, prefix="/api/v3", tags=["analise mercado"])  # Analise de mercado (ciclos, riscos, momentum e tecnico) - Camada 1