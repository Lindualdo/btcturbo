# app/main.py -  v5.0.0

from fastapi import FastAPI
from pathlib import Path
from datetime import datetime
from app.routers import (
    coleta, indicadores, score, analise, diagnostico, camada_risco
)

app = FastAPI(
    title="BTC Turbo API",
    description="Sistema de análise de indicadores BTC",
    version="5.0.0"
)

# ==========================================
# ROUTERS DE DADOS (APIs)
# ==========================================

app.include_router(diagnostico.router, prefix="/api/v1/diagnostico", tags=["🔧 Diagnóstico"]) 
app.include_router(coleta.router, prefix="/api/v1", tags=["📥 Coleta"]) 
app.include_router(indicadores.router, prefix="/api/v1", tags=["📊 Indicadores"]) 
app.include_router(score.router, prefix="/api/v1", tags=["🎯 Scores"])
app.include_router(analise.router, prefix="/api/v1", tags=["📈 Análise"])
app.include_router(camada_risco.router, prefix="/api/v1", tags=["📈 camada_risco"])


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
        "message": "🚀 BTC Turbo API v1.0.21",
        "status": "✅ Online",
        "architecture": "Jinja2 Templates + FastAPI",
        "dashboards": {
            "index": "/dashboard/",
            "funcionando": [
                "/dashboard/riscos",
                "/dashboard/momentum", 
                "/dashboard/ciclos",
                "/dashboard/tecnico"
            ],
            "notas": {
                "templates": "Sistema refatorado para Jinja2",
                "static_files": "CSS/JS integrados"
            }
        },
        "apis": "/docs"
    }

# ==========================================
# STARTUP EVENT (VERIFICAÇÕES)
# ==========================================

@app.on_event("startup")
async def startup_event():
    """Verificações no startup"""
    print("🚀 BTC Turbo v5.0.0 - Iniciando...")
    
    # Verificar estrutura de templates
    template_path = Path("app/templates")
    if template_path.exists():
        print(f"✅ Templates configurados: {template_path}")
        
        # Verificar arquivos críticos
        critical_files = [
            "base.html",
            "dashboard_principal.html"
        ]
        
        for file in critical_files:
            file_path = template_path / file
            if file_path.exists():
                print(f"✅ Template encontrado: {file}")
            else:
                print(f"❌ Template faltando: {file}")
    else:
        print(f"❌ ERRO: Diretório templates não encontrado")
    
    print("🎯 Sistema iniciado - Dashboard disponível em /dashboard/")