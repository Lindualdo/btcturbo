# app/services/utils/helpers/realized_cap/mvrv_calculator.py

import logging
import statistics
from datetime import datetime
from typing import Dict
from .bigquery_rc_calculator import RealizedCapCalculator
from .historical_data import HistoricalDataHandler
from ..market_cap_helper import get_current_market_cap

logger = logging.getLogger(__name__)

class MVRVCalculator:
    def __init__(self):
        self.rc_calculator = RealizedCapCalculator()
        self.historical_handler = HistoricalDataHandler()

    def calculate_mvrv_z_score_real(self, use_sample_method: bool = False) -> Dict:
        """
        Calcula MVRV Z-Score usando dados REAIS
        
        Args:
            use_sample_method: Se True, usa pontos de amostra (mais lento mas preciso)
                              Se False, usa método otimizado (mais rápido)
        """
        try:
            logger.info("🎯 Calculando MVRV Z-Score com dados REAIS...")
            
            # 1. Market Cap atual via helper existente
            mc_data = get_current_market_cap()
            market_cap_atual = mc_data["market_cap_usd"]
            
            # 2. Realized Cap atual REAL via BigQuery
            rc_data = self.rc_calculator.calculate_current_realized_cap()
            realized_cap_atual = rc_data["realized_cap_usd"]
            
            # 3. Série histórica REAL
            if use_sample_method:
                logger.info("📊 Usando método de amostra (preciso mas lento)...")
                historical_series = self.historical_handler.get_mvrv_historical_series_sample(
                    sample_points=15  # Reduzido para performance
                )
            else:
                logger.info("📊 Usando método otimizado (rápido)...")
                historical_series = self.historical_handler.get_mvrv_historical_series_optimized(
                    days=180  # 6 meses de dados
                )
            
            # 4. Calcular StdDev com dados REAIS
            mc_rc_diffs_b = [point["mc_rc_diff"] / 1e9 for point in historical_series]
            
            if len(mc_rc_diffs_b) < 10:
                raise Exception(f"Dados históricos insuficientes: apenas {len(mc_rc_diffs_b)} pontos")
            
            stddev_b = statistics.stdev(mc_rc_diffs_b)
            mean_diff_b = statistics.mean(mc_rc_diffs_b)
            
            # 5. MVRV Z-Score final
            current_diff = market_cap_atual - realized_cap_atual
            current_diff_b = current_diff / 1e9
            
            mvrv_z_score = current_diff_b / stddev_b if stddev_b > 0 else 0
            
            # 6. Preparar resultado detalhado
            result = {
                "mvrv_z_score": round(mvrv_z_score, 2),
                "metodo_usado": "sample_real" if use_sample_method else "optimized_real",
                "componentes": {
                    "market_cap_atual": market_cap_atual,
                    "realized_cap_atual": realized_cap_atual,
                    "diferenca_atual": current_diff,
                    "diferenca_atual_bilhoes": current_diff_b,
                    "stddev_historico_bilhoes": stddev_b,
                    "media_historica_bilhoes": mean_diff_b
                },
                "serie_historica": {
                    "pontos": len(historical_series),
                    "metodo": "BigQuery_RC_real" if use_sample_method else "RC_calibrated",
                    "periodo_dias": len(historical_series)
                },
                "validacao": {
                    "range_esperado": (-2.0, 8.0),
                    "valor_plausivel": -2.0 <= mvrv_z_score <= 8.0,
                    "comparacao_coinglass": 2.5158,
                    "diferenca_vs_coinglass": abs(mvrv_z_score - 2.5158)
                },
                "quality_metrics": {
                    "rc_fonte": rc_data.get("fonte", "unknown"),
                    "mc_fonte": mc_data.get("componentes", {}).get("price_source", "unknown"),
                    "dados_publicos": True,
                    "estimated_accuracy": "high" if use_sample_method else "medium"
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"✅ MVRV Z-Score: {mvrv_z_score:.2f} (vs Coinglass: 2.5158)")
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro MVRV Z-Score real: {str(e)}")
            raise Exception(f"MVRV Z-Score real falhou: {str(e)}")

    def test_realized_cap_accuracy(self) -> Dict:
        """Testa precisão do nosso cálculo RC vs dados conhecidos"""
        try:
            logger.info("🧪 Testando precisão do Realized Cap...")
            
            # RC atual via nosso método
            our_rc = self.rc_calculator.calculate_current_realized_cap()
            
            # Comparar com estimativas conhecidas (RC ~30-40% do MC)
            mc_data = get_current_market_cap()
            market_cap = mc_data["market_cap_usd"]
            
            expected_rc_min = market_cap * 0.25  # 25% mínimo
            expected_rc_max = market_cap * 0.45  # 45% máximo
            
            our_rc_value = our_rc["realized_cap_usd"]
            is_plausible = expected_rc_min <= our_rc_value <= expected_rc_max
            
            return {
                "our_realized_cap": our_rc_value,
                "our_rc_bilhoes": our_rc_value / 1e9,
                "market_cap": market_cap,
                "rc_mc_ratio": our_rc_value / market_cap,
                "expected_range": {
                    "min_bilhoes": expected_rc_min / 1e9,
                    "max_bilhoes": expected_rc_max / 1e9
                },
                "is_plausible": is_plausible,
                "quality_check": "✅ PASS" if is_plausible else "❌ FAIL",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Erro teste RC: {str(e)}")
            return {"error": str(e)}

# Função de conveniência para usar em outros módulos
def calculate_mvrv_z_score_final(use_precise_method: bool = False) -> Dict:
    """
    Função principal para calcular MVRV Z-Score
    
    Args:
        use_precise_method: True = método preciso (lento), False = otimizado (rápido)
    """
    calculator = MVRVCalculator()
    return calculator.calculate_mvrv_z_score_real(use_sample_method=use_precise_method)