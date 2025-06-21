# source: app/services/dashboards/dash_mercado/database_helper.py

import logging
from datetime import datetime,timedelta

logger = logging.getLogger(__name__)

def save_scores_to_db(dados_scores: dict) -> dict:
    """
    Salva scores + JSON completo formatado no banco
    """
    try:
        from app.services.utils.helpers.postgres.base import execute_query
        
        # Buscar IDs dos últimos registros de indicadores
        ids_indicadores = _get_latest_indicators_ids()
        
        # Montar JSON completo dos indicadores com scores
        json_indicadores = _build_indicators_json()

        timestamp_lisboa = (datetime.utcnow() + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
        
        # SQL para inserir scores + JSON
        query = """
            INSERT INTO dash_mercado (
                score_ciclo, classificacao_ciclo,
                score_momentum, classificacao_momentum, 
                score_tecnico, classificacao_tecnico,
                score_consolidado, classificacao_consolidada,
                indicadores_json,
                indicador_ciclo_id, indicador_momentum_id, indicador_tecnico_id, timestamp
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        
        params = (
            dados_scores["score_ciclo"],
            dados_scores["classificacao_ciclo"],
            dados_scores["score_momentum"], 
            dados_scores["classificacao_momentum"],
            dados_scores["score_tecnico"],
            dados_scores["classificacao_tecnico"],
            dados_scores["score_consolidado"],
            dados_scores["classificacao_consolidada"],
            json_indicadores,  # JSON pronto
            ids_indicadores.get("ciclo_id"),
            ids_indicadores.get("momentum_id"),
            ids_indicadores.get("tecnico_id"),
            timestamp_lisboa
        )
        
        resultado = execute_query(query, params, fetch_one=True)
        
        if resultado:
            logger.info(f"✅ Scores + JSON salvos - ID: {resultado['id']}")
            return {
                "status": "success",
                "id": resultado["id"]
            }
        else:
            return {
                "status": "error",
                "erro": "Falha ao inserir registro"
            }
            
    except Exception as e:
        logger.error(f"❌ Erro save_scores_to_db: {str(e)}")
        return {
            "status": "error",
            "erro": str(e)
        }

def get_latest_scores_from_db() -> dict:
    """
    Obtém último registro com JSON já formatado
    """
    try:
        from app.services.utils.helpers.postgres.base import execute_query
        
        query = """
            SELECT 
                id, timestamp,
                score_ciclo, classificacao_ciclo,
                score_momentum, classificacao_momentum,
                score_tecnico, classificacao_tecnico, 
                score_consolidado, classificacao_consolidada,
                indicadores_json
            FROM dash_mercado
            WHERE indicadores_json IS NOT NULL
            ORDER BY timestamp DESC
            LIMIT 1
        """
        
        resultado = execute_query(query, fetch_one=True)
        
        if resultado:
            logger.info(f"✅ Último registro obtido - ID: {resultado['id']}")
            return resultado
        else:
            logger.info("ℹ️ Nenhum registro encontrado")
            return None
            
    except Exception as e:
        logger.error(f"❌ Erro get_latest_scores_from_db: {str(e)}")
        return None

def _build_indicators_json() -> str:
    """Constrói JSON completo dos indicadores com scores"""
    try:
        import json
        from app.services.indicadores import ciclos, momentum
        from app.services.scores.ciclos import calcular_mvrv_score, calcular_nupl_score, calcular_realized_score, calcular_puell_score
        from app.services.scores.momentum import calcular_rsi_score, calcular_funding_score, calcular_sopr_score, calcular_ls_ratio_score
        from app.services.utils.helpers.postgres.indicadores.tecnico_helper import get_dados_tecnico
        
        # Dados CICLO
        dados_ciclo = ciclos.obter_indicadores()["indicadores"]
        mvrv_score, _ = calcular_mvrv_score(dados_ciclo["MVRV_Z"]["valor"])
        nupl_score, _ = calcular_nupl_score(dados_ciclo["NUPL"]["valor"])
        realized_score, _ = calcular_realized_score(dados_ciclo["Realized_Ratio"]["valor"])
        puell_score, _ = calcular_puell_score(dados_ciclo["Puell_Multiple"]["valor"])
        
        # Dados MOMENTUM
        dados_momentum = momentum.obter_indicadores()["indicadores"]
        rsi_score, _ = calcular_rsi_score(dados_momentum["RSI_Semanal"]["valor"])
        funding_score, _ = calcular_funding_score(dados_momentum["Funding_Rates"]["valor"])
        sopr_score, _ = calcular_sopr_score(dados_momentum["SOPR"]["valor"])
        ls_score, _ = calcular_ls_ratio_score(dados_momentum["Long_Short_Ratio"]["valor"])
        
        # Dados TÉCNICO - buscar direto do banco
        dados_tecnico_db = get_dados_tecnico()
        
        if dados_tecnico_db:
            score_geral = float(dados_tecnico_db["score_bloco_final"]) if dados_tecnico_db["score_bloco_final"] else 0
            tecnico_json = {
                "score": score_geral,
                "classificacao": _get_score_description(score_geral),
                "semanal": {
                    "score": float(dados_tecnico_db["score_consolidado_1w"]) if dados_tecnico_db["score_consolidado_1w"] else 0,
                    "alinhamento": float(dados_tecnico_db["score_1w_ema"]) if dados_tecnico_db["score_1w_ema"] else 0,
                    "posicao": float(dados_tecnico_db["score_1w_price"]) if dados_tecnico_db["score_1w_price"] else 0
                },
                "diario": {
                    "score": float(dados_tecnico_db["score_consolidado_1d"]) if dados_tecnico_db["score_consolidado_1d"] else 0,
                    "alinhamento": float(dados_tecnico_db["score_1d_ema"]) if dados_tecnico_db["score_1d_ema"] else 0,
                    "posicao": float(dados_tecnico_db["score_1d_price"]) if dados_tecnico_db["score_1d_price"] else 0
                }
            }
        else:
            tecnico_json = {
                "score": 0,
                "classificacao": "N/A",
                "semanal": {"score": 0, "alinhamento": 0, "posicao": 0},
                "diario": {"score": 0, "alinhamento": 0, "posicao": 0}
            }
        
        json_completo = {
            "ciclo": {
                "mvrv": {"valor": dados_ciclo["MVRV_Z"]["valor"], "score": mvrv_score},
                "nupl": {"valor": dados_ciclo["NUPL"]["valor"], "score": nupl_score},
                "realized_price_ratio": {"valor": dados_ciclo["Realized_Ratio"]["valor"], "score": realized_score},
                "puell_multiple": {"valor": dados_ciclo["Puell_Multiple"]["valor"], "score": puell_score}
            },
            "momentum": {
                "rsi_semanal": {"valor": dados_momentum["RSI_Semanal"]["valor"], "score": rsi_score},
                "funding_rate": {"valor": dados_momentum["Funding_Rates"]["valor"], "score": funding_score},
                "sopr": {"valor": dados_momentum["SOPR"]["valor"], "score": sopr_score},
                "long_short_ratio": {"valor": dados_momentum["Long_Short_Ratio"]["valor"], "score": ls_score}
            },
            "tecnico": tecnico_json
        }
        
        return json.dumps(json_completo)
        
    except Exception as e:
        logger.error(f"❌ Erro _build_indicators_json: {str(e)}")
        return "{}"

def _get_score_description(score):
    """Converte score numérico em descrição"""
    if score >= 8.1:
        return "Tendência Forte"
    elif score >= 6.1:
        return "Correção Saudável"
    elif score >= 4.1:
        return "Neutro"
    elif score >= 2.1:
        return "Reversão"
    else:
        return "Bear Confirmado"

def _get_latest_indicators_ids() -> dict:
    """Busca IDs dos últimos registros de indicadores"""
    try:
        from app.services.utils.helpers.postgres.base import execute_query
        
        # Buscar último ID de cada tabela
        queries = {
            "ciclo_id": "SELECT id FROM indicadores_ciclo ORDER BY timestamp DESC LIMIT 1",
            "momentum_id": "SELECT id FROM indicadores_momentum ORDER BY timestamp DESC LIMIT 1", 
            "tecnico_id": "SELECT id FROM indicadores_tecnico ORDER BY timestamp DESC LIMIT 1"
        }
        
        ids = {}
        for key, query in queries.items():
            resultado = execute_query(query, fetch_one=True)
            ids[key] = resultado["id"] if resultado else None
            
        return ids
        
    except Exception as e:
        logger.error(f"❌ Erro _get_latest_indicators_ids: {str(e)}")
        return {"ciclo_id": None, "momentum_id": None, "tecnico_id": None}

def create_table_if_not_exists():
    """
    Cria tabela dashboard_mercado_scores se não existir
    """
    try:
        from app.services.utils.helpers.postgres.base import execute_query
        
        # SQL para criar tabela
        table_sql = """
            CREATE TABLE IF NOT EXISTS dash_mercado (
                id SERIAL PRIMARY KEY,
                
                -- Scores dos blocos
                score_ciclo DECIMAL(5,2) NOT NULL,
                classificacao_ciclo VARCHAR(20) NOT NULL,
                score_momentum DECIMAL(5,2) NOT NULL,
                classificacao_momentum VARCHAR(20) NOT NULL,
                score_tecnico DECIMAL(5,2) NOT NULL,
                classificacao_tecnico VARCHAR(20) NOT NULL,
                
                -- Score consolidado
                score_consolidado DECIMAL(5,2) NOT NULL,
                classificacao_consolidada VARCHAR(20) NOT NULL,
                
                -- JSON pronto para consumo no dashboard
                indicadores_json JSONB NOT NULL,
                
                -- Relacionamentos (FK para auditoria)
                indicador_ciclo_id INTEGER REFERENCES indicadores_ciclo(id),
                indicador_momentum_id INTEGER REFERENCES indicadores_momentum(id),
                indicador_tecnico_id INTEGER REFERENCES indicadores_tecnico(id),
                
                -- Metadados
                timestamp TIMESTAMP DEFAULT NOW(),
                versao VARCHAR(10) DEFAULT 'v1.0'
            );
            
            -- Índice para busca otimizada
            CREATE INDEX IF NOT EXISTS idx_dashboard_mercado_timestamp 
            ON dashboard_mercado_scores(timestamp DESC);
        """
        
        execute_query(table_sql)
        logger.info("✅ Tabela dashboard_mercado_scores verificada/criada")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro criar tabela: {str(e)}")
        return False