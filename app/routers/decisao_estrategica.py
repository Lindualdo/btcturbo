# app/routers/decisao_estrategica.py

from fastapi import APIRouter, Query
from app.services.decisao_estrategica.estrategia_service import (
    processar_decisao_estrategica, 
    debug_matriz_estrategica,
    obter_decisao_estrategica,
    obter_detalhe_estrategia
)
from app.services.decisao_estrategica.utils.data_helper import get_historico_decisoes

router = APIRouter()

@router.post("/decisao-estrategica")
async def post_decisao_estrategica():
    """
    Processa nova decisão estratégica:
    - Busca scores (tendência + ciclo) + dados completos
    - Consulta matriz estratégica
    - Aplica decisão
    - Grava histórico + JSONs auditoria
    
    Returns:
        Decisão estratégica aplicada
    """
    return processar_decisao_estrategica()

@router.get("/decisao-estrategica")
async def get_decisao_estrategica():
    """
    Obtém última decisão estratégica do histórico
    (sem dados detalhados dos indicadores)
    
    Returns:
        Última decisão aplicada + JSONs auditoria
    """
    return obter_decisao_estrategica()

@router.get("/decisao-estrategica-detalhe")
async def get_decisao_estrategica_detalhe():
    """
    Obtém última decisão estratégica do histórico
    (sem dados detalhados dos indicadores)
    
    Returns:
        Última decisão aplicada + JSONs auditoria
    """
    return obter_detalhe_estrategia()

@router.get("/decisao-estrategica/historico")
async def get_historico_decisoes_endpoint(limit: int = Query(default=10, description="Número de registros")):
    """
    Busca histórico de decisões estratégicas
    (inclui dados completos de auditoria)
    
    Returns:
        Histórico completo com JSONs de auditoria
    """
    try:
        historico = get_historico_decisoes(limit)
        
        return {
            "status": "success",
            "total_registros": len(historico),
            "limit": limit,
            "historico": historico
        }
    except Exception as e:
        return {
            "status": "error",
            "erro": str(e),
            "historico": []
        }

@router.get("/decisao-estrategica/debug")
async def get_debug_matriz():
    """
    Debug da matriz estratégica:
    - Valida completude (15 cenários)
    - Mostra distribuição por tendência
    - Status geral da matriz
    
    Returns:
        Status e validação da matriz
    """
    return debug_matriz_estrategica()