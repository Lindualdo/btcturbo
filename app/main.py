# app/main.py - v5.0.1 com Camada Mercado

from fastapi import FastAPI
from pathlib import Path
from datetime import datetime
from app.routers import alertas_debug ,alertas # ← ADICIONAR
from app.routers import (
    analise_mercado, analise_risco, coleta, indicadores, score, analise, diagnostico, analise_alavancagem,anallise_tatica
)

app = FastAPI(
    title="BTC Turbo API",
    description="Sistema de análise de indicadores BTC",
    version="5.0.1"
)

# ==========================================
# ROUTERS DE DADOS (APIs)
# ==========================================

app.include_router(diagnostico.router, prefix="/api/v1/diagnostico", tags=["🔧 Diagnóstico"]) 
app.include_router(coleta.router, prefix="/api/v1", tags=["📥 Coleta"]) 
app.include_router(indicadores.router, prefix="/api/v1", tags=["📊 Indicadores"]) 
app.include_router(score.router, prefix="/api/v1", tags=["🎯 Scores"])
app.include_router(analise.router, prefix="/api/v1", tags=["📈 Análise"]) #será descontinuada - foi substituida por analises em camadas

# ==========================================
# ROUTERS CAMADAS DE ANÁLISE (APIs)
# ==========================================
app.include_router(analise_mercado.router, prefix="/api/v1", tags=["🎯 Analise Mercado"])  # NOVO
app.include_router(analise_risco.router, prefix="/api/v1", tags=["🛡️ Analise Risco"])
app.include_router(analise_alavancagem.router, prefix="/api/v1", tags=["🎯 Analise Alavancagem"])  # NOVO
app.include_router(anallise_tatica.router, prefix="/api/v1", tags=["🎯 Analise Tatica"])  # NOVO


# ==========================================
# ROUTERS ALERTAS (APIs)
# ==========================================
app.include_router(alertas.router, prefix="/api/v1", tags=["alertas"])  # ← ADICIONAR



# ==========================================
# ROUTERS ALERTAS - DEBUG (APIs)
# ==========================================
app.include_router(alertas_debug.router, prefix="/alertas-debug", tags=["alertas_debug"])  # ← ADICIONAR


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