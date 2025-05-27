# app/main.py

from fastapi import FastAPI
from app.routers import coleta, indicadores,score,analise

app = FastAPI(
    title="BTC Turbo API",
    description="Sistema de análise de indicadores BTC",
    version="1.0.1"
)

# 1 - coleta indicadores (origens diversas) e grava no postgres
app.include_router(coleta.router, prefix="/api/v1", tags=["API v1"]) 

#2 - obter os indicadore (dados brutos) no postgres
app.include_router(indicadores.router, prefix="/api/v1", tags=["API v1"]) 

#3 - calcular score dos indicadores de cada bloco (usa sempre os dados brutos do postgres)
app.include_router(score.router, prefix="/api/v1", tags=["API v1"])

#4 - score consolidado (usa os scores consolidados de cada bloco) 
app.include_router(analise.router, prefix="/api/v1", tags=["API v1"]) 