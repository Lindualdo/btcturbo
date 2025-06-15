# app/services/utils/helpers/v2/dash_mercado/database_helper.py

import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def save_scores_to_db(dados_scores: dict) -> dict:
    """
    Salva scores no banco PostgreSQL
    
    Args:
        dados_scores: Dict com scores calculados
        
    Returns:
        dict: {"status": "success/error", "id": registro_id}
    """
    try:
        from app.services.utils.helpers.postgres.base import execute_query
        
        # SQL para inserir scores
        query = """
            INSERT INTO dashboard_mercado_scores (
                score_ciclo, classificacao_ciclo,
                score_momentum, classificacao_momentum, 
                score_tecnico, classificacao_tecnico,
                score_consolidado, classificacao_consolidada
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
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
            dados_scores["classificacao_consolidada"]
        )
        
        resultado = execute_query(query, params, fetch_one=True)
        
        if resultado:
            logger.info(f"✅ Scores salvos - ID: {resultado['id']}")
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
    Obtém último registro de scores do banco
    
    Returns:
        dict: Dados do último registro ou None
    """
    try:
        from app.services.utils.helpers.postgres.base import execute_query
        
        query = """
            SELECT 
                id, timestamp,
                score_ciclo, classificacao_ciclo,
                score_momentum, classificacao_momentum,
                score_tecnico, classificacao_tecnico, 
                score_consolidado, classificacao_consolidada
            FROM dashboard_mercado_scores
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

def create_table_if_not_exists():
    """
    Cria tabela dashboard_mercado_scores se não existir
    """
    try:
        from app.services.utils.helpers.postgres.base import execute_query
        
        # SQL para criar tabela
        table_sql = """
            CREATE TABLE IF NOT EXISTS dashboard_mercado_scores (
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