# app/services/utils/helpers/notion_helper.py - COMPLETO SIMPLIFICADO

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
        
        # Dados padrão
        dados_ciclo = {
            "mvrv_z_score": None,
            "realized_ratio": None,
            "puell_multiple": None,
            "nupl": None,
            "fonte": "Notion",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"📊 Processando {len(response['results'])} registros para CICLO...")
        
        # LÓGICA SIMPLES: Para cada row, pegar indicador + valor + bloco
        for row in response["results"]:
            props = row.get("properties", {})
            
            # Pegar nome do indicador
            indicador_nome = None
            if "indicador" in props and props["indicador"].get("title"):
                indicador_nome = props["indicador"]["title"][0]["plain_text"].strip()
            
            # Pegar valor
            valor = None
            if "valor" in props and props["valor"].get("number") is not None:
                valor = props["valor"]["number"]
            
            # Pegar bloco (para filtrar só os de ciclo)
            bloco = None
            if "bloco" in props and props["bloco"].get("select"):
                bloco = props["bloco"]["select"]["name"].strip()
            
            # Se temos indicador + valor + bloco correto, mapear
            if indicador_nome and valor is not None and bloco == "ciclo":
                indicador_lower = indicador_nome.lower().strip()
                
                # MAPEAMENTO DIRETO CICLO
                if indicador_lower == "mvrv_z_score":
                    dados_ciclo["mvrv_z_score"] = float(valor)
                elif indicador_lower == "realized_ratio":
                    dados_ciclo["realized_ratio"] = float(valor)
                elif indicador_lower == "puell_multiple":
                    dados_ciclo["puell_multiple"] = float(valor)
                elif indicador_lower == "nupl":
                    dados_ciclo["nupl"] = float(valor)
                    logger.info(f"✅ NUPL encontrado: {valor}")
                
                logger.info(f"📈 CICLO - {indicador_nome}: {valor}")
        
        # Verificar se encontrou dados
        indicadores_encontrados = [k for k, v in dados_ciclo.items() 
                                 if k not in ["fonte", "timestamp"] and v is not None]
        
        if not indicadores_encontrados:
            logger.error("❌ Nenhum indicador de CICLO encontrado!")
            return None
        
        logger.info(f"✅ Indicadores CICLO coletados: {indicadores_encontrados}")
        return dados_ciclo
        
    except Exception as e:
        logger.error(f"❌ Erro na conexão com Notion (CICLO): {str(e)}")
        return None

def get_momentum_data_from_notion() -> Dict:
    """Busca dados do bloco MOMENTUM do Notion Database"""
    try:
        settings = get_settings()
        notion = Client(auth=settings.NOTION_TOKEN)
        database_id = settings.NOTION_DATABASE_ID.strip().replace('"', '')
        
        logger.info(f"🔗 Conectando ao Notion Database: {database_id}")
        
        # Buscar dados da database
        response = notion.databases.query(database_id=database_id)
        
        # Dados padrão
        dados_momentum = {
            "rsi_semanal": None,
            "funding_rates": None,
            "exchange_netflow": None,
            "long_short_ratio": None,
            "sopr": None,
            "fonte": "Notion",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"📊 Processando {len(response['results'])} registros para MOMENTUM...")
        
        # LÓGICA SIMPLES: Para cada row, pegar indicador + valor + bloco
        for row in response["results"]:
            props = row.get("properties", {})
            
            # Pegar nome do indicador
            indicador_nome = None
            if "indicador" in props and props["indicador"].get("title"):
                indicador_nome = props["indicador"]["title"][0]["plain_text"].strip()
            
            # Pegar valor
            valor = None
            if "valor" in props and props["valor"].get("number") is not None:
                valor = props["valor"]["number"]
            
            # Pegar bloco (para filtrar só os de momentum)
            bloco = None
            if "bloco" in props and props["bloco"].get("select"):
                bloco = props["bloco"]["select"]["name"].strip()
            
            # Se temos indicador + valor + bloco correto, mapear
            if indicador_nome and valor is not None and bloco == "momentum":
                indicador_lower = indicador_nome.lower().strip()
                
                # MAPEAMENTO DIRETO MOMENTUM
                if indicador_lower == "rsi_semanal":
                    dados_momentum["rsi_semanal"] = float(valor)
                elif indicador_lower == "funding_rates":
                    dados_momentum["funding_rates"] = float(valor)
                elif indicador_lower == "exchange_netflow":
                    dados_momentum["exchange_netflow"] = float(valor)
                elif indicador_lower == "long_short_ratio":
                    dados_momentum["long_short_ratio"] = float(valor)
                elif indicador_lower == "sopr":
                    dados_momentum["sopr"] = float(valor)
                    logger.info(f"✅ SOPR encontrado: {valor}")
                
                logger.info(f"📈 MOMENTUM - {indicador_nome}: {valor}")
        
        # Verificar se encontrou dados
        indicadores_encontrados = [k for k, v in dados_momentum.items() 
                                 if k not in ["fonte", "timestamp"] and v is not None]
        
        if not indicadores_encontrados:
            logger.error("❌ Nenhum indicador de MOMENTUM encontrado!")
            return None
        
        logger.info(f"✅ Indicadores MOMENTUM coletados: {indicadores_encontrados}")
        return dados_momentum
        
    except Exception as e:
        logger.error(f"❌ Erro na conexão com Notion (MOMENTUM): {str(e)}")
        return None