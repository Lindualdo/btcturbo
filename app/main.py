# app/main.py - v5.0.14 com Camada Mercado

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from datetime import datetime
from app.routers.v2 import dashboard_home as dashboard_home_v2 
from app.routers.v2 import dash_mercado as dash_mercado  
from app.routers.v3 import dash_mercado as dash_mercado_v3
from app.routers.v3 import dash_main as dash_main
from app.routers import alertas_debug ,alertas,dashboard_home
from app.routers import (
    analise_mercado, analise_risco, coleta, indicadores, score, analise, diagnostico, analise_alavancagem,anallise_tatica
)

app = FastAPI(
    title="BTC Turbo API",
    description="Sistema de análise de indicadores BTC",
    version="5.0.14"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ou específico: ["https://btcturbo-frontend.vercel.app"]
    allow_methods=["GET", "POST"],
    allow_headers=["*"]
)

# ==========================================
# (APIs) descontinuadas - Analisar se suas funções estão sendo usadas internamente
# ==========================================

app.include_router(diagnostico.router, prefix="/api/v1/diagnostico", tags=["🔧 Diagnóstico"]) 
app.include_router(indicadores.router, prefix="/api/v1", tags=["📊 Indicadores"]) 
app.include_router(analise.router, prefix="/api/v1", tags=["📈 Análise"]) #será descontinuada - foi substituida por analises em camadas
app.include_router(analise_mercado.router, prefix="/api/v1", tags=["🎯 Analise Mercado"])  # NOVO
app.include_router(analise_risco.router, prefix="/api/v1", tags=["🛡️ Analise Risco"])
app.include_router(analise_alavancagem.router, prefix="/api/v1", tags=["🎯 Analise Alavancagem"])  # NOVO
app.include_router(anallise_tatica.router, prefix="/api/v1", tags=["🎯 Analise Tatica"])  # NOVO
app.include_router(dashboard_home.router, prefix="/api/v1", tags=["DashBoard_Home"])  # substituida pela V2

# ==========================================
# APIs QUE ESTÃO SENDO USADOS
# ==========================================
app.include_router(coleta.router, prefix="/api/v1", tags=["📥 Coleta"]) # coleta indicadores (ciclos, riscos, momentum e tecnico)
app.include_router(indicadores.router, prefix="/api/v1", tags=["📊 Indicadores"])  # obtem os indicadores (ciclos, riscos, momentum e tecnico)
app.include_router(score.router, prefix="/api/v1", tags=["🎯 Scores"]) # calcula scores e retona indicadores  (ciclos, riscos, momentum e tecnico)
app.include_router(dashboard_home_v2.router, prefix="/api/v2", tags=["📊 Dashboard V2"]) # dash principal (post grava e get obtem)
app.include_router(dash_mercado.router, prefix="/api/v2", tags=["📊 dash mercado "]) # dash mercado - detalhe do mercado home (post grava e get obtem)
app.include_router(dash_mercado_v3.router, prefix="/api/v3", tags=["📊 dash mercado "]) # dash mercado - detalhe do mercado home (post grava e get obtem)
app.include_router(dash_main.router, prefix="/api/v3", tags=["📊 dash main "]) # dash main)
app.include_router(alertas_debug.router, prefix="/alertas-debug", tags=["alertas_debug"]) # retorna todos os alertas separados em categorias
app.include_router(alertas.router, prefix="/api/v1", tags=["alertas"])  # Busca os alertas por categorias ()

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
        "message": "🚀 BTC Turbo API v5.0.1",
        "status": "✅ Online",
        "architecture": "4 Camadas de Análise",
        "new_features": {
            "camada_mercado": "/api/v1/camada-mercado",
            "description": "Consolida Ciclo + Técnico + Momentum"
        },
        "apis": {
            "docs": "/docs",
            "camadas": {
                "mercado": "/api/v1/camada-mercado",
                "risco": "/api/v1/camada-risco"
            },
            "blocos": {
                "ciclos": "/api/v1/calcular-score/ciclos",
                "tecnico": "/api/v1/calcular-score/tecnico", 
                "momentum": "/api/v1/calcular-score/momentum"
            }
        }
    }

# ==========================================
# STARTUP EVENT (VERIFICAÇÕES)
# ==========================================

@app.on_event("startup")
async def startup_event():
    """Verificações no startup"""
    print("🚀 BTC Turbo v5.0.1 - Iniciando...")
    print("✅ Nova API: Camada Mercado implementada")
    print("🎯 Disponível em: /api/v1/camada-mercado")
    print("📊 Consolida: Ciclos (50%) + Técnico (30%) + Momentum (20%)")