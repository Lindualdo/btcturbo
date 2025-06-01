# app/routers/debug.py

from fastapi import APIRouter
from datetime import datetime
from app.services.utils.helpers.market_cap_helper import (
    get_current_market_cap, compare_with_reference, get_btc_price, get_btc_supply
)
from app.services.utils.helpers.realized_cap_helper import (
    get_current_realized_cap, BigQueryHelper, calculate_mvrv_z_score
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

@router.get("/bigquery-test")
async def debug_bigquery_connection():
    """Testa apenas a conexão BigQuery"""
    try:
        bigquery_helper = BigQueryHelper()
        connection_ok = bigquery_helper.test_connection()
        
        return {
            "status": "success" if connection_ok else "error",
            "bigquery_connection": connection_ok,
            "message": "BigQuery conectado com sucesso" if connection_ok else "Falha na conexão BigQuery",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/mvrv-z-score-real-bigquery")
async def debug_mvrv_z_score_real_bigquery():
    """NOVO: MVRV Z-Score com dados REAIS do BigQuery"""
    try:
        # Import temporário para testar se pasta existe
        import os
        realized_cap_path = "/app/app/services/utils/helpers/realized_cap"
        files_exist = {
            "bigquery_rc_calculator.py": os.path.exists(f"{realized_cap_path}/bigquery_rc_calculator.py"),
            "historical_data.py": os.path.exists(f"{realized_cap_path}/historical_data.py"),
            "mvrv_calculator.py": os.path.exists(f"{realized_cap_path}/mvrv_calculator.py"),
            "__init__.py": os.path.exists(f"{realized_cap_path}/__init__.py")
        }
        
        return {
            "status": "debug_info",
            "message": "Arquivos ainda não criados - implementação pendente",
            "files_status": files_exist,
            "next_step": "Criar arquivos da pasta realized_cap/",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/mvrv-z-score-calibrated-enhanced")
async def debug_mvrv_z_score_calibrated_enhanced():
    """NOVO: MVRV Z-Score calibrado melhorado"""
    try:
        from app.services.utils.helpers.realized_cap.mvrv_calculator import calculate_mvrv_z_score_final
        
        result = calculate_mvrv_z_score_final(use_real_bigquery=False)
        return {
            "status": "success",
            "data": result,
            "note": "Usando método calibrado melhorado com variação realista"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/compare-mvrv-methods")
async def debug_compare_mvrv_methods():
    """NOVO: Comparação entre métodos REAL vs CALIBRADO"""
    try:
        from app.services.utils.helpers.realized_cap.mvrv_calculator import calculate_mvrv_z_score_final
        
        # Método REAL
        try:
            real_result = calculate_mvrv_z_score_final(use_real_bigquery=True)
            real_mvrv = real_result["mvrv_z_score"]
            real_status = "success"
        except Exception as e:
            real_mvrv = None
            real_status = f"error: {str(e)}"
            real_result = {}
        
        # Método CALIBRADO
        try:
            calibrated_result = calculate_mvrv_z_score_final(use_real_bigquery=False)
            calibrated_mvrv = calibrated_result["mvrv_z_score"]
            calibrated_status = "success"
        except Exception as e:
            calibrated_mvrv = None
            calibrated_status = f"error: {str(e)}"
            calibrated_result = {}
        
        # Comparação
        coinglass_reference = 2.5158
        
        comparison = {
            "coinglass_reference": coinglass_reference,
            "metodos": {
                "real_bigquery": {
                    "mvrv": real_mvrv,
                    "status": real_status,
                    "diferenca_vs_coinglass": abs(real_mvrv - coinglass_reference) if real_mvrv else None
                },
                "calibrated_enhanced": {
                    "mvrv": calibrated_mvrv,
                    "status": calibrated_status,
                    "diferenca_vs_coinglass": abs(calibrated_mvrv - coinglass_reference) if calibrated_mvrv else None
                }
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return {
            "status": "success",
            "data": comparison
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }