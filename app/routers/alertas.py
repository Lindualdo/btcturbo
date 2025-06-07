# app/routers/alertas.py

from fastapi import APIRouter
from typing import List, Optional
from datetime import datetime, timedelta

from app.services.alertas.engine import AlertasEngine
from app.services.alertas.models import AlertaResponse, AlertaConfig, AlertaResumo

router = APIRouter()
alertas_engine = AlertasEngine()

@router.get("/alertas/verificar", summary="Verifica todos os alertas")
async def verificar_alertas():
    """
    Executa verificação completa de todos os tipos de alertas
    Usado pelo sistema automaticamente
    """
    return alertas_engine.verificar_todos_alertas()

@router.get("/alertas/ativos", response_model=List[AlertaResponse])
async def get_alertas_ativos(
    categoria: Optional[str] = Query(None, description="critico, urgente, informativo"),
    tipo: Optional[str] = Query(None, description="posicao, mercado, volatilidade, tatico, onchain"),
    limit: int = Query(20, le=100)
):
    """
    Retorna alertas ativos para dashboard
    """
    return alertas_engine.get_alertas_ativos(categoria=categoria, tipo=tipo, limit=limit)

@router.get("/alertas/resumo", response_model=AlertaResumo)
async def get_resumo_alertas():
    """
    Widget principal do dashboard - contadores por categoria
    """
    return alertas_engine.get_resumo_alertas()

@router.get("/alertas/historico", response_model=List[AlertaResponse])
async def get_historico_alertas(
    dias: int = Query(7, le=30, description="Últimos N dias"),
    incluir_resolvidos: bool = Query(True),
    tipo: Optional[str] = Query(None)
):
    """
    Timeline histórico de alertas
    """
    data_inicio = datetime.utcnow() - timedelta(days=dias)
    return alertas_engine.get_historico_alertas(
        data_inicio=data_inicio,
        incluir_resolvidos=incluir_resolvidos,
        tipo=tipo
    )

@router.post("/alertas/{alerta_id}/resolver")
async def resolver_alerta(alerta_id: int):
    """
    Marca alerta como resolvido
    """
    success = alertas_engine.resolver_alerta(alerta_id)
    if not success:
        raise HTTPException(status_code=404, detail="Alerta não encontrado")
    return {"status": "resolvido", "alerta_id": alerta_id}

@router.post("/alertas/{alerta_id}/snooze")
async def snooze_alerta(alerta_id: int, minutos: int = Query(60, le=1440)):
    """
    Silencia alerta por X minutos
    """
    success = alertas_engine.snooze_alerta(alerta_id, minutos)
    if not success:
        raise HTTPException(status_code=404, detail="Alerta não encontrado")
    return {"status": "snoozed", "alerta_id": alerta_id, "ate": datetime.utcnow() + timedelta(minutes=minutos)}

@router.get("/alertas/config", response_model=List[AlertaConfig])
async def get_config_alertas():
    """
    Configurações atuais de alertas
    """
    return alertas_engine.get_config_alertas()

@router.put("/alertas/config")
async def update_config_alertas(configs: List[AlertaConfig]):
    """
    Atualiza configurações de alertas
    """
    return alertas_engine.update_config_alertas(configs)

@router.get("/alertas/health")
async def health_check_alertas():
    """
    Health check do sistema de alertas
    """
    return {
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "ultima_verificacao": alertas_engine.get_ultima_verificacao(),
        "alertas_ativos": alertas_engine.count_alertas_ativos(),
        "tipos_funcionando": alertas_engine.check_detectores_status()
    }