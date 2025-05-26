# app/services/integracao/notion_ciclo_reader.py

import logging
from datetime import datetime
from typing import Dict, List, Optional
from notion_client import Client
from app.config import get_settings
from app.services.utils.postgres_helper import save_dados_ciclo


def update_ciclo_from_notion():
    """
    Atualiza dados do bloco ciclo no PostgreSQL com dados do Notion.
    """
    try:
        from app.services.utils.postgres_helper import save_dados_ciclo
        
        # Coleta dados do Notion
        dados_notion = get_ciclo_data_from_notion()
        
        # Salva no PostgreSQL usando as funções reais
        sucesso = save_dados_ciclo(dados_notion)
        
        if sucesso:
            logging.info("Dados do bloco ciclo atualizados com sucesso no PostgreSQL")
            return True
        else:
            raise Exception("Falha ao salvar no PostgreSQL")
            
    except Exception as e:
        logging.error(f"Erro ao atualizar bloco ciclo: {str(e)}")
        raise e


def get_ciclo_data_from_notion() -> Dict:
    """
    Lê dados do bloco ciclo da tabela tbl_ciclos no Notion.
    Baseado no padrão existente em fundamentals.py
    
    Returns:
        Dict com dados dos 3 indicadores do bloco ciclo
    """
    try:
        settings = get_settings()
        NOTION_TOKEN = settings.NOTION_TOKEN
        
        # Usar NOTION_DATABASE_ID padrão para ciclos
        DATABASE_ID = settings.NOTION_DATABASE_ID.strip().replace('"', '')
        
        if not DATABASE_ID:
            logging.error("DATABASE_ID está vazio. Verifique NOTION_DATABASE_ID no .env")
            raise ValueError("DATABASE_ID não pode ser vazio.")
            
        logging.info(f"Ciclo Data - DATABASE_ID: {DATABASE_ID}")
        notion = Client(auth=NOTION_TOKEN)
        
        response = notion.databases.query(database_id=DATABASE_ID)
        
        # Dicionário para armazenar os dados coletados
        dados_ciclo = {
            "mvrv_z_score": None,
            "realized_ratio": None, 
            "puell_multiple": None,
            "fonte": "Notion",
            "timestamp": datetime.utcnow()
        }
        
        # Processar cada linha da tabela tbl_ciclos
        for row in response["results"]:
            props = row["properties"]
            
            # Extrair nome do indicador (campo Indicador - Title)
            indicador_raw = props["Indicador"]["title"]
            if not indicador_raw:
                continue
                
            nome_indicador = indicador_raw[0]["plain_text"].strip().lower()
            
            # Extrair valor (campo valor_coleta - Number)
            valor_raw = props.get("valor_coleta", {}).get("number")
            if valor_raw is None:
                logging.warning(f"Valor não encontrado para indicador: {nome_indicador}")
                continue
                
            valor = float(valor_raw)
            
            # Extrair data de coleta (campo data_coleta - Date)
            data_coleta_raw = props.get("data_coleta", {}).get("date")
            data_coleta = None
            if data_coleta_raw:
                data_coleta = data_coleta_raw.get("start")
            
            # Extrair fonte (campo fonte - Select)
            fonte_raw = props.get("fonte", {}).get("select")
            fonte = "Manual"  # Default
            if fonte_raw:
                fonte = fonte_raw.get("name", "Manual")
            
            # Mapear indicadores para campos corretos
            if nome_indicador == "mvrv_z-score":
                dados_ciclo["mvrv_z_score"] = valor
                logging.info(f"MVRV Z-Score coletado: {valor}")
                
            elif nome_indicador == "realized_price":
                dados_ciclo["realized_ratio"] = valor
                logging.info(f"Realized Price coletado: {valor}")
                
            elif nome_indicador == "puell_multiple":
                dados_ciclo["puell_multiple"] = valor
                logging.info(f"Puell Multiple coletado: {valor}")
                
            else:
                logging.warning(f"Indicador desconhecido ignorado: {nome_indicador}")
        
        # Verificar se todos os indicadores foram encontrados
        missing_indicators = []
        for key, value in dados_ciclo.items():
            if key not in ["fonte", "timestamp"] and value is None:
                missing_indicators.append(key)
        
        if missing_indicators:
            logging.warning(f"Indicadores não encontrados: {missing_indicators}")
        
        logging.info(f"Dados coletados do Notion: {dados_ciclo}")
        return dados_ciclo
        
    except Exception as e:
        logging.error(f"Erro ao coletar dados do bloco ciclo no Notion: {str(e)}")
        raise e

def get_individual_indicator_from_notion(indicador_nome: str) -> Optional[float]:
    """
    Busca um indicador específico do Notion.
    Útil para updates individuais.
    
    Args:
        indicador_nome: Nome do indicador ("mvrv_z-score", "realized_price", "puell_multiple")
        
    Returns:
        Valor do indicador ou None se não encontrado
    """
    try:
        dados_completos = get_ciclo_data_from_notion()
        
        # Mapear nomes para campos
        mapeamento = {
            "mvrv_z-score": "mvrv_z_score",
            "realized_price": "realized_ratio",
            "puell_multiple": "puell_multiple"
        }
        
        campo = mapeamento.get(indicador_nome.lower())
        if campo:
            return dados_completos.get(campo)
        
        logging.warning(f"Indicador não mapeado: {indicador_nome}")
        return None
        
    except Exception as e:
        logging.error(f"Erro ao buscar indicador {indicador_nome}: {str(e)}")
        return None
    
    