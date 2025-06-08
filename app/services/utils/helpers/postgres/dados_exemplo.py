# app/services/utils/helpers/postgres/dados_exemplo.py - v5.1.2 COM NUPL

import logging
from datetime import datetime, timedelta
from .base import execute_query

logger = logging.getLogger(__name__)

def insert_dados_exemplo_realistas():
    """
    Insere dados de exemplo mais realistas baseados na documentação
    v5.1.2: INCLUINDO VALORES NUPL REALISTAS
    """
    try:
        logger.info("🧪 Inserindo dados de exemplo v5.1.2 com NUPL...")
        
        # ==========================================
        # DADOS CICLO v5.1.2 - COM NUPL
        # ==========================================
        
        # Cenários realistas baseados em fases de mercado históricas
        # NUPL: >0.75=euforia, 0.5-0.75=sobrecomprado, 0.25-0.5=neutro, 0-0.25=acumulação, <0=oversold
        
        dados_ciclo_v512 = [
            # Cenário Bear Profundo (Acumulação)
            {
                "mvrv": 0.8,      # Bear territory
                "realized": 0.75,  # Abaixo de 1.0
                "puell": 0.6,     # Miners em stress
                "nupl": 0.15,     # ← NOVO: Acumulação (0-0.25)
                "fonte": "Spec_Bear_Profundo"
            },
            
            # Cenário Bull Inicial (Saindo da acumulação)
            {
                "mvrv": 1.8,      # Começando bull
                "realized": 1.1,  # Acima breakeven
                "puell": 1.0,     # Miners normalizando
                "nupl": 0.35,     # ← NOVO: Neutro baixo (0.25-0.5)
                "fonte": "Spec_Bull_Inicial"
            },
            
            # Cenário Bull Maduro (Tendência estabelecida)
            {
                "mvrv": 2.5,      # Bull confirmado
                "realized": 1.4,  # Lucros se materializando
                "puell": 1.3,     # Miners em lucro
                "nupl": 0.62,     # ← NOVO: Neutro alto (0.5-0.75)
                "fonte": "Spec_Bull_Maduro"
            },
            
            # Cenário Topo Formando (Euforia Inicial)
            {
                "mvrv": 3.8,      # Territory perigoso
                "realized": 1.9,  # Muito acima de 1.0
                "puell": 2.2,     # Miners em festa
                "nupl": 0.78,     # ← NOVO: Euforia inicial (>0.75)
                "fonte": "Spec_Topo_Formando"
            },
            
            # Cenário Topo Extremo (Máxima Euforia)
            {
                "mvrv": 5.1,      # Território histórico
                "realized": 2.3,  # Extremo
                "puell": 3.2,     # Miners eufóricos
                "nupl": 0.89,     # ← NOVO: Euforia extrema (perto de 0.9+)
                "fonte": "Spec_Topo_Extremo"
            },
            
            # Cenário Atual (Realista para contexto atual)
            {
                "mvrv": 2.1,      # Moderado
                "realized": 1.3,  # Neutro
                "puell": 1.2,     # OK
                "nupl": 0.42,     # ← NOVO: Neutro (0.25-0.5)
                "fonte": "Spec_Atual"
            }
        ]
        
        # Inserir dados ciclo v5.1.2
        for i, dados in enumerate(dados_ciclo_v512):
            query = """
                INSERT INTO indicadores_ciclo 
                (mvrv_z_score, realized_ratio, puell_multiple, nupl, fonte, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            timestamp = datetime.utcnow() - timedelta(hours=len(dados_ciclo_v512) - i)
            params = (
                dados["mvrv"],
                dados["realized"], 
                dados["puell"],
                dados["nupl"],  # ← NOVO: Incluindo NUPL
                dados["fonte"], 
                timestamp
            )
            execute_query(query, params)
            
            logger.info(f"✅ Inserido cenário: {dados['fonte']} - NUPL: {dados['nupl']}")
        
        # ==========================================
        # DADOS OUTROS BLOCOS (sem alteração v5.1.2)
        # ==========================================
        
        # Dados Momentum - Inalterados
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
        
        # Dados Risco - Inalterados
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
        
        # Dados Técnico - Inalterados
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
        
        logger.info("✅ Dados de exemplo v5.1.2 inseridos com sucesso")
        logger.info(f"📊 Inseridos: {len(dados_ciclo_v512)} ciclo (COM NUPL), {len(dados_momentum)} momentum, {len(dados_risco)} risco, {len(dados_tecnico)} técnico")
        
        # ==========================================
        # VALIDAÇÃO NUPL v5.1.2
        # ==========================================
        
        # Verificar dados NUPL inseridos
        query_validacao = """
            SELECT fonte, nupl, mvrv_z_score, timestamp
            FROM indicadores_ciclo 
            WHERE fonte LIKE 'Spec_%' AND nupl IS NOT NULL
            ORDER BY timestamp DESC
        """
        
        registros_nupl = execute_query(query_validacao, fetch_all=True)
        logger.info(f"🔍 Validação NUPL: {len(registros_nupl)} registros inseridos com NUPL")
        
        for registro in registros_nupl:
            nupl_val = float(registro['nupl'])
            
            # Classificar NUPL para validação
            if nupl_val > 0.75:
                classificacao = "🔴 EUFORIA"
            elif nupl_val > 0.5:
                classificacao = "🟡 SOBRECOMPRADO"
            elif nupl_val > 0.25:
                classificacao = "⚪ NEUTRO"
            elif nupl_val > 0:
                classificacao = "🟢 ACUMULAÇÃO"
            else:
                classificacao = "💎 OVERSOLD"
            
            logger.info(f"📈 {registro['fonte']}: NUPL={nupl_val:.2f} {classificacao}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao inserir dados v5.1.2: {str(e)}")
        return False

def limpar_dados_exemplo():
    """Remove todos os dados de exemplo das tabelas - v5.1.2 compatível"""
    try:
        logger.info("🧹 Limpando dados de exemplo v5.1.2...")
        
        queries = [
            "DELETE FROM indicadores_ciclo WHERE fonte LIKE 'Spec_%' OR fonte = 'Historico' OR fonte = 'Exemplo'",
            "DELETE FROM indicadores_momentum WHERE fonte LIKE 'Spec_%' OR fonte = 'Historico' OR fonte = 'Exemplo'",
            "DELETE FROM indicadores_risco WHERE fonte LIKE 'Spec_%' OR fonte = 'Historico' OR fonte = 'Exemplo'",
            "DELETE FROM indicadores_tecnico WHERE fonte LIKE 'Spec_%' OR fonte = 'Historico' OR fonte = 'Exemplo'"
        ]
        
        for query in queries:
            result = execute_query(query)
            logger.info(f"Limpeza executada: {result.get('affected_rows', 0)} registros removidos")
        
        logger.info("✅ Dados de exemplo v5.1.2 limpos com sucesso")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao limpar dados v5.1.2: {str(e)}")
        return False

def get_dados_exemplo_nupl_stats():
    """
    NOVA FUNÇÃO v5.1.2: Estatísticas dos dados exemplo com NUPL
    """
    try:
        query = """
            SELECT 
                fonte,
                mvrv_z_score,
                realized_ratio,
                puell_multiple,
                nupl,
                CASE 
                    WHEN nupl > 0.75 THEN 'Euforia'
                    WHEN nupl > 0.5 THEN 'Sobrecomprado'
                    WHEN nupl > 0.25 THEN 'Neutro'
                    WHEN nupl > 0 THEN 'Acumulação'
                    ELSE 'Oversold'
                END as nupl_status,
                timestamp
            FROM indicadores_ciclo 
            WHERE fonte LIKE 'Spec_%'
            ORDER BY nupl DESC
        """
        
        return execute_query(query, fetch_all=True)
        
    except Exception as e:
        logger.error(f"❌ Erro stats exemplo NUPL: {str(e)}")
        return []