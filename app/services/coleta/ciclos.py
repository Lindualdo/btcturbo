# app/services/coleta/ciclos.py

from datetime import datetime
import logging
from app.services.utils.helpers.notion_helper import get_ciclo_data_from_notion
from app.services.utils.helpers.postgres.ciclo_helper import insert_dados_ciclo

logger = logging.getLogger(__name__)

def coletar(forcar_coleta: bool):
    """
    Coleta dados do bloco CICLO via Notion Database e grava no PostgreSQL
    
    Args:
        forcar_coleta (bool): Se True, força nova coleta independente do cache
        
    Returns:
        dict: Status da coleta com detalhes dos dados coletados
    """
    try:
        logger.info("🔄 Iniciando coleta bloco CICLO via Notion...")
        
        # 1. Buscar dados do Notion
        logger.info("📋 Conectando ao Notion Database...")
        dados_notion = get_ciclo_data_from_notion()
        
        if not dados_notion:
            raise Exception("Nenhum dado retornado do Notion Database")
        
        # 2. Extrair indicadores necessários
        mvrv_z_score = dados_notion.get("mvrv_z_score")
        realized_ratio = dados_notion.get("realized_ratio") 
        puell_multiple = dados_notion.get("puell_multiple")
        
        # 3. Validar se todos os indicadores foram coletados
        indicadores_faltando = []
        if mvrv_z_score is None:
            indicadores_faltando.append("mvrv_z_score")
        if realized_ratio is None:
            indicadores_faltando.append("realized_ratio")
        if puell_multiple is None:
            indicadores_faltando.append("puell_multiple")
            
        if indicadores_faltando:
            logger.warning(f"⚠️ Indicadores não encontrados no Notion: {indicadores_faltando}")
            # Continua com os dados disponíveis, usando 0.0 para os faltantes
            mvrv_z_score = mvrv_z_score or 0.0
            realized_ratio = realized_ratio or 0.0
            puell_multiple = puell_multiple or 0.0
        
        # 4. Gravar dados no PostgreSQL
        logger.info("💾 Gravando dados no PostgreSQL...")
        sucesso_gravacao = insert_dados_ciclo(
            mvrv_z=float(mvrv_z_score),
            realized_ratio=float(realized_ratio), 
            puell_multiple=float(puell_multiple),
            fonte="notion"
        )
        
        if not sucesso_gravacao:
            raise Exception("Falha ao gravar dados no PostgreSQL")
        
        # 5. Preparar resposta de sucesso
        resposta_sucesso = {
            "bloco": "ciclos",
            "status": "sucesso",
            "timestamp": datetime.utcnow().isoformat(),
            "detalhes": "Dados coletados via Notion Database",
            "dados_coletados": {
                "mvrv_z_score": float(mvrv_z_score),
                "realized_ratio": float(realized_ratio),
                "puell_multiple": float(puell_multiple),
                "fonte_original": dados_notion.get("fonte", "Notion"),
                "timestamp_notion": dados_notion.get("timestamp")
            },
            "fonte": "notion",
            "indicadores_processados": 3,
            "indicadores_faltando": indicadores_faltando if indicadores_faltando else "nenhum"
        }
        
        logger.info(f"✅ Coleta CICLO concluída com sucesso - MVRV: {mvrv_z_score}, Realized: {realized_ratio}, Puell: {puell_multiple}")
        return resposta_sucesso
        
    except Exception as e:
        logger.error(f"❌ Erro na coleta CICLO via Notion: {str(e)}")
        
        resposta_erro = {
            "bloco": "ciclos", 
            "status": "erro",
            "timestamp": datetime.utcnow().isoformat(),
            "detalhes": f"Falha na coleta via Notion: {str(e)}",
            "fonte": "notion",
            "dados_coletados": None
        }
        
        return resposta_erro