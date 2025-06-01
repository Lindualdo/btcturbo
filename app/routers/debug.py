# Adicionar ao app/routers/debug.py

@router.get("/mvrv-z-score-final")
async def debug_mvrv_z_score_final():
    """ENDPOINT FINAL: MVRV Z-Score com série histórica REAL"""
    try:
        from app.services.utils.helpers.mvrv_real_calculator import calculate_mvrv_z_score_real
        
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
        from app.services.utils.helpers.mvrv_real_calculator import calculate_realized_price_ratio_real
        
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
        from app.services.utils.helpers.mvrv_real_calculator import get_real_historical_series
        
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
            from app.services.utils.helpers.mvrv_real_calculator import calculate_mvrv_z_score_real
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