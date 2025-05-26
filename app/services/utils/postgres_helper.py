# app/services/utils/postgres_helper.py
# VERSÃO FINAL - 1 TABELA POR BLOCO

import logging
from datetime import datetime
from typing import Dict, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from app.config import get_settings

def get_db_connection():
    """Conecta com PostgreSQL usando configurações do .env"""
    settings = get_settings()
    return psycopg2.connect(
        host=settings.DB_HOST,
        database=settings.DB_NAME,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        cursor_factory=RealDictCursor
    )

# ==========================================
# FUNÇÕES BLOCO CICLO
# ==========================================

def get_dados_ciclo() -> Optional[Dict]:
    """Busca dados mais recentes do bloco ciclo"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                query = """
                    SELECT mvrv_z_score, realized_ratio, puell_multiple, 
                           timestamp, fonte, metadados
                    FROM indicadores_ciclo 
                    ORDER BY timestamp DESC 
                    LIMIT 1
                """
                cursor.execute(query)
                result = cursor.fetchone()
                return dict(result) if result else None
                
    except Exception as e:
        logging.error(f"Erro ao buscar dados do bloco ciclo: {str(e)}")
        return None

def save_dados_ciclo(dados: Dict) -> bool:
    """Salva dados do bloco ciclo"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                query = """
                    INSERT INTO indicadores_ciclo 
                    (mvrv_z_score, realized_ratio, puell_multiple, fonte, timestamp, metadados)
                    VALUES (%(mvrv_z_score)s, %(realized_ratio)s, %(puell_multiple)s, 
                            %(fonte)s, %(timestamp)s, %(metadados)s)
                """
                
                dados_insert = {
                    "mvrv_z_score": dados.get("mvrv_z_score"),
                    "realized_ratio": dados.get("realized_ratio"),
                    "puell_multiple": dados.get("puell_multiple"),
                    "fonte": dados.get("fonte", "Sistema"),
                    "timestamp": dados.get("timestamp", datetime.utcnow()),
                    "metadados": dados.get("metadados", {})
                }
                
                cursor.execute(query, dados_insert)
                conn.commit()
                
                logging.info(f"Dados do bloco ciclo salvos: {dados_insert}")
                return True
                
    except Exception as e:
        logging.error(f"Erro ao salvar dados do bloco ciclo: {str(e)}")
        return False

def is_ciclo_outdated(hours: int = 8) -> bool:
    """Verifica se bloco ciclo precisa atualização"""
    try:
        dados = get_dados_ciclo()
        
        if not dados:
            logging.info("Bloco ciclo: Não encontrado no PostgreSQL, precisa atualizar")
            return True
        
        last_update = dados["timestamp"]
        time_diff = datetime.utcnow() - last_update
        is_outdated = time_diff.total_seconds() > hours * 3600
        
        if is_outdated:
            logging.info(f"Bloco ciclo: Desatualizado há {time_diff.total_seconds()/3600:.1f}h")
        else:
            logging.info(f"Bloco ciclo: Atualizado, válido por mais {hours - time_diff.total_seconds()/3600:.1f}h")
            
        return is_outdated
        
    except Exception as e:
        logging.error(f"Erro ao verificar bloco ciclo: {str(e)}")
        return True

# ==========================================
# FUNÇÕES BLOCO MOMENTUM
# ==========================================

def get_dados_momentum() -> Optional[Dict]:
    """Busca dados mais recentes do bloco momentum"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                query = """
                    SELECT rsi_semanal, funding_rates, oi_change, long_short_ratio,
                           timestamp, fonte, metadados
                    FROM indicadores_momentum 
                    ORDER BY timestamp DESC 
                    LIMIT 1
                """
                cursor.execute(query)
                result = cursor.fetchone()
                return dict(result) if result else None
                
    except Exception as e:
        logging.error(f"Erro ao buscar dados do bloco momentum: {str(e)}")
        return None

def save_dados_momentum(dados: Dict) -> bool:
    """Salva dados do bloco momentum"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                query = """
                    INSERT INTO indicadores_momentum 
                    (rsi_semanal, funding_rates, oi_change, long_short_ratio, 
                     fonte, timestamp, metadados)
                    VALUES (%(rsi_semanal)s, %(funding_rates)s, %(oi_change)s, 
                            %(long_short_ratio)s, %(fonte)s, %(timestamp)s, %(metadados)s)
                """
                
                dados_insert = {
                    "rsi_semanal": dados.get("rsi_semanal"),
                    "funding_rates": dados.get("funding_rates"),
                    "oi_change": dados.get("oi_change"),
                    "long_short_ratio": dados.get("long_short_ratio"),
                    "fonte": dados.get("fonte", "Sistema"),
                    "timestamp": dados.get("timestamp", datetime.utcnow()),
                    "metadados": dados.get("metadados", {})
                }
                
                cursor.execute(query, dados_insert)
                conn.commit()
                
                logging.info(f"Dados do bloco momentum salvos: {dados_insert}")
                return True
                
    except Exception as e:
        logging.error(f"Erro ao salvar dados do bloco momentum: {str(e)}")
        return False

def is_momentum_outdated(hours: int = 2) -> bool:
    """Verifica se bloco momentum precisa atualização"""
    try:
        dados = get_dados_momentum()
        
        if not dados:
            logging.info("Bloco momentum: Não encontrado, precisa atualizar")
            return True
        
        last_update = dados["timestamp"]
        time_diff = datetime.utcnow() - last_update
        is_outdated = time_diff.total_seconds() > hours * 3600
        
        return is_outdated
        
    except Exception as e:
        logging.error(f"Erro ao verificar bloco momentum: {str(e)}")
        return True

# ==========================================
# FUNÇÕES BLOCO RISCO
# ==========================================

def get_dados_risco() -> Optional[Dict]:
    """Busca dados mais recentes do bloco risco"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                query = """
                    SELECT dist_liquidacao, health_factor, exchange_netflow, stablecoin_ratio,
                           timestamp, fonte, metadados
                    FROM indicadores_risco 
                    ORDER BY timestamp DESC 
                    LIMIT 1
                """
                cursor.execute(query)
                result = cursor.fetchone()
                return dict(result) if result else None
                
    except Exception as e:
        logging.error(f"Erro ao buscar dados do bloco risco: {str(e)}")
        return None

def save_dados_risco(dados: Dict) -> bool:
    """Salva dados do bloco risco"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                query = """
                    INSERT INTO indicadores_risco 
                    (dist_liquidacao, health_factor, exchange_netflow, stablecoin_ratio,
                     fonte, timestamp, metadados)
                    VALUES (%(dist_liquidacao)s, %(health_factor)s, %(exchange_netflow)s, 
                            %(stablecoin_ratio)s, %(fonte)s, %(timestamp)s, %(metadados)s)
                """
                
                dados_insert = {
                    "dist_liquidacao": dados.get("dist_liquidacao"),
                    "health_factor": dados.get("health_factor"),
                    "exchange_netflow": dados.get("exchange_netflow"),
                    "stablecoin_ratio": dados.get("stablecoin_ratio"),
                    "fonte": dados.get("fonte", "Sistema"),
                    "timestamp": dados.get("timestamp", datetime.utcnow()),
                    "metadados": dados.get("metadados", {})
                }
                
                cursor.execute(query, dados_insert)
                conn.commit()
                
                logging.info(f"Dados do bloco risco salvos: {dados_insert}")
                return True
                
    except Exception as e:
        logging.error(f"Erro ao salvar dados do bloco risco: {str(e)}")
        return False

def is_risco_outdated(hours: int = 1) -> bool:
    """Verifica se bloco risco precisa atualização (mais crítico)"""
    try:
        dados = get_dados_risco()
        
        if not dados:
            return True
        
        last_update = dados["timestamp"]
        time_diff = datetime.utcnow() - last_update
        return time_diff.total_seconds() > hours * 3600
        
    except Exception as e:
        logging.error(f"Erro ao verificar bloco risco: {str(e)}")
        return True

# ==========================================
# FUNÇÕES BLOCO TÉCNICO
# ==========================================

def get_dados_tecnico() -> Optional[Dict]:
    """Busca dados mais recentes do bloco técnico"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                query = """
                    SELECT sistema_emas, padroes_graficos,
                           timestamp, fonte, metadados
                    FROM indicadores_tecnico 
                    ORDER BY timestamp DESC 
                    LIMIT 1
                """
                cursor.execute(query)
                result = cursor.fetchone()
                return dict(result) if result else None
                
    except Exception as e:
        logging.error(f"Erro ao buscar dados do bloco técnico: {str(e)}")
        return None

def save_dados_tecnico(dados: Dict) -> bool:
    """Salva dados do bloco técnico"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                query = """
                    INSERT INTO indicadores_tecnico 
                    (sistema_emas, padroes_graficos, fonte, timestamp, metadados)
                    VALUES (%(sistema_emas)s, %(padroes_graficos)s, 
                            %(fonte)s, %(timestamp)s, %(metadados)s)
                """
                
                dados_insert = {
                    "sistema_emas": dados.get("sistema_emas"),
                    "padroes_graficos": dados.get("padroes_graficos"),
                    "fonte": dados.get("fonte", "Sistema"),
                    "timestamp": dados.get("timestamp", datetime.utcnow()),
                    "metadados": dados.get("metadados", {})
                }
                
                cursor.execute(query, dados_insert)
                conn.commit()
                
                logging.info(f"Dados do bloco técnico salvos: {dados_insert}")
                return True
                
    except Exception as e:
        logging.error(f"Erro ao salvar dados do bloco técnico: {str(e)}")
        return False

def is_tecnico_outdated(hours: int = 1) -> bool:
    """Verifica se bloco técnico precisa atualização"""
    try:
        dados = get_dados_tecnico()
        
        if not dados:
            return True
        
        last_update = dados["timestamp"]
        time_diff = datetime.utcnow() - last_update
        return time_diff.total_seconds() > hours * 3600
        
    except Exception as e:
        logging.error(f"Erro ao verificar bloco técnico: {str(e)}")
        return True

# ==========================================
# FUNÇÕES UTILITÁRIAS
# ==========================================

def get_status_todos_blocos() -> Dict:
    """Retorna status de todos os blocos para monitoramento"""
    try:
        status = {
            "timestamp_consulta": datetime.utcnow().isoformat(),
            "blocos": {}
        }
        
        # Status Ciclo
        dados_ciclo = get_dados_ciclo()
        if dados_ciclo:
            time_diff = datetime.utcnow() - dados_ciclo["timestamp"]
            status["blocos"]["ciclo"] = {
                "ultima_atualizacao": dados_ciclo["timestamp"].isoformat(),
                "horas_atras": round(time_diff.total_seconds() / 3600, 2),
                "fonte": dados_ciclo["fonte"],
                "precisa_atualizacao": is_ciclo_outdated()
            }
        else:
            status["blocos"]["ciclo"] = {"status": "sem_dados"}
        
        # Status Momentum
        dados_momentum = get_dados_momentum()
        if dados_momentum:
            time_diff = datetime.utcnow() - dados_momentum["timestamp"]
            status["blocos"]["momentum"] = {
                "ultima_atualizacao": dados_momentum["timestamp"].isoformat(),
                "horas_atras": round(time_diff.total_seconds() / 3600, 2),
                "fonte": dados_momentum["fonte"],
                "precisa_atualizacao": is_momentum_outdated()
            }
        else:
            status["blocos"]["momentum"] = {"status": "sem_dados"}
        
        # Adicionar outros blocos conforme implementação
        
        return status
        
    except Exception as e:
        logging.error(f"Erro ao buscar status dos blocos: {str(e)}")
        return {"erro": str(e)}