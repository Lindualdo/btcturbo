# app/routers/debug.py

from fastapi import APIRouter
from datetime import datetime
from app.services.utils.helpers.mvrv.market_cap_helper import (
    get_current_market_cap, compare_with_reference, get_btc_price, get_btc_supply
)
from app.services.utils.helpers.mvrv.realized_cap_helper import (
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
    """MVRV Z-Score simples sem imports circulares"""
    try:
        from app.services.utils.helpers.mvrv_simple_helper import calculate_mvrv_z_score_simple
        
        result = calculate_mvrv_z_score_simple()
        return {
            "status": "success",
            "data": result,
            "note": "MVRV usando BigQuery simples sem imports circulares"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/realized-price-ratio")
async def debug_realized_price_ratio():
    """Realized Price Ratio simples"""
    try:
        from app.services.utils.helpers.mvrv_simple_helper import calculate_realized_price_ratio_simple
        
        result = calculate_realized_price_ratio_simple()
        return {
            "status": "success",
            "data": result,
            "note": "Realized Price Ratio usando BigQuery simples"
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

# NOVOS ENDPOINTS MVRV REAL

@router.get("/mvrv-z-score-final")
async def debug_mvrv_z_score_final():
    """ENDPOINT FINAL: MVRV Z-Score com série histórica REAL"""
    try:
        from app.services.utils.helpers.mvrv.mvrv_real_calculator import calculate_mvrv_z_score_real
        
        result = calculate_mvrv_z_score_real()
        
        return {
            "status": "success" if "error" not in result else "error",
            "data": result,
            "note": "MVRV Z-Score usando BigQuery + série histórica real"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/realized-price-ratio-final")
async def debug_realized_price_ratio_final():
    """Realized Price Ratio final"""
    try:
        from app.services.utils.helpers.mvrv.mvrv_real_calculator import calculate_realized_price_ratio_real
        
        result = calculate_realized_price_ratio_real()
        
        return {
            "status": "success" if "error" not in result else "error",
            "data": result,
            "note": "Realized Price Ratio usando RC real BigQuery"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/historical-series-test")
async def debug_historical_series():
    """Testa apenas a série histórica"""
    try:
        from app.services.utils.helpers.mvrv.mvrv_real_calculator import get_real_historical_series
        
        # Testar com menos dias para ser mais rápido
        diffs = get_real_historical_series(days=90)
        
        import statistics
        if len(diffs) > 1:
            stddev = statistics.stdev(diffs)
            mean_diff = statistics.mean(diffs)
        else:
            stddev = 0
            mean_diff = 0
        
        return {
            "status": "success",
            "data": {
                "total_pontos": len(diffs),
                "stddev_bilhoes": stddev,
                "media_diferenca_bilhoes": mean_diff,
                "primeiros_5_pontos": diffs[:5],
                "ultimos_5_pontos": diffs[-5:] if len(diffs) >= 5 else diffs
            },
            "note": "Teste da série histórica (MC-RC) para StdDev"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/compare-all-mvrv-methods")
async def debug_compare_all_mvrv():
    """Compara todos os métodos MVRV implementados"""
    try:
        results = {}
        
        # Método 1: Simple helper (existente)
        try:
            from app.services.utils.helpers.mvrv_simple_helper import calculate_mvrv_z_score_simple
            simple_result = calculate_mvrv_z_score_simple()
            results["simple_method"] = {
                "mvrv": simple_result.get("mvrv_z_score"),
                "metodo": simple_result.get("metodo"),
                "status": "success"
            }
        except Exception as e:
            results["simple_method"] = {"status": f"error: {str(e)}"}
        
        # Método 2: Real calculator (novo)
        try:
            from app.services.utils.helpers.mvrv.mvrv_real_calculator import calculate_mvrv_z_score_real
            real_result = calculate_mvrv_z_score_real()
            results["real_method"] = {
                "mvrv": real_result.get("mvrv_z_score"),
                "metodo": real_result.get("metodo"),
                "stddev": real_result.get("componentes", {}).get("stddev_historico_b"),
                "pontos": real_result.get("serie_historica", {}).get("pontos"),
                "status": "success" if "error" not in real_result else f"error: {real_result.get('error')}"
            }
        except Exception as e:
            results["real_method"] = {"status": f"error: {str(e)}"}
        
        # Referência
        coinglass_reference = 2.5158
        
        # Análise comparativa
        comparison = {
            "coinglass_reference": coinglass_reference,
            "metodos": results
        }
        
        # Calcular diferenças vs Coinglass
        for method_name, method_data in results.items():
            if method_data.get("status") == "success" and method_data.get("mvrv"):
                diff = abs(method_data["mvrv"] - coinglass_reference)
                method_data["diferenca_vs_coinglass"] = diff
                method_data["precisao"] = "alta" if diff < 1.0 else "média" if diff < 2.0 else "baixa"
        
        return {
            "status": "success",
            "data": comparison,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }