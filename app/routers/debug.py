# app/routers/debug.py

from fastapi import APIRouter
from datetime import datetime
from app.services.utils.helpers.market_cap_helper import (
    get_current_market_cap, compare_with_reference, get_btc_price, get_btc_supply
)
from app.services.utils.helpers.realized_cap_helper import (
    get_current_realized_cap, compare_realized_cap_sources, BigQueryHelper
)

router = APIRouter()

@router.get("/market-cap")
async def debug_market_cap():
    """Debug endpoint para testar cálculo de Market Cap"""
    try:
        result = get_current_market_cap()
        result["timestamp"] = datetime.utcnow().isoformat()
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/market-cap-comparison")
async def debug_market_cap_comparison():
    """Compara nosso Market Cap com referência CoinGecko"""
    try:
        comparison = compare_with_reference()
        return {
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
            "comparison": comparison
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/btc-price")
async def debug_btc_price():
    """Testa apenas a coleta de preço BTC"""
    try:
        price, source = get_btc_price()
        return {
            "status": "success",
            "price": price,
            "source": source,
            "formatted": f"${price:,.2f}",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/btc-supply")
async def debug_btc_supply():
    """Testa apenas a coleta de supply BTC"""
    try:
        supply, source = get_btc_supply()
        return {
            "status": "success",
            "supply": supply,
            "source": source,
            "formatted": f"{supply:,.0f} BTC",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/realized-cap")
async def debug_realized_cap():
    """Testa cálculo de Realized Cap"""
    try:
        result = get_current_realized_cap()
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/realized-cap-comparison")
async def debug_realized_cap_comparison():
    """Compara BigQuery vs APIs para Realized Cap"""
    try:
        comparison = compare_realized_cap_sources()
        return {
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
            "sources": comparison
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/bigquery-test")
async def debug_bigquery_connection():
    """Testa apenas a conexão BigQuery com diagnóstico detalhado"""
    try:
        from app.config import get_settings
        settings = get_settings()
        
        # 1. Verificar configurações
        config_check = {
            "has_credentials_json": bool(getattr(settings, 'GOOGLE_APPLICATION_CREDENTIALS_JSON', None)),
            "has_project_id": bool(getattr(settings, 'GOOGLE_CLOUD_PROJECT', None)),
            "credentials_length": len(getattr(settings, 'GOOGLE_APPLICATION_CREDENTIALS_JSON', '')) if hasattr(settings, 'GOOGLE_APPLICATION_CREDENTIALS_JSON') else 0
        }
        
        # 2. Tentar inicializar BigQuery
        bigquery_helper = BigQueryHelper()
        connection_ok = bigquery_helper.test_connection()
        
        return {
            "status": "success" if connection_ok else "error",
            "bigquery_connection": connection_ok,
            "config_check": config_check,
            "message": "BigQuery conectado com sucesso" if connection_ok else "Falha na conexão BigQuery",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "config_check": config_check if 'config_check' in locals() else "config_check_failed",
            "timestamp": datetime.utcnow().isoformat()
        }