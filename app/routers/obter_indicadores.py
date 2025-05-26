# app/routers/obter_indicadores.py - VERSÃO CORRIGIDA

from fastapi import APIRouter, Query, HTTPException
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import json
import logging
import traceback

# Imports específicos do projeto
try:
    from app.config import get_settings
except ImportError:
    logger.warning("Erro ao importar get_settings")

try:
    from app.dependencies import get_notion_client
except ImportError:
    logger.warning("Erro ao importar get_notion_client")

try:
    from app.db.database import get_db_session
except ImportError:
    logger.warning("Erro ao importar get_db_session")

# Se não tiver notion_client, criar fallback
try:
    from notion_client import Client as NotionClient
except ImportError:
    logger.warning("Notion client não disponível")

router = APIRouter()

# Configurar logger
logger = logging.getLogger(__name__)

# Configuração do cache (8 horas)
CACHE_EXPIRATION_HOURS = 8

@router.get("/obter-indicadores")
def obter_indicadores(
    forcar: Optional[bool] = Query(False, description="Forçar atualização dos dados"),
    bloco: Optional[str] = Query("ciclo", description="Bloco específico ou 'todos'")
):
    """
    Obtém indicadores com gestão de cache automática
    """
    try:
        logger.info(f"Iniciando obter_indicadores - forcar={forcar}, bloco={bloco}")
        
        timestamp_inicio = datetime.utcnow()
        blocos_processados = {}
        dados_brutos = {}
        resumo = {
            "total_blocos": 0,
            "blocos_atualizados": 0,
            "blocos_cache": 0,
            "blocos_erro": 0
        }
        
        # Definir blocos a processar
        if bloco == "todos":
            blocos_lista = ["ciclo", "riscos", "tecnica", "momentum"]
        else:
            blocos_lista = [bloco]
            
        resumo["total_blocos"] = len(blocos_lista)
        
        # Processar cada bloco
        for bloco_nome in blocos_lista:
            logger.info(f"Processando bloco: {bloco_nome}")
            
            try:
                # Verificar cache ou forçar atualização
                if forcar or is_bloco_outdated(bloco_nome):
                    logger.info(f"Atualizando dados do bloco {bloco_nome}")
                    resultado = atualizar_bloco(bloco_nome)
                    
                    if resultado["sucesso"]:
                        blocos_processados[bloco_nome] = {
                            "atualizado": True,
                            "motivo": "forcado" if forcar else "cache_expirado",
                            "fonte": resultado["fonte"],
                            "timestamp_dados": resultado["timestamp"],
                            "timestamp_processamento": datetime.utcnow().isoformat()
                        }
                        dados_brutos[bloco_nome] = resultado["dados"]
                        resumo["blocos_atualizados"] += 1
                    else:
                        # Erro na atualização, usar fallback
                        blocos_processados[bloco_nome] = {
                            "atualizado": False,
                            "motivo": "erro_com_fallback",
                            "fonte": resultado["fonte"],
                            "timestamp_dados": resultado.get("timestamp_fallback"),
                            "erro": resultado["erro"],
                            "timestamp_erro": datetime.utcnow().isoformat()
                        }
                        dados_brutos[bloco_nome] = resultado.get("dados_fallback", {})
                        resumo["blocos_erro"] += 1
                        
                else:
                    # Usar dados do cache
                    logger.info(f"Usando cache para bloco {bloco_nome}")
                    dados_cache = get_dados_cache(bloco_nome)
                    
                    blocos_processados[bloco_nome] = {
                        "atualizado": False,
                        "motivo": "cache_valido",
                        "fonte": dados_cache["fonte"],
                        "timestamp_dados": dados_cache["timestamp"],
                        "timestamp_processamento": datetime.utcnow().isoformat()
                    }
                    dados_brutos[bloco_nome] = dados_cache["dados"]
                    resumo["blocos_cache"] += 1
                    
            except Exception as e:
                logger.error(f"Erro geral no bloco {bloco_nome}: {str(e)}")
                blocos_processados[bloco_nome] = {
                    "atualizado": False,
                    "motivo": "erro_critico",
                    "erro": str(e),
                    "timestamp_erro": datetime.utcnow().isoformat()
                }
                resumo["blocos_erro"] += 1
        
        # Resposta consolidada
        return {
            "timestamp": timestamp_inicio.isoformat() + "Z",
            "parametro_forcar": forcar,
            "blocos_processados": blocos_processados,
            "dados_brutos": dados_brutos,
            "resumo": resumo
        }
        
    except Exception as e:
        logger.error(f"Erro crítico em obter_indicadores: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500, 
            detail=f"Erro interno do servidor: {str(e)}"
        )


def is_bloco_outdated(bloco: str) -> bool:
    """
    Verifica se os dados do bloco estão desatualizados (> 8h)
    """
    try:
        # Simulação - substitua pela implementação real do banco
        logger.info(f"Verificando cache do bloco {bloco}")
        
        # Por enquanto, sempre retorna True para forçar atualização em desenvolvimento
        # TODO: Implementar verificação real do PostgreSQL
        return True
        
    except Exception as e:
        logger.error(f"Erro ao verificar cache do bloco {bloco}: {str(e)}")
        return True  # Se há erro, forçar atualização


def get_dados_cache(bloco: str) -> Dict[str, Any]:
    """
    Recupera dados do cache (PostgreSQL)
    """
    try:
        logger.info(f"Recuperando dados do cache para bloco {bloco}")
        
        # Simulação - substitua pela implementação real do banco
        # TODO: Implementar busca real no PostgreSQL
        return {
            "dados": {},
            "fonte": "cache_simulado",
            "timestamp": datetime.utcnow().isoformat()
        }
                
    except Exception as e:
        logger.error(f"Erro ao recuperar cache do bloco {bloco}: {str(e)}")
        return {
            "dados": {},
            "fonte": "cache_erro",
            "timestamp": datetime.utcnow().isoformat()
        }


def atualizar_bloco(bloco: str) -> Dict[str, Any]:
    """
    Atualiza dados do bloco buscando nas fontes externas
    """
    logger.info(f"=== INICIANDO ATUALIZAR_BLOCO ===")
    logger.info(f"Bloco solicitado: {bloco}")
    
    try:
        logger.info(f"Iniciando atualização do bloco {bloco}")
        
        # Coletar dados das fontes externas
        logger.info("Determinando função de coleta baseada no bloco...")
        
        if bloco == "ciclo":
            logger.info("Chamando coletar_dados_ciclo()...")
            dados_novos = coletar_dados_ciclo()
            logger.info(f"Dados coletados do ciclo: {dados_novos}")
        elif bloco == "riscos":
            logger.info("Chamando coletar_dados_riscos()...")
            dados_novos = coletar_dados_riscos()
        elif bloco == "tecnica":
            logger.info("Chamando coletar_dados_tecnica()...")
            dados_novos = coletar_dados_tecnica()
        elif bloco == "momentum":
            logger.info("Chamando coletar_dados_momentum()...")
            dados_novos = coletar_dados_momentum()
        else:
            logger.error(f"Bloco desconhecido recebido: {bloco}")
            raise ValueError(f"Bloco desconhecido: {bloco}")
            
        logger.info(f"Coleta de dados externa concluída para bloco {bloco}")
        logger.info(f"Quantidade de indicadores coletados: {len(dados_novos)}")
        logger.info(f"Indicadores: {list(dados_novos.keys())}")
        
        # Preparar timestamp
        timestamp_dados = datetime.utcnow().isoformat()
        logger.info(f"Timestamp dos dados: {timestamp_dados}")
        
        # Tentar salvar no PostgreSQL
        logger.info("=== INICIANDO TENTATIVA DE SAVE NO POSTGRESQL ===")
        
        try:
            save_to_database(bloco, dados_novos, timestamp_dados)
            logger.info(f"✅ Dados do bloco {bloco} salvos com sucesso no PostgreSQL")
            
            return {
                "sucesso": True,
                "dados": dados_novos,
                "fonte": "API_Externa",
                "timestamp": timestamp_dados
            }
            
        except Exception as save_error:
            logger.error(f"=== ERRO NO SAVE - INICIANDO FALLBACK ===")
            logger.error(f"Erro ao salvar dados do bloco {bloco}: {str(save_error)}")
            logger.error(f"Tipo do erro de save: {type(save_error).__name__}")
            logger.warning("Usando dados existentes devido ao erro na atualização")
            
            # Buscar dados existentes como fallback
            logger.info("Buscando dados do cache como fallback...")
            dados_fallback = get_dados_cache(bloco)
            logger.info(f"Dados de fallback obtidos: {dados_fallback}")
            
            return {
                "sucesso": False,
                "erro": "Falha ao salvar no PostgreSQL",
                "dados_fallback": dados_novos,  # Dados coletados (mesmo que não salvos)
                "fonte": "API_Externa",
                "timestamp_fallback": dados_fallback.get("timestamp"),
                "detalhes_erro": str(save_error)
            }
            
    except Exception as e:
        logger.error(f"=== ERRO GERAL EM ATUALIZAR_BLOCO ===")
        logger.error(f"Erro ao atualizar bloco {bloco}: {str(e)}")
        logger.error(f"Tipo do erro: {type(e).__name__}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        return {
            "sucesso": False,
            "erro": f"Falha na coleta de dados: {str(e)}",
            "fonte": "erro",
            "timestamp": datetime.utcnow().isoformat()
        }


def save_to_database(bloco: str, dados: Dict[str, Any], timestamp: str):
    """
    CORREÇÃO: Salva dados no PostgreSQL convertendo dict para JSON
    """
    logger.info(f"=== INICIANDO SAVE_TO_DATABASE ===")
    logger.info(f"Bloco: {bloco}")
    logger.info(f"Timestamp: {timestamp}")
    logger.info(f"Dados recebidos: {dados}")
    logger.info(f"Tipo dos dados: {type(dados)}")
    
    try:
        # ✅ CORREÇÃO: Converter dict para JSON string
        logger.info("Convertendo dados para JSON string...")
        dados_json = json.dumps(dados, ensure_ascii=False, default=str)
        logger.info(f"Dados convertidos para JSON: {dados_json}")
        logger.info(f"Tamanho do JSON: {len(dados_json)} caracteres")
        
        # TODO: Implementar save real no PostgreSQL
        logger.info("SIMULANDO save no PostgreSQL...")
        logger.info(f"✅ Dados do bloco {bloco} 'salvos' com sucesso (simulado)")
        
        # Remover este comentário quando implementar conexão real:
        # with get_db_session() as db:
        #     query = """
        #         INSERT INTO indicadores (bloco, dados_json, fonte, timestamp_dados, created_at)
        #         VALUES (%s, %s, %s, %s, %s)
        #         ON CONFLICT (bloco, timestamp_dados) 
        #         DO UPDATE SET 
        #             dados_json = EXCLUDED.dados_json,
        #             fonte = EXCLUDED.fonte,
        #             updated_at = CURRENT_TIMESTAMP
        #     """
        #     parametros = [bloco, dados_json, "API_Externa", timestamp, datetime.utcnow()]
        #     result = db.execute(query, parametros)
        #     db.commit()
            
    except Exception as e:
        logger.error(f"❌ ERRO DETALHADO ao salvar no PostgreSQL:")
        logger.error(f"   - Bloco: {bloco}")
        logger.error(f"   - Timestamp: {timestamp}")
        logger.error(f"   - Dados originais: {dados}")
        logger.error(f"   - Tipo do erro: {type(e).__name__}")
        logger.error(f"   - Mensagem do erro: {str(e)}")
        logger.error(f"   - Traceback completo: {traceback.format_exc()}")
        raise e


def coletar_dados_ciclo() -> Dict[str, Any]:
    """
    Coleta dados específicos do bloco Ciclo
    """
    logger.info(f"=== INICIANDO COLETAR_DADOS_CICLO ===")
    
    try:
        logger.info("Obtendo configurações do sistema...")
        
        # Verificar se get_settings está disponível
        try:
            settings = get_settings()
            database_id = settings.NOTION_DATABASE_ID
            logger.info(f"Database ID do Notion: {database_id}")
        except Exception as e:
            logger.error(f"Erro ao obter settings: {e}")
            raise ValueError("Configurações não disponíveis")
        
        logger.info("Obtendo cliente do Notion...")
        
        # Verificar se get_notion_client está disponível
        try:
            notion = get_notion_client()
            logger.info("Cliente do Notion obtido com sucesso")
        except Exception as e:
            logger.error(f"Erro ao obter cliente Notion: {e}")
            raise ValueError("Cliente Notion não disponível")
        
        # Query no Notion para dados do ciclo
        logger.info("Preparando query para o Notion...")
        filtro = {
            "property": "Bloco",
            "select": {"equals": "Ciclo"}
        }
        logger.info(f"Filtro da query: {filtro}")
        
        logger.info("Executando query no banco Notion...")
        response = notion.databases.query(
            database_id=database_id,
            filter=filtro
        )
        logger.info(f"Query executada - Resposta recebida")
        logger.info(f"Número de resultados: {len(response.get('results', []))}")
        
        # Processar dados do Notion
        logger.info("Iniciando processamento dos dados do Notion...")
        dados_processados = {}
        
        for i, item in enumerate(response.get("results", [])):
            logger.info(f"--- Processando item {i+1} ---")
            properties = item.get("properties", {})
            logger.info(f"Propriedades disponíveis: {list(properties.keys())}")
            
            # Extrair indicadores específicos
            if "Indicador" in properties:
                indicador_prop = properties["Indicador"]
                logger.info(f"Propriedade Indicador: {indicador_prop}")
                
                if indicador_prop.get("title") and len(indicador_prop["title"]) > 0:
                    indicador = indicador_prop["title"][0]["text"]["content"]
                    logger.info(f"Nome do indicador: {indicador}")
                    
                    if "Valor" in properties:
                        valor_prop = properties["Valor"]
                        logger.info(f"Propriedade Valor: {valor_prop}")
                        
                        if valor_prop.get("number") is not None:
                            valor = valor_prop["number"]
                            logger.info(f"Valor numérico: {valor} (tipo: {type(valor)})")
                            
                            # Mapear indicadores
                            if "MVRV" in indicador:
                                dados_processados["mvrv_z_score"] = valor
                                logger.info(f"✅ MVRV Z-Score mapeado: {valor}")
                            elif "Realized" in indicador:
                                dados_processados["realized_ratio"] = valor
                                logger.info(f"✅ Realized Ratio mapeado: {valor}")
                            elif "Puell" in indicador:
                                dados_processados["puell_multiple"] = valor
                                logger.info(f"✅ Puell Multiple mapeado: {valor}")
                            else:
                                logger.warning(f"⚠️ Indicador não reconhecido: {indicador}")
                        else:
                            logger.warning(f"⚠️ Valor nulo para indicador: {indicador}")
                    else:
                        logger.warning(f"⚠️ Propriedade 'Valor' não encontrada para: {indicador}")
                else:
                    logger.warning(f"⚠️ Título do indicador vazio no item {i+1}")
            else:
                logger.warning(f"⚠️ Propriedade 'Indicador' não encontrada no item {i+1}")
        
        logger.info(f"=== PROCESSAMENTO CONCLUÍDO ===")
        logger.info(f"Dados processados finais: {dados_processados}")
        logger.info(f"Total de indicadores coletados: {len(dados_processados)}")
        
        if not dados_processados:
            logger.error("❌ ERRO: Nenhum dado válido retornado do Notion")
            raise ValueError("Nenhum dado válido retornado do Notion")
            
        logger.info("✅ Coleta do Notion concluída com sucesso")
        return dados_processados
        
    except Exception as e:
        logger.error(f"=== ERRO EM COLETAR_DADOS_CICLO ===")
        logger.error(f"Tipo do erro: {type(e).__name__}")
        logger.error(f"Mensagem: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise e  # Re-raise o erro ao invés de retornar dados fake


def coletar_dados_riscos() -> Dict[str, Any]:
    """
    Coleta dados específicos do bloco Riscos
    IMPLEMENTAR: Conexões com APIs externas reais
    """
    raise NotImplementedError("Função coletar_dados_riscos ainda não implementada")


def coletar_dados_tecnica() -> Dict[str, Any]:
    """
    Coleta dados específicos do bloco Técnica  
    IMPLEMENTAR: TradingView, análise técnica
    """
    raise NotImplementedError("Função coletar_dados_tecnica ainda não implementada")


def coletar_dados_momentum() -> Dict[str, Any]:
    """
    Coleta dados específicos do bloco Momentum
    IMPLEMENTAR: APIs de funding rates, OI, etc.
    """
    raise NotImplementedError("Função coletar_dados_momentum ainda não implementada")   