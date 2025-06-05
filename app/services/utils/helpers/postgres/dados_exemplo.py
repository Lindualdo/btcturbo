# app/services/utils/helpers/postgres/dados_exemplo.py

import logging
from datetime import datetime, timedelta
from .base import execute_query

logger = logging.getLogger(__name__)

def insert_dados_exemplo_realistas():
    """
    Insere dados de exemplo mais realistas baseados na documentação
    Múltiplos registros para simular histórico
    """
    try:
        logger.info("🧪 Inserindo dados de exemplo realistas...")
        
        # Dados Ciclo - Baseados na tabela da spec (MVRV Z-Score 0-6, Realized 0.7-2.5, Puell 0.5-4.0)
        dados_ciclo = [
            # Cenário Atual (Neutro)
            (2.1, 1.3, 1.2, 'Spec_Atual'),
            # Cenário Bull (Bom)  
            (1.5, 0.9, 0.8, 'Spec_Bull'),
            # Cenário Bear (Crítico)
            (5.2, 2.1, 3.5, 'Spec_Bear'),
            # Histórico adicional
            (2.8, 1.6, 1.5, 'Historico'),
            (1.9, 1.1, 0.9, 'Historico')
        ]
        
        for mvrv, realized, puell, fonte in dados_ciclo:
            query = """
                INSERT INTO indicadores_ciclo (mvrv_z_score, realized_ratio, puell_multiple, fonte, timestamp)
                VALUES (%s, %s, %s, %s, %s)
            """
            timestamp = datetime.utcnow() - timedelta(hours=len(dados_ciclo))
            params = (mvrv, realized, puell, fonte, timestamp)
            execute_query(query, params)
        
        # Dados Momentum - RSI 30-70, Funding -0.05 a 0.1%, OI -30% a +50%, L/S 0.8-1.3
        dados_momentum = [
            # Cenário Atual (Neutro)
            (52.0, 0.015, 12.0, 0.98, 'Spec_Atual'),
            # Cenário Oversold (Ótimo)
            (28.5, -0.02, -15.0, 0.85, 'Spec_Oversold'),
            # Cenário Overbought (Crítico)
            (72.5, 0.08, 45.0, 1.25, 'Spec_Overbought'),
            # Histórico
            (48.2, 0.008, 5.5, 1.05, 'Historico'),
            (55.8, 0.025, 18.2, 0.92, 'Historico')
        ]
        
        for rsi, funding, oi, ls_ratio, fonte in dados_momentum:
            query = """
                INSERT INTO indicadores_momentum (rsi_semanal, funding_rates, oi_change, long_short_ratio, fonte, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            timestamp = datetime.utcnow() - timedelta(hours=len(dados_momentum))
            params = (rsi, funding, oi, ls_ratio, fonte, timestamp)
            execute_query(query, params)
        
        # Dados Risco - Dist >50% ótimo, HF >2.0 ótimo, Netflow -50k/+50k, Stable 2%-15%
        dados_risco = [
            # Cenário Atual (Bom)
            (35.0, 1.7, -5000, 8.0, 'Spec_Atual'),
            # Cenário Seguro (Ótimo)
            (55.0, 2.2, -25000, 12.0, 'Spec_Seguro'),
            # Cenário Perigoso (Crítico)
            (8.0, 1.05, 30000, 3.0, 'Spec_Perigoso'),
            # Histórico
            (42.0, 1.9, -2000, 9.5, 'Historico'),
            (28.0, 1.4, 15000, 6.5, 'Historico')
        ]
        
        for dist, hf, netflow, stable, fonte in dados_risco:
            query = """
                INSERT INTO indicadores_risco (dist_liquidacao, health_factor, exchange_netflow, stablecoin_ratio, fonte, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            timestamp = datetime.utcnow() - timedelta(hours=len(dados_risco))
            params = (dist, hf, netflow, stable, fonte, timestamp)
            execute_query(query, params)
        
        # Dados Técnico - Scores 0-10 (8+ ótimo, 6-8 bom, 4-6 neutro, 2-4 ruim, 0-2 crítico)
        dados_tecnico = [
            # Cenário Atual (Bom)
            (7.5, 6.0, 'Spec_Atual'),
            # Cenário Bull Forte (Ótimo)
            (9.2, 8.5, 'Spec_Bull'),
            # Cenário Bear (Crítico)
            (1.8, 2.5, 'Spec_Bear'),
            # Histórico
            (6.5, 5.5, 'Historico'),
            (8.8, 7.0, 'Historico')
        ]
        
        for emas, padroes, fonte in dados_tecnico:
            query = """
                INSERT INTO indicadores_tecnico (sistema_emas, padroes_graficos, fonte, timestamp)
                VALUES (%s, %s, %s, %s)
            """
            timestamp = datetime.utcnow() - timedelta(hours=len(dados_tecnico))
            params = (emas, padroes, fonte, timestamp)
            execute_query(query, params)
        
        logger.info("✅ Dados de exemplo realistas inseridos com sucesso")
        logger.info(f"📊 Inseridos: {len(dados_ciclo)} ciclo, {len(dados_momentum)} momentum, {len(dados_risco)} risco, {len(dados_tecnico)} técnico")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao inserir dados realistas: {str(e)}")
        return False

def limpar_dados_exemplo():
    """Remove todos os dados de exemplo das tabelas"""
    try:
        logger.info("🧹 Limpando dados de exemplo...")
        
        queries = [
            "DELETE FROM indicadores_ciclo WHERE fonte LIKE 'Spec_%' OR fonte = 'Historico' OR fonte = 'Exemplo'",
            "DELETE FROM indicadores_momentum WHERE fonte LIKE 'Spec_%' OR fonte = 'Historico' OR fonte = 'Exemplo'",
            "DELETE FROM indicadores_risco WHERE fonte LIKE 'Spec_%' OR fonte = 'Historico' OR fonte = 'Exemplo'",
            "DELETE FROM indicadores_tecnico WHERE fonte LIKE 'Spec_%' OR fonte = 'Historico' OR fonte = 'Exemplo'"
        ]
        
        for query in queries:
            result = execute_query(query)
            logger.info(f"Limpeza executada: {result.get('affected_rows', 0)} registros removidos")
        
        logger.info("✅ Dados de exemplo limpos com sucesso")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao limpar dados: {str(e)}")
        return False