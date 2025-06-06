# app/services/analises/analise_tatica_completa.py - REFATORADO

from datetime import datetime
import logging
from app.services.analises.tatica.coleta_dados import coletar_dados_todas_camadas
from app.services.analises.tatica.logica_cenarios import processar_decisao_tatica
from app.services.analises.tatica.resposta_final import montar_resposta_final

logger = logging.getLogger(__name__)

def calcular_analise_tatica_completa():
    """
    FUNÇÃO PRINCIPAL: Análise Tática Completa com 8 Cenários
    
    Integra todas as 4 camadas:
    1. Análise de Mercado
    2. Análise de Risco  
    3. Análise de Alavancagem
    4. Matriz Completa de Cenários
    
    REFATORADO: Dividido em 3 módulos menores para facilitar manutenção
    """
    try:
        logger.info("🎯 Iniciando análise tática COMPLETA (8 cenários)...")
        
        # 1. Coletar dados de todas as camadas
        dados_coletados = coletar_dados_todas_camadas()
        
        # 2. Processar decisão tática (cenários + matriz básica)
        decisao_processada = processar_decisao_tatica(dados_coletados)
        
        # 3. Montar resposta final
        resposta_final = montar_resposta_final(dados_coletados, decisao_processada)
        
        logger.info(f"✅ Análise tática concluída: {decisao_processada['acao_padrao']} {decisao_processada['tamanho_final']}%")
        return resposta_final
        
    except Exception as e:
        logger.error(f"❌ Erro na análise tática completa: {str(e)}")
        return {
            "analise": "tatica_completa",
            "timestamp": datetime.utcnow().isoformat(),
            "acao_recomendada": "Sistema com falha crítica - não operar",
            "status": "error",
            "erro": str(e)
        }