# app/routers/obter_indicadores.py

from fastapi import APIRouter, Query, HTTPException
from datetime import datetime
from typing import Dict, List
import logging

router = APIRouter()

@router.get("/obter-indicadores", 
            summary="Obter Todos Indicadores", 
            tags=["Indicadores"])
def obter_todos_indicadores(forcar: bool = Query(False, description="Forçar atualização dos dados ignorando cache")):
    """
    Obtém dados de todos os blocos de indicadores do PostgreSQL.
    Atualiza automaticamente se dados estiverem desatualizados ou se forçado.
    
    Esta é a API CENTRALIZADORA usada por:
    - APIs de score (/analise-btc, /analise-ciclo)
    - Scheduler N8N (com forcar=true)
    - Dashboard e outras consultas
    
    Args:
        forcar: Se True, ignora cache e força atualização de todos os blocos
        
    Returns:
        Dados brutos atuais de todos os blocos + status de processamento
    """
    resultado = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "parametro_forcar": forcar,
        "blocos_processados": {},
        "dados_brutos": {},
        "resumo": {
            "total_blocos": 0,
            "blocos_atualizados": 0,
            "blocos_cache": 0,
            "blocos_erro": 0
        }
    }
    
    # Processamento do bloco ciclo com import direto
    try:
        logging.info("Processando bloco ciclo...")
        
        # Import direto para evitar problemas de path
        from app.services.utils.postgres_helper import is_ciclo_outdated, get_dados_ciclo
        from app.services.integracao.notion_ciclo_reader import update_ciclo_from_notion
        
        # Verifica se precisa atualizar
        precisa_atualizar = forcar or is_ciclo_outdated(hours=8)
        
        if not precisa_atualizar:
            # Dados ainda válidos, usa cache
            dados_cache = get_dados_ciclo()
            
            logging.info("Bloco ciclo: Usando dados do cache PostgreSQL")
            
            resultado["blocos_processados"]["ciclo"] = {
                "atualizado": False,
                "motivo": "cache_valido",
                "fonte": dados_cache.get("fonte") if dados_cache else "PostgreSQL",
                "timestamp_dados": dados_cache.get("timestamp").isoformat() if dados_cache and dados_cache.get("timestamp") else None,
                "timestamp_processamento": datetime.utcnow().isoformat() + "Z"
            }
            
            resultado["dados_brutos"]["ciclo"] = {
                "mvrv_z_score": dados_cache.get("mvrv_z_score") if dados_cache else None,
                "realized_ratio": dados_cache.get("realized_ratio") if dados_cache else None,
                "puell_multiple": dados_cache.get("puell_multiple") if dados_cache else None
            }
            
            resultado["resumo"]["blocos_cache"] += 1
            
        else:
            # Precisa atualizar - busca do Notion
            logging.info("Bloco ciclo: Buscando dados atualizados do Notion")
            
            try:
                sucesso = update_ciclo_from_notion()
                
                if not sucesso:
                    raise Exception("Falha ao atualizar dados do Notion")
                
                # Busca dados recém-salvos
                dados_atualizados = get_dados_ciclo()
                
                if not dados_atualizados:
                    raise Exception("Dados não foram salvos corretamente no PostgreSQL")
                
                resultado["blocos_processados"]["ciclo"] = {
                    "atualizado": True,
                    "motivo": "forcado" if forcar else "cache_expirado",
                    "fonte": "Notion",
                    "timestamp_dados": dados_atualizados.get("timestamp").isoformat() if dados_atualizados.get("timestamp") else None,
                    "timestamp_processamento": datetime.utcnow().isoformat() + "Z"
                }
                
                resultado["dados_brutos"]["ciclo"] = {
                    "mvrv_z_score": dados_atualizados.get("mvrv_z_score"),
                    "realized_ratio": dados_atualizados.get("realized_ratio"),
                    "puell_multiple": dados_atualizados.get("puell_multiple")
                }
                
                resultado["resumo"]["blocos_atualizados"] += 1
                
            except Exception as update_error:
                # Erro na atualização, tenta usar dados existentes
                logging.error(f"Erro ao atualizar bloco ciclo: {str(update_error)}")
                
                dados_fallback = get_dados_ciclo()
                
                if dados_fallback:
                    logging.warning("Usando dados existentes devido ao erro na atualização")
                    
                    resultado["blocos_processados"]["ciclo"] = {
                        "atualizado": False,
                        "motivo": "erro_com_fallback",
                        "fonte": dados_fallback.get("fonte"),
                        "timestamp_dados": dados_fallback.get("timestamp").isoformat() if dados_fallback.get("timestamp") else None,
                        "erro": str(update_error),
                        "timestamp_erro": datetime.utcnow().isoformat() + "Z"
                    }
                    
                    resultado["dados_brutos"]["ciclo"] = {
                        "mvrv_z_score": dados_fallback.get("mvrv_z_score"),
                        "realized_ratio": dados_fallback.get("realized_ratio"),
                        "puell_multiple": dados_fallback.get("puell_multiple")
                    }
                    
                    resultado["resumo"]["blocos_erro"] += 1
                else:
                    # Sem dados para fallback
                    raise update_error
        
        resultado["resumo"]["total_blocos"] += 1
        logging.info("Bloco ciclo processado com sucesso")
        
    except Exception as e:
        # Erro crítico no bloco ciclo
        logging.error(f"Erro crítico ao processar bloco ciclo: {str(e)}")
        
        resultado["blocos_processados"]["ciclo"] = {
            "atualizado": False,
            "motivo": "erro_critico",
            "erro": str(e),
            "tipo_erro": type(e).__name__,
            "timestamp_erro": datetime.utcnow().isoformat() + "Z"
        }
        
        resultado["dados_brutos"]["ciclo"] = None
        resultado["resumo"]["total_blocos"] += 1
        resultado["resumo"]["blocos_erro"] += 1
    
    # Se o único bloco falhou completamente, retorna erro HTTP
    if resultado["resumo"]["blocos_erro"] == resultado["resumo"]["total_blocos"] and resultado["dados_brutos"]["ciclo"] is None:
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Falha ao obter dados do bloco ciclo",
                "detalhes": resultado
            }
        )
    
    return resultado

@router.get("/debug-import", 
            summary="Debug Import Ciclo", 
            tags=["Debug"])
def debug_import():
    """Endpoint para debugar imports"""
    try:
        from app.services.utils.postgres_helper import get_dados_ciclo
        from app.services.integracao.notion_ciclo_reader import update_ciclo_from_notion
        
        return {
            "status": "sucesso",
            "imports": {
                "postgres_helper": "OK",
                "notion_ciclo_reader": "OK"
            },
            "dados_teste": get_dados_ciclo() is not None
        }
    except Exception as e:
        return {
            "status": "erro",
            "erro": str(e),
            "tipo": type(e).__name__
        }