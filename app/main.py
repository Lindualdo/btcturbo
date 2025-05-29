from fastapi import FastAPI
from datetime import datetime
from app.routers import coleta, indicadores, score, analise, diagnostico, dashboards

app = FastAPI(
    title="BTC Turbo API",
    description="Sistema de análise de indicadores BTC com PostgreSQL + HTML Templates",
    version="1.0.5"
)

# ==========================================
# ROUTERS ORGANIZADOS
# ==========================================

# APIs de dados
app.include_router(diagnostico.router, prefix="/api/v1/diagnostico", tags=["🔧 Diagnóstico"]) 
app.include_router(coleta.router, prefix="/api/v1", tags=["📥 Coleta"]) 
app.include_router(indicadores.router, prefix="/api/v1", tags=["📊 Indicadores"]) 
app.include_router(score.router, prefix="/api/v1", tags=["🎯 Scores"])
app.include_router(analise.router, prefix="/api/v1", tags=["📈 Análise"])

# Dashboards HTML
app.include_router(dashboards.router, prefix="/dashboard", tags=["📱 Dashboards"])

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
        "message": "🚀 BTC Turbo API v1.0.5",
        "status": "✅ Online",
        "endpoints": {
            "apis": "/docs",
            "dashboards": {
                "tecnico": "/dashboard/tecnico",
                "ciclos": "/dashboard/ciclos", 
                "momentum": "/dashboard/momentum",
                "riscos": "/dashboard/riscos",
                "consolidado": "/dashboard/consolidado"
            }
        }
    }