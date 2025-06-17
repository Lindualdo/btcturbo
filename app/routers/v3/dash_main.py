# routers/v3/dash_home.py
from fastapi import APIRouter
from app.services.v3.dash_main.dash_home_service import processar_dashboard, obter_dashboard, debug_dashboard 

router = APIRouter()

@router.post("/dashboard-home")
async def post_dashboard():
    """POST - Calcula novo dashboard V3"""
    return processar_dashboard()

@router.get("/dashboard-home")
async def get_dashboard():
    """GET - Retorna último dashboard V3"""
    return obter_dashboard()

@router.get("/dashboard-home/debug")
async def debug_dashboard_endpoint():
    """DEBUG - Info sistema V3"""
    return debug_dashboard()

# Adicionar ao router dash_main.py
@router.get("/dashboard/debug/mercado")
async def debug_analise_mercado():
    """
    Debug específico da Camada 1 - Análise de Mercado
    Retorna dados brutos + ciclo identificado + estratégia
    """
    try:
        from app.services.v3.dash_main.utils.analise.mercado.analise_mercado import executar_analise_mercado
        
        resultado = executar_analise_mercado()
        
        return {
            "status": "success",
            "camada": "1-mercado",
            "dados": resultado
        }
        
    except Exception as e:
        logger.error(f"❌ Erro debug mercado: {str(e)}")
        return {
            "status": "error",
            "camada": "1-mercado", 
            "erro": str(e)
        }