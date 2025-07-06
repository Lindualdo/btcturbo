# app/services/decisao_estrategica/utils/data_helper.py

import logging
from datetime import datetime
from typing import Dict, Optional
from app.services.utils.helpers.postgres.base import execute_query

logger = logging.getLogger(__name__)

def obter_estrategia(score_tendencia: int, score_ciclo: int) -> Optional[Dict]:
    """
    Busca estratégia correspondente na matriz v2 baseada nos scores
    
    Args:
        score_tendencia: Score tendência (0-100)
        score_ciclo: Score ciclo (0-100) - chamado score_onchain na matriz v2
        
    Returns:
        Dict com estratégia encontrada ou None
    """
    try:
        logger.info(f"🔍 Buscando estratégia para Tendência:{score_tendencia}, Ciclo:{score_ciclo}")
        
        # Validar inputs
        if not (0 <= score_tendencia <= 100) or not (0 <= score_ciclo <= 100):
            raise ValueError(f"Scores inválidos: tendência={score_tendencia}, ciclo={score_ciclo}")
        
        query = """
            SELECT 
                id, tendencia, alavancagem, satelite_percent, acao, protecao,
                score_tendencia_min, score_tendencia_max, 
                score_onchain_min, score_onchain_max
            FROM matriz_estrategica_v2 
            WHERE %s BETWEEN score_tendencia_min AND score_tendencia_max
              AND %s BETWEEN score_onchain_min AND score_onchain_max
            ORDER BY id
            LIMIT 1
        """
        
        result = execute_query(query, params=(score_tendencia, score_ciclo), fetch_one=True)
        
        if result:
            # Mapear campos para manter compatibilidade
            estrategia = {
                "id": result["id"],
                "fase_operacional": result["fase_operacional"], 
                "alavancagem": result["alavancagem"],
                "satelite": result["satelite_percent"] / 100.0,  # converter % para decimal
                "acao": result["acao"],
                "tendencia": _mapear_tendencia(result["tendencia"]),  
                "score_tendencia_min": result["score_tendencia_min"],
                "score_tendencia_max": result["score_tendencia_max"],
                "score_ciclo_min": result["score_onchain_min"],
                "score_ciclo_max": result["score_onchain_max"]
            }
            
            logger.info(f"✅ Estratégia encontrada: {estrategia['fase_operacional']} - {estrategia['tendencia']}")
            return estrategia
        else:
            logger.warning(f"⚠️ Nenhuma estratégia encontrada para scores T:{score_tendencia}, C:{score_ciclo}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Erro ao buscar estratégia: {str(e)}")
        return None

def _mapear_tendencia(cenario: str) -> str:
    """
    Mapeia cenário para tendência para manter compatibilidade
    
    Args:
        cenario: Nome do cenário da matriz v2
        
    Returns:
        Tendência mapeada
    """
    mapeamento = {
        "Bull Forte": "BULL",
        "Bull Consolidação": "BULL", 
        "Neutro": "NEUTRO",
        "Bear": "BEAR",
        "Bear Extremo": "BEAR"
    }
    
    return mapeamento.get(cenario, "NEUTRO")

def inserir_decisao(dados: Dict) -> bool:
    """
    Insere nova decisão estratégica no histórico
    
    Args:
        dados: Dict com dados da decisão + JSONs auditoria
        
    Returns:
        bool: Sucesso da operação
    """
    try:
        logger.info(f"💾 Inserindo decisão estratégica: {dados.get('fase_operacional')}")
        
        # Converter JSONs para string com serialização segura de datetime
        import json
        from datetime import datetime
        
        def json_serializer(obj):
            """Serializa datetime para JSON"""
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
        
        json_emas_str = json.dumps(dados.get("json_emas", {}), default=json_serializer)
        json_ciclo_str = json.dumps(dados.get("json_ciclo", {}), default=json_serializer)
        
        query = """
            INSERT INTO decisao_estrategica (
                score_tendencia, score_ciclo, matriz_id,
                fase_operacional, alavancagem, satelite, acao, tendencia,
                json_emas, json_ciclo, timestamp
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        params = (
            dados.get("score_tendencia"),
            dados.get("score_ciclo"),
            dados.get("matriz_id"),
            dados.get("fase_operacional"),
            dados.get("alavancagem"),
            dados.get("satelite"),
            dados.get("acao"),
            dados.get("tendencia"),
            json_emas_str,
            json_ciclo_str,
            datetime.utcnow()
        )
        
        execute_query(query, params)
        logger.info("✅ Decisão estratégica + JSONs auditoria inseridos com sucesso")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao inserir decisão: {str(e)}")
        return False

def get_ultima_decisao() -> Optional[Dict]:
    """
    Busca última decisão estratégica
    
    Returns:
        Dict com última decisão ou None
    """
    try:
        logger.info("🔍 Buscando última decisão estratégica...")
        
        query = """
            SELECT 
                score_tendencia, score_ciclo, fase_operacional,
                alavancagem, satelite, acao, tendencia, timestamp
            FROM decisao_estrategica 
            ORDER BY timestamp DESC 
            LIMIT 1
        """
        
        result = execute_query(query, fetch_one=True)
        
        if result:
            return dict(result)
        else:
            logger.warning("⚠️ Nenhuma decisão encontrada no histórico")
            return None
            
    except Exception as e:
        logger.error(f"❌ Erro ao buscar última decisão: {str(e)}")
        return None

def get_detalhe_estrategia() -> Optional[Dict]:
    """
    Busca os JSONs com detalhe da última estratégia
    Returns:
        Dict com última decisão ou None
    """
    try:
        logger.info("🔍 Buscando última decisão estratégica...")
        
        query = """
            SELECT 
                score_tendencia, score_ciclo, fase_operacional,
                alavancagem, satelite, acao, tendencia, timestamp,
                json_emas, json_ciclo
            FROM decisao_estrategica 
            ORDER BY timestamp DESC 
            LIMIT 1
        """
        
        result = execute_query(query, fetch_one=True)
        
        if result:
            logger.info(f"✅ Última decisão: {result['fase_operacional']} ({result['timestamp']})")
            return dict(result)
        else:
            logger.warning("⚠️ Nenhuma decisão encontrada no histórico")
            return None
            
    except Exception as e:
        logger.error(f"❌ Erro ao buscar última decisão: {str(e)}")
        return None

def get_historico_decisoes(limit: int = 10) -> list:
    """
    Busca histórico de decisões estratégicas (incluindo JSONs auditoria)
    
    Args:
        limit: Número máximo de registros
        
    Returns:
        List com histórico de decisões
    """
    try:
        logger.info(f"📊 Buscando histórico decisões (últimos {limit})")
        
        query = """
            SELECT 
                id, score_tendencia, score_ciclo, fase_operacional,
                alavancagem, satelite, acao, tendencia, timestamp,
                json_emas, json_ciclo
            FROM decisao_estrategica 
            ORDER BY timestamp DESC 
            LIMIT %s
        """
        
        result = execute_query(query, params=(limit,), fetch_all=True)
        
        if result:
            logger.info(f"✅ {len(result)} decisões históricas encontradas")
            return [dict(row) for row in result]
        else:
            logger.warning("⚠️ Nenhum histórico encontrado")
            return []
            
    except Exception as e:
        logger.error(f"❌ Erro ao buscar histórico: {str(e)}")
        return []

def validar_matriz_completa() -> Dict:
    """
    Valida se a matriz estratégica v2 está completa (25 cenários)
    
    Returns:
        Dict com status da validação
    """
    try:
        logger.info("🔍 Validando completude da matriz estratégica v2...")
        
        query = """
            SELECT 
                COUNT(*) as total_cenarios,
                COUNT(CASE WHEN cenario LIKE '%Bull%' THEN 1 END) as bull_cenarios,
                COUNT(CASE WHEN cenario LIKE '%Bear%' THEN 1 END) as bear_cenarios,
                COUNT(CASE WHEN cenario = 'Neutro' THEN 1 END) as neutro_cenarios
            FROM matriz_estrategica_v2
        """
        
        result = execute_query(query, fetch_one=True)
        
        if result:
            total = result["total_cenarios"]
            status = "✅ COMPLETA" if total == 25 else f"⚠️ INCOMPLETA ({total}/25)"
            
            logger.info(f"📊 Matriz v2: {status}")
            
            return {
                "status": "completa" if total == 25 else "incompleta",
                "total_cenarios": total,
                "distribuicao": {
                    "bull": result["bull_cenarios"],
                    "bear": result["bear_cenarios"],
                    "neutro": result["neutro_cenarios"]
                },
                "esperado": 25
            }
        else:
            return {"status": "erro", "total_cenarios": 0}
            
    except Exception as e:
        logger.error(f"❌ Erro na validação da matriz: {str(e)}")
        return {"status": "erro", "erro": str(e)}