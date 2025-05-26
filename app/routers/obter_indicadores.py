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
        "dados_brutos": {},  # ← DADOS SEMPRE RETORNADOS
        "resumo": {
            "total_blocos": 0,
            "blocos_atualizados": 0,
            "blocos_cache": 0,
            "blocos_erro": 0
        }
    }
    
    # Lista de blocos disponíveis no sistema
    blocos = [
        ("ciclo", "app.services.blocos.ciclos.update_ciclo", "update_ciclo"),
        # ("momentum", "app.services.blocos.momentum.update_momentum", "update_momentum"),  # Futuro
        # ("risco", "app.services.blocos.risco.update_risco", "update_risco"),              # Futuro
        # ("tecnico", "app.services.blocos.tecnico.update_tecnico", "update_tecnico")       # Futuro
    ]
    
    for nome_bloco, modulo_path, funcao_nome in blocos:
        try:
            # Import dinâmico do módulo do bloco
            modulo = __import__(modulo_path, fromlist=[funcao_nome])
            funcao_update = getattr(modulo, funcao_nome)
            
            # Executa obtenção/atualização do bloco
            resultado_bloco = funcao_update(forcar=forcar)
            
            # Registra status do processamento
            resultado["blocos_processados"][nome_bloco] = {
                "atualizado": resultado_bloco["atualizado"],
                "motivo": resultado_bloco["motivo"],
                "fonte": resultado_bloco.get("fonte"),
                "timestamp_dados": resultado_bloco.get("timestamp_dados"),
                "timestamp_processamento": resultado_bloco.get("timestamp_atualizacao", resultado_bloco.get("timestamp_verificacao"))
            }
            
            # SEMPRE inclui dados brutos atuais do PostgreSQL
            if resultado_bloco["dados"]:
                resultado["dados_brutos"][nome_bloco] = resultado_bloco["dados"]
            else:
                resultado["dados_brutos"][nome_bloco] = None
            
            # Atualiza contadores
            resultado["resumo"]["total_blocos"] += 1
            
            if resultado_bloco["atualizado"]:
                resultado["resumo"]["blocos_atualizados"] += 1
            elif resultado_bloco["motivo"] == "erro":
                resultado["resumo"]["blocos_erro"] += 1
            else:
                resultado["resumo"]["blocos_cache"] += 1
                
            logging.info(f"Bloco {nome_bloco} obtido com sucesso")
            
        except Exception as e:
            erro_detalhes = {
                "atualizado": False,
                "motivo": "erro_sistema",
                "erro": str(e),
                "tipo_erro": type(e).__name__,
                "timestamp_erro": datetime.utcnow().isoformat() + "Z"
            }
            
            resultado["blocos_processados"][nome_bloco] = erro_detalhes
            resultado["dados_brutos"][nome_bloco] = None  # Indica erro
            resultado["resumo"]["blocos_erro"] += 1
            
            logging.error(f"Erro ao obter bloco {nome_bloco}: {str(e)}")
    
    # Se todos os blocos falharam, retorna erro HTTP
    if resultado["resumo"]["blocos_erro"] == resultado["resumo"]["total_blocos"]:
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Falha ao obter dados de todos os blocos",
                "detalhes": resultado
            }
        )
    
    return resultado