# source: app/services/dashboards/dash_mercado/database_helper.py

import logging
from datetime import datetime,timedelta
from app.services.utils.helpers.postgres.base import execute_query

logger = logging.getLogger(__name__)

def save_scores_to_db(dados_scores: dict) -> dict:
    """
    Salva scores + JSON completo formatado no banco
    """
    try:
        
        # Buscar IDs dos últimos registros de indicadores
        ids_indicadores = _get_latest_indicators_ids()
        
        # Montar JSON completo dos indicadores com scores
        json_indicadores = _build_indicators_json(dados_scores) 

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
            dados_scores["ciclo"]["score_consolidado"],
            dados_scores["ciclo"]["classificacao_consolidada"],
            dados_scores["momentum"]["score_consolidado"], 
            dados_scores["momentum"]["classificacao_consolidada"],
            dados_scores["tecnico"]["score_consolidado"],
            dados_scores["tecnico"]["classificacao_consolidada"],
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

def _build_indicators_json(dados_scores: dict) -> str:
    """Constrói JSON usando apenas dados_scores (já contém tudo)"""
    try:
        import json
        from datetime import datetime
        from decimal import Decimal
        
        def serialize_json(obj):
            """Serializa datetime e Decimal para JSON"""
            if isinstance(obj, datetime):
                return obj.isoformat()
            elif isinstance(obj, Decimal):
                return float(obj)
            elif isinstance(obj, dict):
                return {k: serialize_json(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [serialize_json(item) for item in obj]
            else:
                return obj
        
        # Estrutura JSON usando dados que já estão em dados_scores
        json_completo = {
            "ciclo": serialize_json(dados_scores.get("ciclo", {})),
            "momentum": serialize_json(dados_scores.get("momentum", {})),
            "tecnico": serialize_json(dados_scores.get("tecnico", {}))
        }
        
        return json.dumps(json_completo)
        
    except Exception as e:
        logger.error(f"❌ Erro _build_indicators_json: {str(e)}")
        return "{}"

def get_latest_scores_from_db() -> dict:
    """
    Obtém último registro com JSON já formatado
    """
    try:
        
        
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

    """Constrói JSON completo dos indicadores com scores"""
    try:
        return "{}"

        
        
        return json.dumps(json_completo)
        
    except Exception as e:
        logger.error(f"❌ Erro _build_indicators_json: {str(e)}")
        return "{}"

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