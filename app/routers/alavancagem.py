# Adicionar no arquivo app/routers/dashboards.py

from app.services.alavancagem.alavancagem_service import calcular_alavancagem, get_status_alavancagem

from fastapi import APIRouter

router = APIRouter()

# === NOVO ENDPOINT ALAVANCAGEM ===

@router.get("/alavancagem")
async def get_alavancagem():
    """
    Nova API de Alavancagem - Independente do dash-main
    
    Busca alavancagem permitida da tabela decisao_estrategica (último registro)
    Aplica as mesmas regras do dash-main para cálculo financeiro
    
    Returns:
        {
            "alavancagem": {
                "atual": 1.27,
                "status": "pode_aumentar",
                "permitida": 1.5,
                "divida_total": 17028.662893,
                "valor_a_reduzir": 0,
                "valor_disponivel": 14900.91377150001
            }
        }
    """
    return calcular_alavancagem()

@router.get("/alavancagem/status")
async def get_alavancagem_status():
    """
    Status resumido da alavancagem (versão simplificada)
    
    Returns:
        Status simplificado com indicadores básicos
    """
    return get_status_alavancagem()