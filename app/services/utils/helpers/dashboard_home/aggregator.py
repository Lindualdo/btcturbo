# app/services/utils/helpers/dashboard_home/aggregator.py - ATUALIZADO COM ESTRATÉGIA

import logging
from datetime import datetime
from .header_helper import get_header_data
from .mercado_helper import get_mercado_data
from .risco_helper import get_risco_data
from .alavancagem_helper import get_alavancagem_data
from .estrategia_helper import get_estrategia_data  # ← NOVO

logger = logging.getLogger(__name__)

def collect_all_dashboard_data() -> dict:
    """
    Coleta dados de todos os módulos do dashboard incluindo estratégia
    
    Returns:
        dict com todos os campos + JSON consolidado
    """
    try:
        logger.info("🚀 Coletando dados completos do dashboard com estratégia...")
        
        # Coletar dados de cada módulo (mesma ordem)
        header_data = get_header_data()
        mercado_data = get_mercado_data()
        risco_data = get_risco_data()
        alavancagem_data = get_alavancagem_data()
        
        # NOVO: Coletar dados de estratégia (precisa dos dados dos outros módulos)
        dados_para_estrategia = {
            "mercado": mercado_data,
            "risco": risco_data,
            "alavancagem": alavancagem_data
        }
        
        estrategia_data = get_estrategia_data(dados_para_estrategia)
        
        # Verificar se algum módulo falhou
        erros = []
        if header_data["status"] != "success":
            erros.append(f"Header: {header_data['erro']}")
        if mercado_data["status"] != "success":
            erros.append(f"Mercado: {mercado_data['erro']}")
        if risco_data["status"] != "success":
            erros.append(f"Risco: {risco_data['erro']}")
        if alavancagem_data["status"] != "success":
            erros.append(f"Alavancagem: {alavancagem_data['erro']}")
        if estrategia_data["status"] != "success":
            erros.append(f"Estratégia: {estrategia_data['erro']}")
        
        if erros:
            raise Exception(f"Falhas nos módulos: {'; '.join(erros)}")
        
        # Consolidar campos para PostgreSQL
        campos_consolidados = {
            **header_data["campos"],
            **mercado_data["campos"],
            **risco_data["campos"],
            **alavancagem_data["campos"],
            **estrategia_data["campos"]  # ← NOVO
        }
        
        # Consolidar JSON para frontend
        json_consolidado = {
            "fase": "5_header_mercado_risco_alavancagem_estrategia",  # ← ATUALIZADO
            "timestamp": datetime.utcnow().isoformat(),
            "header": header_data["json"],
            "mercado": mercado_data["json"],
            "risco": risco_data["json"],
            "alavancagem": alavancagem_data["json"],
            "estrategia": estrategia_data["json"],  # ← NOVO
            "metadata": {
                "fonte_header": header_data["fonte"],
                "fonte_mercado": mercado_data["fonte"],
                "fonte_risco": risco_data["fonte"],
                "fonte_alavancagem": alavancagem_data["fonte"],
                "fonte_estrategia": estrategia_data["fonte"],  # ← NOVO
                "modulos": ["header", "mercado", "risco", "alavancagem", "estrategia"],  # ← ATUALIZADO
                "versao": "modular_v2_com_estrategia"  # ← ATUALIZADO
            }
        }
        
        logger.info("✅ Dados consolidados com sucesso (incluindo estratégia)")
        
        return {
            "status": "success",
            "campos": campos_consolidados,
            "json": json_consolidado,
            "modulos_coletados": ["header", "mercado", "risco", "alavancagem", "estrategia"],  # ← ATUALIZADO
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Erro na consolidação com estratégia: {str(e)}")
        return {
            "status": "error",
            "erro": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }