# app/services/utils/helpers/postgres/alertas_helper.py

import logging
import json
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from .base import execute_query

logger = logging.getLogger(__name__)

class AlertasPostgresHelper:
    """Helper para operações PostgreSQL de alertas"""
    
    def criar_alerta(self, alerta) -> Optional[int]:
        """Cria novo alerta se não existir similar em cooldown"""
        try:
            # Verificar se existe alerta similar em cooldown
            if self._existe_alerta_similar_em_cooldown(alerta):
                logger.debug(f"⏭️ Alerta {alerta.titulo} em cooldown - pulando")
                return None
            
            query = """
                INSERT INTO alertas_historico 
                (tipo, categoria, prioridade, titulo, mensagem, 
                 threshold_configurado, valor_atual, dados_contexto, cooldown_ate)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """
            
            cooldown_ate = datetime.utcnow() + timedelta(minutes=alerta.cooldown_minutos)
            dados_contexto_json = json.dumps(alerta.dados_contexto)
            
            params = (
                alerta.tipo.value,
                alerta.categoria.value, 
                alerta.prioridade,
                alerta.titulo,
                alerta.mensagem,
                alerta.threshold_configurado,
                alerta.valor_atual,
                dados_contexto_json,
                cooldown_ate
            )
            
            result = execute_query(query, params, fetch_one=True)
            
            if result:
                alerta_id = result["id"]
                logger.info(f"✅ Alerta criado: ID {alerta_id} - {alerta.titulo}")
                return alerta_id
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro criando alerta: {str(e)}")
            return None
    
    def get_alertas_ativos(self, categoria: Optional[str] = None, 
                          tipo: Optional[str] = None, limit: int = 20) -> List[Dict]:
        """Busca alertas ativos com filtros"""
        try:
            where_clauses = ["ativo = true", "resolvido = false"]
            params = []
            
            if categoria:
                where_clauses.append("categoria = %s")
                params.append(categoria)
            
            if tipo:
                where_clauses.append("tipo = %s")
                params.append(tipo)
            
            where_sql = " AND ".join(where_clauses)
            params.append(limit)
            
            query = f"""
                SELECT id, tipo, categoria, prioridade, titulo, mensagem,
                       threshold_configurado, valor_atual, dados_contexto,
                       ativo, resolvido, resolvido_em, timestamp
                FROM alertas_historico 
                WHERE {where_sql}
                ORDER BY prioridade ASC, timestamp DESC
                LIMIT %s
            """
            
            return execute_query(query, tuple(params), fetch_all=True)
            
        except Exception as e:
            logger.error(f"❌ Erro buscando alertas ativos: {str(e)}")
            return []
    
    def get_contadores_alertas(self) -> Dict[str, int]:
        """Contadores por categoria para widget principal"""
        try:
            query = """
                SELECT categoria, COUNT(*) as total
                FROM alertas_historico 
                WHERE ativo = true AND resolvido = false
                GROUP BY categoria
            """
            
            result = execute_query(query, fetch_all=True)
            
            contadores = {}
            for row in result:
                contadores[row["categoria"]] = row["total"]
            
            # Contar volatilidade separadamente
            query_vol = """
                SELECT COUNT(*) as total
                FROM alertas_historico 
                WHERE ativo = true AND resolvido = false AND tipo = 'volatilidade'
            """
            vol_result = execute_query(query_vol, fetch_one=True)
            if vol_result:
                contadores["volatilidade"] = vol_result["total"]
            
            return contadores
            
        except Exception as e:
            logger.error(f"❌ Erro contando alertas: {str(e)}")
            return {}
    
    def get_contadores_por_tipo(self) -> Dict[str, int]:
        """Contadores por tipo"""
        try:
            query = """
                SELECT tipo, COUNT(*) as total
                FROM alertas_historico 
                WHERE ativo = true AND resolvido = false
                GROUP BY tipo
            """
            
            result = execute_query(query, fetch_all=True)
            
            return {row["tipo"]: row["total"] for row in result}
            
        except Exception as e:
            logger.error(f"❌ Erro contando por tipo: {str(e)}")
            return {}
    
    def get_historico_alertas(self, data_inicio: datetime,
                             incluir_resolvidos: bool = True,
                             tipo: Optional[str] = None) -> List[Dict]:
        """Histórico de alertas para timeline"""
        try:
            where_clauses = ["timestamp >= %s"]
            params = [data_inicio]
            
            if not incluir_resolvidos:
                where_clauses.append("resolvido = false")
            
            if tipo:
                where_clauses.append("tipo = %s")
                params.append(tipo)
            
            where_sql = " AND ".join(where_clauses)
            
            query = f"""
                SELECT id, tipo, categoria, prioridade, titulo, mensagem,
                       threshold_configurado, valor_atual, dados_contexto,
                       ativo, resolvido, resolvido_em, timestamp
                FROM alertas_historico 
                WHERE {where_sql}
                ORDER BY timestamp DESC
                LIMIT 100
            """
            
            return execute_query(query, tuple(params), fetch_all=True)
            
        except Exception as e:
            logger.error(f"❌ Erro histórico alertas: {str(e)}")
            return []
    
    def resolver_alerta(self, alerta_id: int) -> bool:
        """Marca alerta como resolvido"""
        try:
            query = """
                UPDATE alertas_historico 
                SET resolvido = true, resolvido_em = %s
                WHERE id = %s AND resolvido = false
            """
            
            result = execute_query(query, (datetime.utcnow(), alerta_id))
            return result.get("affected_rows", 0) > 0
            
        except Exception as e:
            logger.error(f"❌ Erro resolvendo alerta {alerta_id}: {str(e)}")
            return False
    
    def snooze_alerta(self, alerta_id: int, minutos: int) -> bool:
        """Silencia alerta por X minutos"""
        try:
            cooldown_ate = datetime.utcnow() + timedelta(minutes=minutos)
            
            query = """
                UPDATE alertas_historico 
                SET cooldown_ate = %s
                WHERE id = %s
            """
            
            result = execute_query(query, (cooldown_ate, alerta_id))
            return result.get("affected_rows", 0) > 0
            
        except Exception as e:
            logger.error(f"❌ Erro snooze alerta {alerta_id}: {str(e)}")
            return False
    
    def get_alerta_mais_critico(self) -> Optional[Dict]:
        """Busca alerta crítico mais recente para sugerir ação"""
        try:
            query = """
                SELECT titulo, mensagem, dados_contexto
                FROM alertas_historico 
                WHERE ativo = true AND resolvido = false AND categoria = 'critico'
                ORDER BY timestamp DESC
                LIMIT 1
            """
            
            return execute_query(query, fetch_one=True)
            
        except Exception as e:
            logger.error(f"❌ Erro buscando alerta crítico: {str(e)}")
            return None
    
    def count_alertas_ativos(self) -> int:
        """Conta total de alertas ativos"""
        try:
            query = """
                SELECT COUNT(*) as total
                FROM alertas_historico 
                WHERE ativo = true AND resolvido = false
            """
            
            result = execute_query(query, fetch_one=True)
            return result["total"] if result else 0
            
        except Exception as e:
            logger.error(f"❌ Erro contando alertas: {str(e)}")
            return 0
    
    def get_config_alertas(self) -> List[Dict]:
        """Busca configurações de alertas"""
        try:
            query = """
                SELECT tipo, categoria, habilitado, threshold_customizado,
                       cooldown_minutos, notificacao_dashboard, notificacao_webhook
                FROM alertas_config
                ORDER BY tipo, categoria
            """
            
            return execute_query(query, fetch_all=True)
            
        except Exception as e:
            logger.error(f"❌ Erro buscando config: {str(e)}")
            return []
    
    def update_config_alertas(self, configs: List[Dict]) -> bool:
        """Atualiza configurações de alertas"""
        try:
            for config in configs:
                query = """
                    INSERT INTO alertas_config 
                    (tipo, categoria, habilitado, threshold_customizado, cooldown_minutos,
                     notificacao_dashboard, notificacao_webhook, atualizado_em)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (tipo, categoria) 
                    DO UPDATE SET
                        habilitado = EXCLUDED.habilitado,
                        threshold_customizado = EXCLUDED.threshold_customizado,
                        cooldown_minutos = EXCLUDED.cooldown_minutos,
                        notificacao_dashboard = EXCLUDED.notificacao_dashboard,
                        notificacao_webhook = EXCLUDED.notificacao_webhook,
                        atualizado_em = EXCLUDED.atualizado_em
                """
                
                params = (
                    config.get("tipo"),
                    config.get("categoria"),
                    config.get("habilitado", True),
                    config.get("threshold_customizado"),
                    config.get("cooldown_minutos", 60),
                    config.get("notificacao_dashboard", True),
                    config.get("notificacao_webhook", False),
                    datetime.utcnow()
                )
                
                execute_query(query, params)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro atualizando config: {str(e)}")
            return False
    
    def _existe_alerta_similar_em_cooldown(self, alerta) -> bool:
        """Verifica se existe alerta similar em período de cooldown"""
        try:
            query = """
                SELECT id FROM alertas_historico 
                WHERE tipo = %s AND categoria = %s 
                  AND titulo = %s
                  AND cooldown_ate > %s
                LIMIT 1
            """
            
            params = (
                alerta.tipo.value,
                alerta.categoria.value,
                alerta.titulo,
                datetime.utcnow()
            )
            
            result = execute_query(query, params, fetch_one=True)
            return result is not None
            
        except Exception as e:
            logger.error(f"❌ Erro verificando cooldown: {str(e)}")
            return False
    
    def limpar_alertas_antigos(self, dias: int = 30) -> int:
        """Remove alertas antigos para manter performance"""
        try:
            cutoff = datetime.utcnow() - timedelta(days=dias)
            
            query = """
                DELETE FROM alertas_historico 
                WHERE timestamp < %s AND resolvido = true
            """
            
            result = execute_query(query, (cutoff,))
            removed = result.get("affected_rows", 0)
            
            logger.info(f"🧹 {removed} alertas antigos removidos")
            return removed
            
        except Exception as e:
            logger.error(f"❌ Erro limpando alertas: {str(e)}")
            return 0