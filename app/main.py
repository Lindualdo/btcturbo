from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.v3 import (dash_main as dash_main_v3,analise_mercado as analise_mercado_v3, dash_mercado as dash_mercado_v3)
from app.routers import (coleta, indicadores, score)

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
app.include_router(dash_mercado_v3.router, prefix="/api/v3", tags=["📊 dash mercado "]) # (POST e GET) Post carrega indicadores e scores de mercado e Get obtem
app.include_router(dash_main_v3.router, prefix="/api/v3", tags=["📊 dash main "]) # (POST e GET) Post carrgeda dados gerais do Dash 4 camadas de analise e get obtem

#analisar se tem mesmo a necessidade de expor esse endpoint
app.include_router(analise_mercado_v3.router, prefix="/api/v3", tags=["analise mercado"]) # GET - Obtem Analise de mercado (ciclos, riscos, momentum e tecnico) - Camada 1