# app/services/dashboards/dash_finance_service.py

import logging
from datetime import datetime
from .dash_finance.queries_orchestrator import (
    get_health_factor_history,
    get_alavancagem_history,
    get_patrimonio_history,
    get_capital_history,
    convert_periodo_to_date
)
from app.services.utils.helpers.tradingview.price_helper import get_btc_price

logger = logging.getLogger(__name__)

def obter_health_factor(periodo: str = "30d") -> dict:
    """Retorna histórico health factor (REAL)"""
    try:
        logger.info(f"🔍 Consultando Health Factor - período: {periodo}")
        
        # Validar período
        if not _validar_periodo(periodo):
            periodo = "30d"
            logger.warning(f"⚠️ Período inválido, usando default: {periodo}")
        
        dados = get_health_factor_history(periodo)
        
        logger.info(f"✅ Health Factor: {len(dados)} registros encontrados")
        
        return {
            "status": "success",
            "indicador": "health_factor", 
            "periodo": periodo,
            "dados": dados,
            "total_registros": len(dados),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Erro consulta Health Factor: {str(e)}")
        return {
            "status": "error",
            "indicador": "health_factor",
            "periodo": periodo,
            "erro": str(e),
            "dados": [],
            "timestamp": datetime.utcnow().isoformat()
        }

def obter_alavancagem(periodo: str = "30d") -> dict:
    """Retorna histórico alavancagens (MOCK)"""
    try:
        logger.info(f"🔍 Consultando Alavancagem - período: {periodo} [MOCK]")
        
        if not _validar_periodo(periodo):
            periodo = "30d"
        
        dados = get_alavancagem_history(periodo)
        
        logger.info(f"✅ Alavancagem: {len(dados)} registros mockados")
        
        return {
            "status": "success",
            "indicador": "alavancagem",
            "periodo": periodo,
            "dados": dados,
            "total_registros": len(dados),
            "mock": True,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Erro consulta Alavancagem: {str(e)}")
        return {
            "status": "error",
            "indicador": "alavancagem", 
            "periodo": periodo,
            "erro": str(e),
            "dados": [],
            "timestamp": datetime.utcnow().isoformat()
        }

def obter_patrimonio(periodo: str = "30d") -> dict:
    """Retorna evolução patrimônio líquido (REAL)"""
    try:
        logger.info(f"🔍 Consultando Patrimônio - período: {periodo}")
        
        if not _validar_periodo(periodo):
            periodo = "30d"
        
        dados = get_patrimonio_history(periodo)
        btc_price = get_btc_price()
        
        logger.info(f"✅ Patrimônio: {len(dados)} registros encontrados")
        
        return {
            "status": "success",
            "indicador": "patrimonio",
            "saldo_btc_core":0.765223,
            "btc_price":btc_price,
            "periodo": periodo, 
            "dados": dados,
            "total_registros": len(dados),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Erro consulta Patrimônio: {str(e)}")
        return {
            "status": "error",
            "indicador": "patrimonio",
            "periodo": periodo,
            "erro": str(e), 
            "dados": [],
            "timestamp": datetime.utcnow().isoformat()
        }

def obter_capital_investido(periodo: str = "30d") -> dict:
    """Retorna evolução capital investido (MOCK)"""
    try:
        logger.info(f"🔍 Consultando Capital Investido - período: {periodo} [MOCK]")
        
        if not _validar_periodo(periodo):
            periodo = "30d"
        
        dados = get_capital_history(periodo)
        
        logger.info(f"✅ Capital Investido: {len(dados)} registros mockados")
        
        return {
            "status": "success",
            "indicador": "capital_investido",
            "periodo": periodo,
            "dados": dados, 
            "total_registros": len(dados),
            "mock": True,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Erro consulta Capital Investido: {str(e)}")
        return {
            "status": "error",
            "indicador": "capital_investido",
            "periodo": periodo,
            "erro": str(e),
            "dados": [],
            "timestamp": datetime.utcnow().isoformat()
        }

def _validar_periodo(periodo: str) -> bool:
    """Valida formato do período"""
    periodos_validos = ["30d", "3m", "6m", "1y", "all"]
    return periodo in periodos_validos