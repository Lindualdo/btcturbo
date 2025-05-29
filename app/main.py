# app/main.py

from fastapi import FastAPI
from datetime import datetime
from app.routers import (
    coleta, indicadores, score, analise, diagnostico, 
    dashboards, dashboard_riscos, dashboard_momentum
)

app = FastAPI(
    title="BTC Turbo API",
    description="Sistema de análise de indicadores BTC com PostgreSQL + Dashboards HTML",
    version="1.0.6"
)

# ==========================================
# ROUTERS DE DADOS (APIs)
# ==========================================

app.include_router(diagnostico.router, prefix="/api/v1/diagnostico", tags=["🔧 Diagnóstico"]) 
app.include_router(coleta.router, prefix="/api/v1", tags=["📥 Coleta"]) 
app.include_router(indicadores.router, prefix="/api/v1", tags=["📊 Indicadores"]) 
app.include_router(score.router, prefix="/api/v1", tags=["🎯 Scores"])
app.include_router(analise.router, prefix="/api/v1", tags=["📈 Análise"])

# ==========================================
# ROUTERS DE DASHBOARDS (HTML)
# ==========================================

# Dashboard principal (índice)
app.include_router(dashboards.router, prefix="/dashboard", tags=["📱 Dashboards"])

# Dashboards específicos
app.include_router(dashboard_riscos.router, prefix="/dashboard", tags=["📱 Dashboards"])
app.include_router(dashboard_momentum.router, prefix="/dashboard", tags=["📱 Dashboards"])

# TODO: Adicionar quando prontos
# app.include_router(dashboard_ciclos.router, prefix="/dashboard", tags=["📱 Dashboards"])
# app.include_router(dashboard_tecnico.router, prefix="/dashboard", tags=["📱 Dashboards"])

# ==========================================
# ENDPOINTS BÁSICOS
# ==========================================

@app.get("/ping")
async def ping():
    """Keep-alive endpoint"""
    return {"status": "alive", "timestamp": datetime.utcnow().isoformat()}

@app.get("/health")
async def health():
    """Health check simples"""
    return {"healthy": True, "time": datetime.utcnow().isoformat()}

@app.get("/")
async def root():
    return {
        "message": "🚀 BTC Turbo API v1.0.6",
        "status": "✅ Online",
        "architecture": "Router por Bloco",
        "dashboards": {
            "index": "/dashboard/",
            "funcionando": [
                "/dashboard/riscos",
                "/dashboard/momentum"
            ],
            "desenvolvimento": [
                "/dashboard/ciclos", 
                "/dashboard/tecnico"
            ]
        },
        "apis": "/docs"
    }