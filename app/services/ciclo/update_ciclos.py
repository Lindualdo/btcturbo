# app/services/blocos/ciclos/update_ciclo.py

from datetime import datetime
from typing import Dict
import logging

def update_ciclo(forcar: bool = False) -> Dict:
    """
    Atualiza indicadores do bloco ciclo.
    
    Args:
        forcar: Se True, ignora cache e força atualização
        
    Returns:
        Dict com status da atualização e dados atuais
    """
    try:
        from app.services.utils.postgres_helper import is_ciclo_outdated, get_dados_ciclo
        from app.services.integracao.notion_ciclo_reader import update_ciclo_from_notion
        
        # Verifica se precisa atualizar (ou se está sendo forçado)
        precisa_atualizar = forcar or is_ciclo_outdated(hours=8)
        
        if not precisa_atualizar:
            # Dados ainda válidos, retorna do cache PostgreSQL
            dados_cache = get_dados_ciclo()
            
            logging.info("Bloco ciclo: Usando dados do cache PostgreSQL")
            
            return {
                "bloco": "ciclo",
                "atualizado": False,
                "motivo": "cache_valido",
                "dados": {
                    "mvrv_z_score": dados_cache.get("mvrv_z_score"),
                    "realized_ratio": dados_cache.get("realized_ratio"),
                    "puell_multiple": dados_cache.get("puell_multiple")
                },
                "fonte": dados_cache.get("fonte"),
                "timestamp_dados": dados_cache.get("timestamp").isoformat() if dados_cache.get("timestamp") else None,
                "timestamp_verificacao": datetime.utcnow().isoformat() + "Z"
            }
        
        # Precisa atualizar - busca do Notion e salva no PostgreSQL
        logging.info("Bloco ciclo: Buscando dados atualizados do Notion")
        
        # Chama função que busca Notion e salva PostgreSQL
        sucesso = update_ciclo_from_notion()
        
        if not sucesso:
            raise Exception("Falha ao atualizar dados do Notion")
        
        # Busca dados recém-salvos para confirmar
        dados_atualizados = get_dados_ciclo()
        
        if not dados_atualizados:
            raise Exception("Dados não foram salvos corretamente no PostgreSQL")
        
        logging.info("Bloco ciclo: Dados atualizados com sucesso")
        
        return {
            "bloco": "ciclo",
            "atualizado": True,
            "motivo": "forcado" if forcar else "cache_expirado",
            "dados": {
                "mvrv_z_score": dados_atualizados.get("mvrv_z_score"),
                "realized_ratio": dados_atualizados.get("realized_ratio"),
                "puell_multiple": dados_atualizados.get("puell_multiple")
            },
            "fonte": "Notion",
            "timestamp_dados": dados_atualizados.get("timestamp").isoformat() if dados_atualizados.get("timestamp") else None,
            "timestamp_atualizacao": datetime.utcnow().isoformat() + "Z"
        }
        
    except Exception as e:
        logging.error(f"Erro ao atualizar bloco ciclo: {str(e)}")
        
        # Tenta retornar dados existentes mesmo com erro na atualização
        try:
            dados_fallback = get_dados_ciclo()
            if dados_fallback:
                logging.warning("Retornando dados existentes devido ao erro na atualização")
                return {
                    "bloco": "ciclo",
                    "atualizado": False,
                    "motivo": "erro_com_fallback",
                    "dados": {
                        "mvrv_z_score": dados_fallback.get("mvrv_z_score"),
                        "realized_ratio": dados_fallback.get("realized_ratio"),
                        "puell_multiple": dados_fallback.get("puell_multiple")
                    },
                    "fonte": dados_fallback.get("fonte"),
                    "timestamp_dados": dados_fallback.get("timestamp").isoformat() if dados_fallback.get("timestamp") else None,
                    "erro": str(e),
                    "timestamp_erro": datetime.utcnow().isoformat() + "Z"
                }
        except Exception:
            pass
        
        # Se não conseguiu nem buscar dados existentes
        return {
            "bloco": "ciclo",
            "atualizado": False,
            "motivo": "erro",
            "dados": None,
            "erro": str(e),
            "timestamp_erro": datetime.utcnow().isoformat() + "Z"
        }