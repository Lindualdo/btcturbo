# app/main.py

from fastapi import FastAPI
from app.routers import coleta, indicadores, score, analise, diagnostico

app = FastAPI(
    title="BTC Turbo API",
    description="Sistema de análise de indicadores BTC com PostgreSQL",
    version="1.0.4"
)

# 0 - DIAGNÓSTICO E SETUP (NOVO)
app.include_router(diagnostico.router, prefix="/api/v1/diagnostico", tags=["🔧 Diagnóstico"]) 

# 1 - Coleta indicadores (origens diversas) e grava no postgres
app.include_router(coleta.router, prefix="/api/v1", tags=["📥 Coleta"]) 

# 2 - Obter os indicadores (dados brutos) do postgres
app.include_router(indicadores.router, prefix="/api/v1", tags=["📊 Indicadores"]) 

# 3 - Calcular score dos indicadores de cada bloco (usa sempre os dados brutos do postgres)
app.include_router(score.router, prefix="/api/v1", tags=["🎯 Scores"])

# 4 - Score consolidado (usa os scores consolidados de cada bloco) 
app.include_router(analise.router, prefix="/api/v1", tags=["📈 Análise"])

@app.get("/")
async def root():
    return {
        "message": "🚀 BTC Turbo API v1.0.4",
        "status": "✅ Online",
        "endpoints": {
            "diagnostico": "/api/v1/diagnostico/health-check",
            "setup": "/api/v1/diagnostico/setup-database",
            "teste": "/api/v1/diagnostico/test-indicadores",
            "indicadores": "/api/v1/obter-indicadores/{bloco}",
            "docs": "/docs"
        }
    }