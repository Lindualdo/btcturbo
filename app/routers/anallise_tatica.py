# app/routers/anallise_tatica.py - ATUALIZADO PARA VERSÃO COMPLETA

from fastapi import APIRouter
from app.services.analises.analise_tatica_completa import calcular_analise_tatica_completa

router = APIRouter()

@router.get("/analise-tatica")
async def analisar_tatica():
    """
    API da Camada 4: Análise Tática COMPLETA
    
    NOVA IMPLEMENTAÇÃO:
    - Integra todas as 4 camadas de análise
    - Aplica matriz de 8 cenários completos
    - Override inteligente por contexto
    - Score integrado final
    
    Cenários suportados:
    1. Bull Market Inicial
    2. Bull Market Maduro  
    3. Topo Formando
    4. Correção em Bull
    5. Início Bear Market
    6. Bear Market Profundo
    7. Risco Crítico (Override)
    8. Volatilidade Comprimida
    """
    return calcular_analise_tatica_completa()