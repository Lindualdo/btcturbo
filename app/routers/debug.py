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

@router.get("/mvrv-improved")
async def debug_mvrv_improved():
    """MVRV BigQuery melhorado com TradingView"""
    try:
        from app.services.utils.helpers.mvrv.mvrv_bigquery_improved import calculate_mvrv_z_score_improved
        
        result = calculate_mvrv_z_score_improved()
        
        return {
            "status": "success" if "error" not in result else "error",
            "data": result,
            "note": "MVRV BigQuery melhorado com TradingView + distribuição de idade"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/mvrv-improved_v2")
async def debug_mvrv_improved_v2():
    """MVRV BigQuery melhorado V2"""
    try:
        from app.services.utils.helpers.mvrv.mvrv_bigquery_improved_v2 import calculate_mvrv_z_score_improved
        
        result = calculate_mvrv_z_score_improved()
        
        return {
            "status": "success" if "error" not in result else "error",
            "data": result,
            "note": "MVRV BigQuery melhorado V2 com TradingView + distribuição de idade"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/mvrv-z-score-calibrated")
async def debug_mvrv_calibrated():
    try:
        from app.services.utils.helpers.mvrv.mvrv_calibrated_calculator import calculate_mvrv_z_score_calibrated
        
        result = calculate_mvrv_z_score_calibrated()
        
        return {
            "status": "success" if "error" not in result else "error",
            "data": result,
            "note": "MVRV Z-Score CALIBRADO com dados reais Glassnode"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/mvrv-calibrated-v2")
async def debug_mvrv_calibrated_v2():
    """MVRV Calibrado V2 com detecção de regime de mercado"""
    try:
        from app.services.utils.helpers.mvrv.mvrv_calibrated_v2 import calculate_mvrv_z_score_calibrated
        
        result = calculate_mvrv_z_score_calibrated()
        
        return {
            "status": "success" if "error" not in result else "error",
            "data": result,
            "note": "MVRV Z-Score CALIBRADO V2 - Melhorado com regimes de mercado"
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

@router.get("/mvrv-comparison-all")
async def debug_mvrv_comparison_all():
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
        
        # Método 2: Real calculator
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
        
        # Método 3: Improved
        try:
            from app.services.utils.helpers.mvrv.mvrv_bigquery_improved import calculate_mvrv_z_score_improved
            improved_result = calculate_mvrv_z_score_improved()
            results["improved_method"] = {
                "mvrv": improved_result.get("mvrv_z_score"),
                "metodo": improved_result.get("metodo"),
                "status": "success" if "error" not in improved_result else f"error: {improved_result.get('error')}"
            }
        except Exception as e:
            results["improved_method"] = {"status": f"error: {str(e)}"}
        
        # Método 4: Calibrated V2
        try:
            from app.services.utils.helpers.mvrv.mvrv_calibrated_v2 import calculate_mvrv_z_score_calibrated
            calibrated_result = calculate_mvrv_z_score_calibrated()
            results["calibrated_v2_method"] = {
                "mvrv": calibrated_result.get("mvrv_z_score"),
                "mvrv_raw": calibrated_result.get("mvrv_z_score_raw"),
                "metodo": calibrated_result.get("metodo"),
                "regime": calibrated_result.get("componentes", {}).get("regime_atual"),
                "status": "success" if "error" not in calibrated_result else f"error: {calibrated_result.get('error')}"
            }
        except Exception as e:
            results["calibrated_v2_method"] = {"status": f"error: {str(e)}"}
        
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
                method_data["precisao"] = "alta" if diff < 0.5 else "média" if diff < 1.0 else "baixa"
        
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
    # Adicionar em app/routers/debug.py

@router.get("/test-ema-calculation")
async def debug_test_ema_calculation():
    """Testa cálculo completo EMAs e scores"""
    try:
        from app.services.utils.helpers.ema_calculator import get_complete_ema_analysis
        
        result = get_complete_ema_analysis()
        
        return {
            "status": "success" if result.get("status") == "success" else "error",
            "data": result,
            "note": "Teste do cálculo completo EMAs com scores"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.post("/test-coleta-tecnico")
async def debug_test_coleta_tecnico(forcar_coleta: bool = True):
    """Testa coleta completa técnico com gravação no PostgreSQL"""
    try:
        from app.services.coleta.tecnico import coletar
        
        result = coletar(forcar_coleta)
        
        return {
            "status": "success" if result.get("status") == "sucesso" else "error", 
            "data": result,
            "note": "Teste da coleta técnico com gravação PostgreSQL"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/test-dados-tecnico-db")
async def debug_test_dados_tecnico_db():
    """Testa leitura dos dados técnicos do PostgreSQL"""
    try:
        from app.services.utils.helpers.postgres.tecnico_helper import get_dados_tecnico, get_emas_detalhadas
        
        # Dados básicos
        dados_basicos = get_dados_tecnico()
        
        # EMAs detalhadas
        emas_detalhadas = get_emas_detalhadas()
        
        return {
            "status": "success",
            "data": {
                "dados_basicos": dados_basicos,
                "emas_detalhadas": emas_detalhadas,
                "tem_dados": dados_basicos is not None,
                "tem_emas": emas_detalhadas is not None
            },
            "note": "Teste de leitura dados técnicos PostgreSQL"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }