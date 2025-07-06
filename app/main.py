from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import coleta
from app.routers import indicadores
from app.routers import score
from app.routers import dashboards
from app.routers import tendencia
from app.routers import decisao_estrategica
from app.routers import financeiro

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
app.include_router(financeiro.router, prefix="/api/v1/financeiro", tags=["📊 financeiro"]) 