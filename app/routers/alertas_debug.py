# app/routers/debug_alertas.py

from fastapi import APIRouter
from app.services.alertas.debug_service import AlertasDebugService

router = APIRouter()
debug_service = AlertasDebugService()

@router.get("/criticos")
async def debug_alertas_criticos():
    """
    Debug completo categoria CRÍTICOS
    Mesma estrutura produção = fidelidade teste
    """
    return debug_service.debug_criticos()

@router.get("/debug/alertas/geral")
async def debug_alertas_geral():
    """
    Overview todas categorias (implementar após críticos)
    """
    return {
        "message": "Implementar após completar críticos",
        "categorias_disponiveis": ["criticos"],
        "proximas": ["urgentes", "mercado", "volatilidade", "tatico", "onchain"]
    }