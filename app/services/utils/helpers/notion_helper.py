# app/services/utils/helpers/notion_helper.py - CORRIGIDO

from datetime import datetime
from notion_client import Client
from typing import Dict
from app.config import get_settings
import logging

logger = logging.getLogger(__name__)

def get_ciclo_data_from_notion() -> Dict:
    """
    Busca dados do bloco CICLO do Notion Database
    Mapeamento correto baseado na confirmação do usuário
    """
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
            "fonte": "Notion",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Mapeamento FLEXÍVEL - adaptar conforme estrutura real
        # Se os campos no Notion são diretamente os nomes dos indicadores:
        indicador_map = {
            "mvrv_z_score": "mvrv_z_score",      
            "realized_ratio": "realized_ratio",   
            "puell_multiple": "puell_multiple",
            # Variações possíveis
            "mvrv_z-score": "mvrv_z_score",
            "mvrv": "mvrv_z_score",
            "realized": "realized_ratio",
            "puell": "puell_multiple"
        }
        
        logger.info(f"📊 Processando {len(response['results'])} registros do Notion...")
        
        # DEBUG: Verificar estrutura da primeira linha
        if response["results"]:
            first_row = response["results"][0]
            logger.info(f"🔍 DEBUG - Campos disponíveis: {list(first_row['properties'].keys())}")
        
        for row in response["results"]:
            try:
                props = row["properties"]
                
                # MÉTODO 1: Buscar campo "indicador" (várias variações)
                indicador_titulo = None
                possible_indicator_fields = ["indicador", "Indicador", "indicator", "name", "Name"]
                
                for field_name in possible_indicator_fields:
                    if field_name in props:
                        prop_data = props[field_name]
                        if prop_data.get("title"):
                            indicador_titulo = prop_data["title"][0]["plain_text"].strip()
                            logger.info(f"📌 Campo indicador encontrado: '{field_name}' = '{indicador_titulo}'")
                            break
                        elif prop_data.get("rich_text"):
                            indicador_titulo = prop_data["rich_text"][0]["plain_text"].strip()
                            logger.info(f"📌 Campo indicador encontrado: '{field_name}' = '{indicador_titulo}'")
                            break
                
                # MÉTODO 2: Buscar campo "valor" (várias variações)
                valor = None
                possible_value_fields = ["valor", "value", "valor_coleta", "number"]
                
                for field_name in possible_value_fields:
                    if field_name in props and props[field_name].get("number") is not None:
                        valor = props[field_name]["number"]
                        logger.info(f"💰 Campo valor encontrado: '{field_name}' = {valor}")
                        break
                
                # MÉTODO 3: Se não encontrou indicador, tentar mapear direto pelos campos
                if not indicador_titulo:
                    # Buscar diretamente campos conhecidos
                    for campo_postgres, campo_notion in indicador_map.items():
                        if campo_notion in props and props[campo_notion].get("number") is not None:
                            valor_direto = props[campo_notion]["number"]
                            dados_ciclo[campo_postgres] = float(valor_direto)
                            logger.info(f"✅ Mapeamento direto: {campo_postgres} = {valor_direto}")
                
                # Mapear indicador se encontrado via método 1
                if indicador_titulo and valor is not None:
                    indicador_key = indicador_titulo.lower().strip()
                    
                    if indicador_key in indicador_map:
                        dados_ciclo[indicador_map[indicador_key]] = float(valor)
                        logger.info(f"✅ {indicador_titulo}: {valor}")
                    else:
                        logger.warning(f"⚠️ Indicador não mapeado: '{indicador_titulo}' (disponível: {list(indicador_map.keys())})")
                
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