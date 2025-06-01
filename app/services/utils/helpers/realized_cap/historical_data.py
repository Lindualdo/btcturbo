# app/services/utils/helpers/realized_cap/historical_data.py

import logging
from datetime import datetime, timedelta
from typing import List, Dict
import requests
from .bigquery_rc_calculator import RealizedCapCalculator

logger = logging.getLogger(__name__)

class HistoricalDataHandler:
    def __init__(self):
        self.rc_calculator = RealizedCapCalculator()

    def get_market_cap_historical_series(self, days: int = 365) -> List[Dict]:
        """Busca série histórica Market Cap via CoinGecko"""
        try:
            logger.info(f"🔍 Buscando Market Cap histórico ({days} dias)...")
            
            url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
            params = {
                "vs_currency": "usd",
                "days": days,
                "interval": "daily"
            }
            
            response = requests.get(url, params=params, timeout=20)
            response.raise_for_status()
            data = response.json()
            
            series = []
            for timestamp, market_cap in data["market_caps"]:
                date_obj = datetime.fromtimestamp(timestamp/1000)
                series.append({
                    "date": date_obj.strftime('%Y-%m-%d'),
                    "timestamp": timestamp,
                    "market_cap": float(market_cap)
                })
            
            logger.info(f"✅ Market Cap histórico: {len(series)} pontos")
            return series
            
        except Exception as e:
            logger.error(f"❌ Erro Market Cap histórico: {str(e)}")
            raise Exception(f"Market Cap histórico falhou: {str(e)}")

    def get_mvrv_historical_series_sample(self, sample_points: int = 20) -> List[Dict]:
        """
        Calcula série MVRV histórica usando pontos de amostra
        Para evitar overload do BigQuery, usa apenas pontos espaçados
        """
        try:
            logger.info(f"🔍 Calculando MVRV histórico ({sample_points} pontos de amostra)...")
            
            # Market Cap histórico completo
            mc_series = self.get_market_cap_historical_series(days=365)
            
            if len(mc_series) < sample_points:
                raise Exception(f"Dados MC insuficientes: {len(mc_series)} pontos")
            
            # Selecionar pontos espaçados
            step = len(mc_series) // sample_points
            sampled_dates = mc_series[::step][:sample_points]
            
            # Buscar preços históricos para RC calculation
            price_dict = self.rc_calculator.get_historical_btc_prices(days=400)
            
            mvrv_series = []
            for point in sampled_dates:
                try:
                    date_str = point["date"]
                    market_cap = point["market_cap"]
                    
                    # Calcular RC real para esta data
                    realized_cap = self.rc_calculator.calculate_realized_cap_for_date(
                        date_str, price_dict
                    )
                    
                    mc_rc_diff = market_cap - realized_cap
                    
                    mvrv_series.append({
                        "date": date_str,
                        "market_cap": market_cap,
                        "realized_cap": realized_cap,
                        "mc_rc_diff": mc_rc_diff,
                        "rc_mc_ratio": realized_cap / market_cap if market_cap > 0 else 0
                    })
                    
                    logger.info(f"📊 {date_str}: MC=${market_cap/1e9:.1f}B, RC=${realized_cap/1e9:.1f}B")
                    
                except Exception as e:
                    logger.warning(f"⚠️ Falha para {point['date']}: {str(e)}")
                    continue
            
            if len(mvrv_series) < 10:
                raise Exception(f"Pontos MVRV insuficientes: apenas {len(mvrv_series)}")
            
            logger.info(f"✅ Série MVRV histórica: {len(mvrv_series)} pontos calculados")
            return mvrv_series
            
        except Exception as e:
            logger.error(f"❌ Erro série MVRV histórica: {str(e)}")
            raise Exception(f"Série MVRV histórica falhou: {str(e)}")

    def get_mvrv_historical_series_optimized(self, days: int = 90) -> List[Dict]:
        """
        Versão otimizada: RC histórico usando estimativa melhorada
        Baseada em dados reais mas com performance melhor
        """
        try:
            logger.info(f"🔍 MVRV histórico otimizado ({days} dias)...")
            
            # Market Cap + Preços históricos
            mc_series = self.get_market_cap_historical_series(days=days)
            price_dict = self.rc_calculator.get_historical_btc_prices(days=days + 30)
            
            # RC atual real para calibração
            current_rc_data = self.rc_calculator.calculate_current_realized_cap()
            current_rc = current_rc_data["realized_cap_usd"]
            
            # MC atual para calcular proporção
            current_mc = mc_series[0]["market_cap"] if mc_series else 2e12
            rc_mc_ratio_current = current_rc / current_mc
            
            logger.info(f"📊 Proporção RC/MC atual (real): {rc_mc_ratio_current:.3f}")
            
            mvrv_series = []
            for point in mc_series:
                date_str = point["date"]
                market_cap = point["market_cap"]
                
                # RC estimado baseado na proporção atual com ajuste temporal
                # Em bear markets, RC/MC ratio é maior (RC não cai tanto)
                # Em bull markets, RC/MC ratio é menor (MC sobe mais rápido)
                
                if date_str in price_dict:
                    # Ajuste baseado no preço: preços baixos = ratio maior
                    btc_price = price_dict[date_str]
                    price_factor = min(btc_price / 50000, 2.0)  # Normalizar vs $50k
                    
                    adjusted_ratio = rc_mc_ratio_current * (2.0 - price_factor * 0.5)
                    realized_cap = market_cap * adjusted_ratio
                else:
                    realized_cap = market_cap * rc_mc_ratio_current
                
                mc_rc_diff = market_cap - realized_cap
                
                mvrv_series.append({
                    "date": date_str,
                    "market_cap": market_cap,
                    "realized_cap": realized_cap,
                    "mc_rc_diff": mc_rc_diff
                })
            
            logger.info(f"✅ MVRV otimizado: {len(mvrv_series)} pontos")
            return mvrv_series
            
        except Exception as e:
            logger.error(f"❌ Erro MVRV otimizado: {str(e)}")
            raise Exception(f"MVRV otimizado falhou: {str(e)}")