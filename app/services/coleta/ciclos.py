# app/services/coleta/ciclos.py - v5.1.2 SIMPLIFICADO

from datetime import datetime
import logging
from app.services.utils.helpers.notion_helper import get_ciclo_data_from_notion
from app.services.utils.helpers.postgres.ciclo_helper import insert_dados_ciclo

logger = logging.getLogger(__name__)

def coletar(forcar_coleta: bool):
    """Coleta dados do bloco CICLO via Notion Database"""
    try:
        logger.info("🔄 Iniciando coleta bloco CICLO...")
        
        # 1. Buscar dados do Notion
        dados_notion = get_ciclo_data_from_notion()
        if not dados_notion:
            raise Exception("Nenhum dado retornado do Notion Database")
        
        # 2. Extrair indicadores 
        mvrv_z_score = dados_notion.get("mvrv_z_score") or 0.0
        realized_ratio = dados_notion.get("realized_ratio") or 0.0
        puell_multiple = dados_notion.get("puell_multiple") or 0.0
        nupl = dados_notion.get("nupl") or 0.0 
        # 4. Gravar no PostgreSQL
        sucesso = insert_dados_ciclo(
            mvrv_z=float(mvrv_z_score),
            realized_ratio=float(realized_ratio),
            puell_multiple=float(puell_multiple),
            nupl=float(nupl),
            fonte="notion"
        )
        
        if not sucesso:
            raise Exception("Falha ao gravar dados no PostgreSQL")
        
        # 5. Resposta de sucesso
        return {
            "bloco": "ciclos",
            "status": "sucesso",
            "timestamp": datetime.utcnow().isoformat(),
            "dados_coletados": {
                "mvrv_z_score": float(mvrv_z_score),
                "realized_ratio": float(realized_ratio),
                "puell_multiple": float(puell_multiple),
                "nupl":float(nupl),
                "fonte": "notion"
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Erro na coleta CICLO: {str(e)}")
        return {
            "bloco": "ciclos",
            "status": "erro",
            "timestamp": datetime.utcnow().isoformat(),
            "detalhes": f"Falha na coleta: {str(e)}",
            "fonte": "notion"
        }