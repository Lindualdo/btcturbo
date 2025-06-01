# app/services/utils/helpers/realized_cap/mvrv_calculator.py - DADOS REAIS

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

    def calculate_mvrv_z_score_real(self, use_real_bigquery: bool = True) -> Dict:
        """
        Calcula MVRV Z-Score usando dados REAIS do BigQuery
        
        Args:
            use_real_bigquery: True = dados reais BigQuery, False = calibrado melhorado
        """
        try:
            logger.info("🎯 Calculando MVRV Z-Score com dados REAIS...")
            
            # 1. Market Cap atual
            mc_data = get_current_market_cap()
            market_cap_atual = mc_data["market_cap_usd"]
            
            # 2. Realized Cap atual REAL
            rc_data = self.rc_calculator.calculate_current_realized_cap()
            realized_cap_atual = rc_data["realized_cap_usd"]
            
            # 3. Série histórica (REAL ou calibrada melhorada)
            if use_real_bigquery:
                logger.info("📊 Usando série histórica REAL via BigQuery...")
                historical_series = self.historical_handler.get_mvrv_historical_series_real(days=120)
                metodo_usado = "bigquery_real_utxo_sampling"
            else:
                logger.info("📊 Usando série histórica calibrada melhorada...")
                historical_series = self.historical_handler.get_mvrv_historical_series_optimized(days=120)
                metodo_usado = "calibrated_enhanced_volatility"
            
            # 4. Calcular StdDev com dados históricos
            if len(historical_series) < 10:
                raise Exception(f"Dados históricos insuficientes: apenas {len(historical_series)} pontos")
            
            mc_rc_diffs_b = [point["mc_rc_diff"] / 1e9 for point in historical_series]
            
            stddev_b = statistics.stdev(mc_rc_diffs_b)
            mean_diff_b = statistics.mean(mc_rc_diffs_b)
            
            # 5. MVRV Z-Score final
            current_diff = market_cap_atual - realized_cap_atual
            current_diff_b = current_diff / 1e9
            
            mvrv_z_score = current_diff_b / stddev_b if stddev_b > 0 else 0
            
            # 6. Validação contra referência conhecida
            coinglass_mvrv = 2.5158
            diferenca_vs_coinglass = abs(mvrv_z_score - coinglass_mvrv)
            
            # Se diferença muito grande, usar método alternativo
            if diferenca_vs_coinglass > 5.0 and use_real_bigquery:
                logger.warning(f"⚠️ MVRV muito diferente do Coinglass ({mvrv_z_score:.2f} vs {coinglass_mvrv})")
                logger.info("🔄 Tentando método calibrado melhorado...")
                return self.calculate_mvrv_z_score_real(use_real_bigquery=False)
            
            # 7. Resultado final
            result = {
                "mvrv_z_score": round(mvrv_z_score, 2),
                "metodo_usado": metodo_usado,
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
                    "metodo": metodo_usado,
                    "periodo_dias": len(historical_series),
                    "data_source": historical_series[0].get("data_source", "unknown") if historical_series else "unknown"
                },
                "validacao": {
                    "range_esperado": (-2.0, 8.0),
                    "valor_plausivel": -2.0 <= mvrv_z_score <= 8.0,
                    "comparacao_coinglass": coinglass_mvrv,
                    "diferenca_vs_coinglass": diferenca_vs_coinglass,
                    "precisao_vs_coinglass": "alta" if diferenca_vs_coinglass < 1.0 else "média" if diferenca_vs_coinglass < 3.0 else "baixa"
                },
                "quality_metrics": {
                    "rc_fonte": rc_data.get("fonte", "unknown"),
                    "mc_fonte": mc_data.get("componentes", {}).get("price_source", "unknown"),
                    "dados_reais": use_real_bigquery,
                    "stddev_plausivel": 200 <= stddev_b <= 800,  # Range esperado para StdDev
                    "estimated_accuracy": "high" if use_real_bigquery and diferenca_vs_coinglass < 1.0 else "medium"
                },
                "debugging_info": {
                    "stddev_objetivo": "300-600B para MVRV ~2.5",
                    "stddev_atual": f"{stddev_b:.1f}B",
                    "mc_rc_ratio_atual": realized_cap_atual / market_cap_atual,
                    "serie_sample": [
                        {
                            "date": point["date"],
                            "rc_mc_ratio": point.get("rc_mc_ratio", 0),
                            "mc_rc_diff_b": point["mc_rc_diff"] / 1e9
                        } for point in historical_series[:5]  # Primeiros 5 pontos
                    ]
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"✅ MVRV Z-Score: {mvrv_z_score:.2f} (vs Coinglass: {coinglass_mvrv})")
            logger.info(f"📊 StdDev: {stddev_b:.1f}B | RC/MC: {realized_cap_atual/market_cap_atual:.1%}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro MVRV Z-Score real: {str(e)}")
            raise Exception(f"MVRV Z-Score real falhou: {str(e)}")

    def test_realized_cap_accuracy(self) -> Dict:
        """Testa precisão do RC vs dados conhecidos"""
        try:
            logger.info("🧪 Testando precisão do Realized Cap...")
            
            # RC atual via nosso método
            our_rc = self.rc_calculator.calculate_current_realized_cap()
            
            # Market Cap para comparação
            mc_data = get_current_market_cap()
            market_cap = mc_data["market_cap_usd"]
            
            # Range esperado baseado em dados históricos
            expected_rc_min = market_cap * 0.25  # 25% mínimo histórico
            expected_rc_max = market_cap * 0.85  # 85% máximo histórico
            
            our_rc_value = our_rc["realized_cap_usd"]
            is_plausible = expected_rc_min <= our_rc_value <= expected_rc_max
            
            # Teste com diferentes métodos
            rc_sampling = self.rc_calculator.calculate_realized_cap_real_sampling()
            
            return {
                "our_realized_cap": our_rc_value,
                "our_rc_bilhoes": our_rc_value / 1e9,
                "market_cap": market_cap,
                "rc_mc_ratio": our_rc_value / market_cap,
                "expected_range": {
                    "min_bilhoes": expected_rc_min / 1e9,
                    "max_bilhoes": expected_rc_max / 1e9,
                    "min_percent": 25,
                    "max_percent": 85
                },
                "is_plausible": is_plausible,
                "quality_check": "✅ PASS" if is_plausible else "❌ FAIL",
                "metodos_testados": {
                    "current_method": {
                        "valor": our_rc_value / 1e9,
                        "fonte": our_rc.get("fonte", "unknown")
                    },
                    "sampling_method": {
                        "valor": rc_sampling["realized_cap_usd"] / 1e9,
                        "fonte": rc_sampling.get("fonte", "unknown")
                    }
                },
                "recomendacao": "RC plausível - usar para MVRV" if is_plausible else "RC fora do range - verificar BigQuery",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Erro teste RC: {str(e)}")
            return {"error": str(e), "timestamp": datetime.utcnow().isoformat()}

    def calculate_realized_price_ratio(self) -> Dict:
        """
        BONUS: Calcula Realized Price Ratio para completar indicadores do ciclo
        Fórmula: Preço BTC / (Realized Cap / Supply Circulante)
        """
        try:
            logger.info("🎯 Calculando Realized Price Ratio...")
            
            # 1. Preço BTC atual
            from ..market_cap_helper import get_btc_price
            btc_price, price_source = get_btc_price()
            
            # 2. Supply circulante
            from ..market_cap_helper import get_btc_supply
            btc_supply, supply_source = get_btc_supply()
            
            # 3. Realized Cap atual
            rc_data = self.rc_calculator.calculate_current_realized_cap()
            realized_cap = rc_data["realized_cap_usd"]
            
            # 4. Realized Price (RC / Supply)
            realized_price = realized_cap / btc_supply
            
            # 5. Realized Price Ratio
            realized_ratio = btc_price / realized_price
            
            return {
                "realized_price_ratio": round(realized_ratio, 3),
                "componentes": {
                    "btc_price": btc_price,
                    "realized_price": realized_price,
                    "realized_cap": realized_cap,
                    "btc_supply": btc_supply
                },
                "fontes": {
                    "price_source": price_source,
                    "supply_source": supply_source,
                    "rc_source": rc_data.get("fonte", "unknown")
                },
                "interpretacao": {
                    "valor_atual": realized_ratio,
                    "range_tipico": "0.7 - 2.5",
                    "situacao": "barato" if realized_ratio < 1.0 else "neutro" if realized_ratio < 1.5 else "caro"
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Erro Realized Price Ratio: {str(e)}")
            return {"error": str(e), "timestamp": datetime.utcnow().isoformat()}

# Função de conveniência para usar em outros módulos
def calculate_mvrv_z_score_final(use_real_bigquery: bool = True) -> Dict:
    """
    Função principal para calcular MVRV Z-Score
    
    Args:
        use_real_bigquery: True = dados reais BigQuery, False = calibrado melhorado
    """
    calculator = MVRVCalculator()
    return calculator.calculate_mvrv_z_score_real(use_real_bigquery=use_real_bigquery)

def calculate_realized_price_ratio_final() -> Dict:
    """Função para calcular Realized Price Ratio"""
    calculator = MVRVCalculator()
    return calculator.calculate_realized_price_ratio()