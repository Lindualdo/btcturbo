# app/services/utils/helpers/notion_helper.py - v5.1.3 NUPL SIMPLIFICADO

from datetime import datetime
from notion_client import Client
from typing import Dict
from app.config import get_settings
import logging

logger = logging.getLogger(__name__)

def get_ciclo_data_from_notion() -> Dict:
    """Busca dados do bloco CICLO do Notion Database"""
    try:
        settings = get_settings()
        notion = Client(auth=settings.NOTION_TOKEN)
        database_id = settings.NOTION_DATABASE_ID.strip().replace('"', '')
        
        logger.info(f"🔗 Conectando ao Notion Database: {database_id}")
        
        # Buscar dados da database
        response = notion.databases.query(database_id=database_id)
        
        # Inicializar dados padrão
        dados_ciclo = {
            "mvrv_z_score": None,
            "realized_ratio": None,
            "puell_multiple": None,
            "nupl": None,
            "fonte": "Notion",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Mapeamento SIMPLIFICADO
        indicador_map = {
            # MVRV Z-Score
            "mvrv_z_score": "mvrv_z_score",      
            "mvrv_z-score": "mvrv_z_score",
            "mvrv": "mvrv_z_score",
            
            # Realized Ratio
            "realized_ratio": "realized_ratio",   
            "realized": "realized_ratio",
            
            # Puell Multiple
            "puell_multiple": "puell_multiple",
            "puell": "puell_multiple",
            
            # NUPL - apenas variações principais
            "nupl": "nupl",
            "net_unrealized_profit_loss": "nupl"
        }
        
        logger.info(f"📊 Processando {len(response['results'])} registros do Notion...")
        
        for row in response["results"]:
            try:
                props = row["properties"]
                
                # MÉTODO 1: Buscar campo "indicador"
                indicador_titulo = None
                possible_indicator_fields = ["indicador", "Indicador", "indicator", "name", "Name"]
                
                for field_name in possible_indicator_fields:
                    if field_name in props:
                        prop_data = props[field_name]
                        if prop_data.get("title"):
                            indicador_titulo = prop_data["title"][0]["plain_text"].strip()
                            break
                        elif prop_data.get("rich_text"):
                            indicador_titulo = prop_data["rich_text"][0]["plain_text"].strip()
                            break
                
                # MÉTODO 2: Buscar campo "valor"
                valor = None
                possible_value_fields = ["valor", "value", "valor_coleta", "number"]
                
                for field_name in possible_value_fields:
                    if field_name in props and props[field_name].get("number") is not None:
                        valor = props[field_name]["number"]
                        break
                
                # MÉTODO 3: Mapeamento direto pelos campos
                if not indicador_titulo:
                    for campo_postgres, campo_notion in indicador_map.items():
                        if campo_notion in props and props[campo_notion].get("number") is not None:
                            valor_direto = props[campo_notion]["number"]
                            dados_ciclo[campo_postgres] = float(valor_direto)
                            logger.info(f"✅ Mapeamento direto: {campo_postgres} = {valor_direto}")
                
                # Mapear indicador se encontrado
                if indicador_titulo and valor is not None:
                    indicador_key = indicador_titulo.lower().strip()
                    
                    if indicador_key in indicador_map:
                        campo_destino = indicador_map[indicador_key]
                        dados_ciclo[campo_destino] = float(valor)
                        logger.info(f"✅ {indicador_titulo}: {valor}")
                    else:
                        logger.warning(f"⚠️ Indicador não mapeado: '{indicador_titulo}'")
                
            except Exception as e:
                logger.error(f"❌ Erro processando linha: {str(e)}")
                continue
        
        # Validar se pelo menos um indicador foi encontrado
        indicadores_encontrados = [k for k, v in dados_ciclo.items() 
                                 if k not in ["fonte", "timestamp"] and v is not None]
        
        if not indicadores_encontrados:
            logger.warning("⚠️ Nenhum indicador válido encontrado no Notion")
            return None
        
        logger.info(f"✅ Dados coletados do Notion: {indicadores_encontrados}")
        return dados_ciclo
        
    except Exception as e:
        logger.error(f"❌ Erro na conexão com Notion: {str(e)}")
        return None

def get_momentum_data_from_notion() -> Dict:
    """Busca dados do bloco MOMENTUM do Notion Database"""
    try:
        settings = get_settings()
        notion = Client(auth=settings.NOTION_TOKEN)
        database_id = settings.NOTION_DATABASE_ID.strip().replace('"', '')
        
        logger.info(f"🔗 Conectando ao Notion Database para MOMENTUM: {database_id}")
        
        # Buscar dados da database
        response = notion.databases.query(database_id=database_id)
        
        # Inicializar dados padrão
        dados_momentum = {
            "rsi_semanal": None,
            "funding_rates": None,
            "exchange_netflow": None,
            "long_short_ratio": None,
            "sopr": None,
            "fonte": "Notion",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Mapeamento FLEXÍVEL
        indicador_map = {
            # Indicadores existentes
            "rsi_semanal": "rsi_semanal",      
            "funding_rates": "funding_rates",   
            "exchange_netflow": "exchange_netflow",
            "long_short_ratio": "long_short_ratio",
            
            # SOPR
            "sopr": "sopr",
            "spent_output_profit_ratio": "sopr",
            
            # Variações
            "rsi": "rsi_semanal",
            "funding": "funding_rates",
            "netflow": "exchange_netflow",
            "long_short": "long_short_ratio"
        }
        
        logger.info(f"📊 Processando {len(response['results'])} registros do Notion...")
        
        for row in response["results"]:
            try:
                props = row["properties"]
                
                # MÉTODO 1: Buscar campo "indicador"
                indicador_titulo = None
                possible_indicator_fields = ["indicador", "Indicador", "indicator", "name", "Name"]
                
                for field_name in possible_indicator_fields:
                    if field_name in props:
                        prop_data = props[field_name]
                        if prop_data.get("title"):
                            indicador_titulo = prop_data["title"][0]["plain_text"].strip()
                            break
                        elif prop_data.get("rich_text"):
                            indicador_titulo = prop_data["rich_text"][0]["plain_text"].strip()
                            break
                
                # MÉTODO 2: Buscar campo "valor"
                valor = None
                possible_value_fields = ["valor", "value", "valor_coleta", "number"]
                
                for field_name in possible_value_fields:
                    if field_name in props and props[field_name].get("number") is not None:
                        valor = props[field_name]["number"]
                        break
                
                # MÉTODO 3: Mapeamento direto pelos campos
                if not indicador_titulo:
                    for campo_postgres, campo_notion in indicador_map.items():
                        if campo_notion in props and props[campo_notion].get("number") is not None:
                            valor_direto = props[campo_notion]["number"]
                            dados_momentum[campo_postgres] = float(valor_direto)
                            logger.info(f"✅ Mapeamento direto: {campo_postgres} = {valor_direto}")
                
                # Mapear indicador se encontrado
                if indicador_titulo and valor is not None:
                    indicador_key = indicador_titulo.lower().strip()
                    
                    if indicador_key in indicador_map:
                        campo_destino = indicador_map[indicador_key]
                        dados_momentum[campo_destino] = float(valor)
                        logger.info(f"✅ {indicador_titulo}: {valor}")
                    else:
                        logger.warning(f"⚠️ Indicador não mapeado: '{indicador_titulo}'")
                
            except Exception as e:
                logger.error(f"❌ Erro processando linha: {str(e)}")
                continue
        
        # Validar se pelo menos um indicador foi encontrado
        indicadores_encontrados = [k for k, v in dados_momentum.items() 
                                 if k not in ["fonte", "timestamp"] and v is not None]
        
        if not indicadores_encontrados:
            logger.warning("⚠️ Nenhum indicador válido encontrado no Notion para MOMENTUM")
            return None
        
        logger.info(f"✅ Dados MOMENTUM coletados do Notion: {indicadores_encontrados}")
        return dados_momentum
        
    except Exception as e:
        logger.error(f"❌ Erro na conexão com Notion para MOMENTUM: {str(e)}")
        return None