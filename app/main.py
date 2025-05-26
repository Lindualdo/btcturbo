from fastapi import FastAPI
from app.routers import analise_btc, analise_ciclo

app = FastAPI()

# Rotas principais
app.include_router(analise_ciclo.router, prefix="/analise-ciclo")
app.include_router(analise_btc.router, prefix="/analise-btc")