# app/services/utils/helpers/postgres/dados_exemplo.py - v5.1.3 COM NUPL + SOPR

import logging
from datetime import datetime, timedelta
from .base import execute_query

logger = logging.getLogger(__name__)

def insert_dados_exemplo_realistas():
    """
    Insere dados de exemplo mais realistas baseados na documentação
    v5.1.3: INCLUINDO VALORES SOPR REALISTAS + NUPL v5.1.2
    """
    try:
        logger.info("🧪 Inserindo dados de exemplo v5.1.3 com NUPL + SOPR...")
        
        # ==========================================
        # DADOS CICLO v5.1.2 - COM NUPL (inalterado)
        # ==========================================
        
        dados_ciclo_v512 = [
            # Cenário Bear Profundo (Acumulação)
            {
                "mvrv": 0.8,      # Bear territory
                "realized": 0.75,  # Abaixo de 1.0
                "puell": 0.6,     # Miners em stress
                "nupl": 0.15,     # Acumulação (0-0.25)
                "fonte": "Spec_Bear_Profundo"
            },
            
            # Cenário Bull Inicial (Saindo da acumulação)
            {
                "mvrv": 1.8,      # Começando bull
                "realized": 1.1,  # Acima breakeven
                "puell": 1.0,     # Miners normalizando
                "nupl": 0.35,     # Neutro baixo (0.25-0.5)
                "fonte": "Spec_Bull_Inicial"
            },
            
            # Cenário Bull Maduro (Tendência estabelecida)
            {
                "mvrv": 2.5,      # Bull confirmado
                "realized": 1.4,  # Lucros se materializando
                "puell": 1.3,     # Miners em lucro
                "nupl": 0.62,     # Neutro alto (0.5-0.75)
                "fonte": "Spec_Bull_Maduro"
            },
            
            # Cenário Topo Formando (Euforia Inicial)
            {
                "mvrv": 3.8,      # Territory perigoso
                "realized": 1.9,  # Muito acima de 1.0
                "puell": 2.2,     # Miners em festa
                "nupl": 0.78,     # Euforia inicial (>0.75)
                "fonte": "Spec_Topo_Formando"
            },
            
            # Cenário Topo Extremo (Máxima Euforia)
            {
                "mvrv": 5.1,      # Território histórico
                "realized": 2.3,  # Extremo
                "puell": 3.2,     # Miners eufóricos
                "nupl": 0.89,     # Euforia extrema (perto de 0.9+)
                "fonte": "Spec_Topo_Extremo"
            },
            
            # Cenário Atual (Realista para contexto atual)
            {
                "mvrv": 2.1,      # Moderado
                "realized": 1.3,  # Neutro
                "puell": 1.2,     # OK
                "nupl": 0.42,     # Neutro (0.25-0.5)
                "fonte": "Spec_Atual"
            }
        ]
        
        # Inserir dados ciclo v5.1.2 (inalterado)
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
                dados["nupl"],
                dados["fonte"], 
                timestamp
            )
            execute_query(query, params)
            
            logger.info(f"✅ Inserido cenário CICLO: {dados['fonte']} - NUPL: {dados['nupl']}")
        
        # ==========================================
        # DADOS MOMENTUM v5.1.3 - COM SOPR (NOVO)
        # ==========================================
        
        # Cenários SOPR baseados na tabela de conversão README v5.1.3
        dados_momentum_v513 = [
            # Cenário Capitulação Extrema (SOPR < 0.90)
            {
                "rsi": 25.0,      # RSI oversold
                "funding": -0.025, # Funding negativo (shorts pagando)
                "netflow": -45000, # Exchange outflow massivo
                "ls_ratio": 0.75,  # Long/Short favorável
                "sopr": 0.87,     # ← NOVO v5.1.3: Capitulação extrema (score 10)
                "fonte": "Spec_Capitulacao_Extrema"
            },
            
            # Cenário Capitulação (SOPR 0.93-0.95)
            {
                "rsi": 32.0,      # RSI baixo
                "funding": -0.01,  # Funding levemente negativo
                "netflow": -25000, # Outflow moderado
                "ls_ratio": 0.85,  # Long/Short bom
                "sopr": 0.94,     # ← NOVO v5.1.3: Capitulação (score 8)
                "fonte": "Spec_Capitulacao"
            },
            
            # Cenário Neutro (SOPR 0.99-1.01)
            {
                "rsi": 52.0,      # RSI neutro
                "funding": 0.008,  # Funding levemente positivo
                "netflow": 5000,   # Inflow leve
                "ls_ratio": 0.98,  # Long/Short equilibrado
                "sopr": 1.003,    # ← NOVO v5.1.3: Neutro (score 5)
                "fonte": "Spec_Neutro"
            },
            
            # Cenário Realização Alta (SOPR 1.03-1.05)
            {
                "rsi": 68.0,      # RSI alto
                "funding": 0.035,  # Funding alto (longs pagando)
                "netflow": 35000,  # Inflow (vendas para exchanges)
                "ls_ratio": 1.15,  # Long/Short desfavorável
                "sopr": 1.042,    # ← NOVO v5.1.3: Realização alta (score 2)
                "fonte": "Spec_Realizacao_Alta"
            },
            
            # Cenário Ganância Extrema (SOPR > 1.08)
            {
                "rsi": 78.0,      # RSI extremo
                "funding": 0.065,  # Funding extremo
                "netflow": 65000,  # Inflow massivo
                "ls_ratio": 1.35,  # Long/Short muito desfavorável
                "sopr": 1.12,     # ← NOVO v5.1.3: Ganância extrema (score 0)
                "fonte": "Spec_Ganancia_Extrema"
            },
            
            # Cenário Atual (Realista)
            {
                "rsi": 48.5,      # RSI neutro baixo
                "funding": 0.012,  # Funding moderado
                "netflow": 8500,   # Inflow leve
                "ls_ratio": 1.02,  # Long/Short ligeiramente desfavorável
                "sopr": 1.015,    # ← NOVO v5.1.3: Realização leve (score 4)
                "fonte": "Spec_Atual"
            }
        ]
        
        # Inserir dados momentum v5.1.3 COM SOPR
        for i, dados in enumerate(dados_momentum_v513):
            query = """
                INSERT INTO indicadores_momentum 
                (rsi_semanal, funding_rates, exchange_netflow, long_short_ratio, sopr, fonte, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            timestamp = datetime.utcnow() - timedelta(hours=len(dados_momentum_v513) - i)
            params = (
                dados["rsi"],
                dados["funding"],
                dados["netflow"], 
                dados["ls_ratio"],
                dados["sopr"],  # ← NOVO v5.1.3
                dados["fonte"], 
                timestamp
            )
            execute_query(query, params)
            
            # Classificar SOPR para log
            sopr_val = dados["sopr"]
            if sopr_val < 0.90:
                sopr_status = "🔥 CAPITULAÇÃO EXTREMA"
            elif sopr_val < 0.95:
                sopr_status = "💎 CAPITULAÇÃO"
            elif sopr_val < 0.99:
                sopr_status = "🟡 PRESSÃO"
            elif sopr_val <= 1.01:
                sopr_status = "⚪ NEUTRO"
            elif sopr_val < 1.05:
                sopr_status = "📈 REALIZAÇÃO"
            elif sopr_val < 1.08:
                sopr_status = "🔴 GANÂNCIA"
            else:
                sopr_status = "🚨 GANÂNCIA EXTREMA"
            
            logger.info(f"✅ Inserido cenário MOMENTUM: {dados['fonte']} - SOPR: {sopr_val} {sopr_status}")
        
        # ==========================================
        # DADOS OUTROS BLOCOS (sem alteração v5.1.3)
        # ==========================================
        
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
        
        logger.info("✅ Dados de exemplo v5.1.3 inseridos com sucesso")
        logger.info(f"📊 Inseridos: {len(dados_ciclo_v512)} ciclo (COM NUPL), {len(dados_momentum_v513)} momentum (COM SOPR), {len(dados_risco)} risco, {len(dados_tecnico)} técnico")
        
        # ==========================================
        # VALIDAÇÃO SOPR v5.1.3
        # ==========================================
        
        # Verificar dados SOPR inseridos
        query_validacao_sopr = """
            SELECT fonte, sopr, rsi_semanal, timestamp
            FROM indicadores_momentum 
            WHERE fonte LIKE 'Spec_%' AND sopr IS NOT NULL
            ORDER BY timestamp DESC
        """
        
        registros_sopr = execute_query(query_validacao_sopr, fetch_all=True)
        logger.info(f"🔍 Validação SOPR: {len(registros_sopr)} registros inseridos com SOPR")
        
        for registro in registros_sopr:
            sopr_val = float(registro['sopr'])
            
            # Classificar SOPR para validação (conforme tabela README)
            if sopr_val < 0.90:
                classificacao = "🔥 CAPITULAÇÃO EXTREMA"
                score_esperado = 10
            elif sopr_val < 0.95:
                classificacao = "💎 CAPITULAÇÃO"
                score_esperado = "8-9"
            elif sopr_val < 0.99:
                classificacao = "🟡 PRESSÃO"
                score_esperado = "6-7"
            elif sopr_val <= 1.01:
                classificacao = "⚪ NEUTRO"
                score_esperado = 5
            elif sopr_val < 1.05:
                classificacao = "📈 REALIZAÇÃO"
                score_esperado = "2-4"
            elif sopr_val < 1.08:
                classificacao = "🔴 GANÂNCIA"
                score_esperado = 1
            else:
                classificacao = "🚨 GANÂNCIA EXTREMA"
                score_esperado = 0
            
            logger.info(f"📈 {registro['fonte']}: SOPR={sopr_val:.3f} {classificacao} (Score: {score_esperado})")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao inserir dados v5.1.3: {str(e)}")
        return False

def get_dados_exemplo_sopr_stats():
    """
    NOVA FUNÇÃO v5.1.3: Estatísticas dos dados exemplo com SOPR
    """
    try:
        query = """
            SELECT 
                fonte,
                rsi_semanal,
                funding_rates,
                exchange_netflow,
                long_short_ratio,
                sopr,
                CASE 
                    WHEN sopr < 0.90 THEN 'Capitulação Extrema'
                    WHEN sopr < 0.95 THEN 'Capitulação'
                    WHEN sopr < 0.99 THEN 'Pressão'
                    WHEN sopr <= 1.01 THEN 'Neutro'
                    WHEN sopr < 1.05 THEN 'Realização'
                    WHEN sopr < 1.08 THEN 'Ganância'
                    ELSE 'Ganância Extrema'
                END as sopr_status,
                timestamp
            FROM indicadores_momentum 
            WHERE fonte LIKE 'Spec_%' AND sopr IS NOT NULL
            ORDER BY sopr ASC
        """
        
        return execute_query(query, fetch_all=True)
        
    except Exception as e:
        logger.error(f"❌ Erro stats exemplo SOPR: {str(e)}")
        return []

def get_dados_exemplo_completos_stats():
    """
    NOVA FUNÇÃO v5.1.3: Estatísticas completas dos dados exemplo (NUPL + SOPR)
    """
    try:
        logger.info("📊 Gerando estatísticas completas dos dados exemplo v5.1.3...")
        
        # Stats NUPL (v5.1.2)
        nupl_stats = get_dados_exemplo_nupl_stats()
        
        # Stats SOPR (v5.1.3)
        sopr_stats = get_dados_exemplo_sopr_stats()
        
        return {
            "versao": "5.1.3",
            "timestamp": datetime.utcnow().isoformat(),
            "ciclo_nupl": {
                "total_registros": len(nupl_stats),
                "dados": nupl_stats
            },
            "momentum_sopr": {
                "total_registros": len(sopr_stats),
                "dados": sopr_stats
            },
            "cobertura": {
                "nupl_implementado": "v5.1.2",
                "sopr_implementado": "v5.1.3"
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Erro stats completas: {str(e)}")
        return {"erro": str(e)}

# Manter função v5.1.2 para compatibilidade
def get_dados_exemplo_nupl_stats():
    """Função v5.1.2 mantida para compatibilidade"""
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

def limpar_dados_exemplo():
    """Remove todos os dados de exemplo das tabelas - v5.1.3 compatível"""
    try:
        logger.info("🧹 Limpando dados de exemplo v5.1.3...")
        
        queries = [
            "DELETE FROM indicadores_ciclo WHERE fonte LIKE 'Spec_%' OR fonte = 'Historico' OR fonte = 'Exemplo'",
            "DELETE FROM indicadores_momentum WHERE fonte LIKE 'Spec_%' OR fonte = 'Historico' OR fonte = 'Exemplo'",
            "DELETE FROM indicadores_risco WHERE fonte LIKE 'Spec_%' OR fonte = 'Historico' OR fonte = 'Exemplo'",
            "DELETE FROM indicadores_tecnico WHERE fonte LIKE 'Spec_%' OR fonte = 'Historico' OR fonte = 'Exemplo'"
        ]
        
        for query in queries:
            result = execute_query(query)
            logger.info(f"Limpeza executada: {result.get('affected_rows', 0)} registros removidos")
        
        logger.info("✅ Dados de exemplo v5.1.3 limpos com sucesso")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao limpar dados v5.1.3: {str(e)}")
        return False