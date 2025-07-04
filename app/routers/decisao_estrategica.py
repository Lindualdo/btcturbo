# app/routers/decisao_estrategica.py

from fastapi import APIRouter
from app.services.estrategia.estrategia_service import (
    processar_decisao_estrategica,
    obter_ultima_estrategia, 
    debug_matriz_estrategica
)

router = APIRouter()

@router.post("/decisao-estrategica")
async def post_decisao_estrategica():
    """
    Processa nova decisão estratégica:
    - Busca scores (tendência + ciclo)
    - Consulta matriz estratégica
    - Aplica decisão
    - Grava histórico
    
    Returns:
        Decisão estratégica aplicada
    """
    return processar_decisao_estrategica()

@router.get("/decisao-estrategica")
async def get_decisao_estrategica():
    """
    Obtém última decisão estratégica do histórico
    
    Returns:
        Última decisão aplicada
    """
    return obter_ultima_estrategia()

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