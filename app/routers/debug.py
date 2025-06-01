# app/routers/debug.py - ENDPOINTS ATUALIZADOS

@router.get("/mvrv-z-score-real-bigquery")
async def debug_mvrv_z_score_real_bigquery():
    """NOVO: MVRV Z-Score com dados REAIS do BigQuery"""
    try:
        from app.services.utils.helpers.realized_cap.mvrv_calculator import calculate_mvrv_z_score_final
        
        result = calculate_mvrv_z_score_final(use_real_bigquery=True)  # DADOS REAIS
        return {
            "status": "success",
            "data": result,
            "note": "Usando dados REAIS do BigQuery com amostragem UTXO"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/mvrv-z-score-calibrated-enhanced")
async def debug_mvrv_z_score_calibrated_enhanced():
    """NOVO: MVRV Z-Score calibrado melhorado (fallback)"""
    try:
        from app.services.utils.helpers.realized_cap.mvrv_calculator import calculate_mvrv_z_score_final
        
        result = calculate_mvrv_z_score_final(use_real_bigquery=False)  # CALIBRADO MELHORADO
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

@router.get("/realized-price-ratio")
async def debug_realized_price_ratio():
    """NOVO: Realized Price Ratio para completar bloco CICLO"""
    try:
        from app.services.utils.helpers.realized_cap.mvrv_calculator import calculate_realized_price_ratio_final
        
        result = calculate_realized_price_ratio_final()
        return {
            "status": "success",
            "data": result,
            "note": "Realized Price Ratio usando RC real do BigQuery"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/bigquery-rc-real-sampling")
async def debug_bigquery_rc_real_sampling():
    """NOVO: Teste RC real com amostragem BigQuery"""
    try:
        from app.services.utils.helpers.realized_cap.bigquery_rc_calculator import RealizedCapCalculator
        
        calculator = RealizedCapCalculator()
        result = calculator.calculate_realized_cap_real_sampling()
        
        return {
            "status": "success",
            "data": result,
            "note": "RC calculado via amostragem REAL de UTXOs do BigQuery"
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
                    "diferenca_vs_coinglass": abs(real_mvrv - coinglass_reference) if real_mvrv else None,
                    "stddev": real_result.get("componentes", {}).get("stddev_historico_bilhoes"),
                    "metodo": real_result.get("metodo_usado")
                },
                "calibrated_enhanced": {
                    "mvrv": calibrated_mvrv,
                    "status": calibrated_status,
                    "diferenca_vs_coinglass": abs(calibrated_mvrv - coinglass_reference) if calibrated_mvrv else None,
                    "stddev": calibrated_result.get("componentes", {}).get("stddev_historico_bilhoes"),
                    "metodo": calibrated_result.get("metodo_usado")
                }
            },
            "recomendacao": None,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Determinar melhor método
        if real_status == "success" and calibrated_status == "success":
            real_diff = abs(real_mvrv - coinglass_reference)
            calibrated_diff = abs(calibrated_mvrv - coinglass_reference)
            
            if real_diff < calibrated_diff:
                comparison["recomendacao"] = "Usar método REAL BigQuery (mais preciso)"
            else:
                comparison["recomendacao"] = "Usar método CALIBRADO (mais estável)"
        elif real_status == "success":
            comparison["recomendacao"] = "Usar método REAL BigQuery (único funcionando)"
        elif calibrated_status == "success":
            comparison["recomendacao"] = "Usar método CALIBRADO (único funcionando)"
        else:
            comparison["recomendacao"] = "Ambos métodos falharam - investigar BigQuery"
        
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