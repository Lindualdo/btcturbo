# app/services/utils/helpers/ema_calculator.py

import logging
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Tuple, Optional
from tvDatafeed import TvDatafeed, Interval
from app.config import get_settings

logger = logging.getLogger(__name__)

class EMACalculator:
    def __init__(self):
        """Inicializa calculadora EMAs com configurações"""
        self.settings = get_settings()
        self.tv = None
        self.ema_periods = [17, 34, 144, 305, 610]
        
    def get_tv_session(self) -> TvDatafeed:
        """Obtém sessão TradingView reutilizável"""
        if self.tv is None:
            try:
                logger.info("🔗 Conectando TradingView...")
                self.tv = TvDatafeed(
                    username=self.settings.TV_USERNAME,
                    password=self.settings.TV_PASSWORD
                )
                logger.info("✅ TradingView conectado")
            except Exception as e:
                logger.error(f"❌ Erro TradingView: {str(e)}")
                # Fallback sem login
                self.tv = TvDatafeed()
                logger.warning("⚠️ TradingView sem login - dados limitados")
        return self.tv
    
    def fetch_ohlc_data(self, symbol: str = "BTCUSDT", exchange: str = "BINANCE", 
                       interval: Interval = Interval.in_1_week, n_bars: int = 1000) -> Optional[pd.DataFrame]:
        """Busca dados OHLC do TradingView"""
        try:
            tv = self.get_tv_session()
            
            logger.info(f"📊 Buscando dados {symbol} {exchange} {interval} ({n_bars} barras)")
            
            df = tv.get_hist(
                symbol=symbol,
                exchange=exchange,
                interval=interval,
                n_bars=n_bars
            )
            
            if df is None or df.empty:
                raise Exception("DataFrame vazio ou None")
            
            logger.info(f"✅ {len(df)} barras obtidas - período: {df.index[0]} a {df.index[-1]}")
            return df
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar dados: {str(e)}")
            return None
    
    def calculate_emas(self, df: pd.DataFrame) -> Dict[int, float]:
        """Calcula EMAs para todos os períodos"""
        try:
            if df is None or df.empty:
                raise Exception("DataFrame inválido")
            
            emas = {}
            current_price = float(df['close'].iloc[-1])
            
            for period in self.ema_periods:
                # Calcular EMA usando pandas
                ema_series = df['close'].ewm(span=period, adjust=False).mean()
                ema_value = float(ema_series.iloc[-1])
                emas[period] = round(ema_value, 2)
                
                logger.debug(f"EMA{period}: {ema_value:.2f}")
            
            logger.info(f"✅ EMAs calculadas - Preço atual: ${current_price:,.2f}")
            return emas, current_price
            
        except Exception as e:
            logger.error(f"❌ Erro cálculo EMAs: {str(e)}")
            return {}, 0.0
    
    def calculate_alignment_score(self, emas: Dict[int, float]) -> Tuple[float, Dict]:
        """
        Calcula score de alinhamento (50% do bloco)
        Regra: EMA menor > EMA maior = bullish
        """
        try:
            if not emas or len(emas) < 5:
                return 0.0, {}
            
            score = 0
            details = {}
            
            # Pontuação por par de EMAs (conforme documentação)
            pairs = [
                (17, 34, 1, "curtíssimo prazo"),      # +1 ponto
                (34, 144, 2, "curto prazo"),          # +2 pontos  
                (144, 305, 3, "médio prazo"),         # +3 pontos
                (305, 610, 4, "longo prazo")          # +4 pontos
            ]
            
            for ema_menor, ema_maior, pontos, descricao in pairs:
                if ema_menor in emas and ema_maior in emas:
                    is_bullish = emas[ema_menor] > emas[ema_maior]
                    if is_bullish:
                        score += pontos
                    
                    details[f"{ema_menor}>{ema_maior}"] = {
                        "bullish": is_bullish,
                        "pontos": pontos if is_bullish else 0,
                        "descricao": descricao
                    }
            
            logger.info(f"📈 Score alinhamento: {score}/10")
            return float(score), details
            
        except Exception as e:
            logger.error(f"❌ Erro score alinhamento: {str(e)}")
            return 0.0, {}
    
    def calculate_position_score(self, current_price: float, emas: Dict[int, float]) -> Tuple[float, Dict]:
        """
        Calcula score de posição com distância (50% do bloco)
        Aplica multiplicadores baseados na distância do preço
        """
        try:
            if not emas or current_price <= 0:
                return 0.0, {}
            
            score = 0
            details = {}
            distances = {}
            
            # Pontos base por EMA (conforme documentação)
            base_points = {17: 1, 34: 1, 144: 2, 305: 3, 610: 3}
            
            for period, base_pts in base_points.items():
                if period not in emas:
                    continue
                    
                ema_value = emas[period]
                
                # Calcular distância percentual
                distance_pct = ((current_price - ema_value) / ema_value) * 100
                distances[f"ema_{period}"] = f"{distance_pct:+.2f}%"
                
                # Aplicar multiplicadores conforme regras
                if current_price > ema_value:
                    # Preço acima da EMA
                    if distance_pct > 5:
                        multiplier = 0.5    # Muito esticado
                        risk = "🔴 Alto"
                    elif distance_pct > 2:
                        multiplier = 0.8    # Esticado
                        risk = "🟡 Médio"
                    else:
                        multiplier = 1.0    # Saudável
                        risk = "🟢 Baixo"
                else:
                    # Preço abaixo da EMA
                    if distance_pct >= -2:
                        multiplier = 0.3    # Teste de suporte
                        risk = "🟡 Alerta"
                    else:
                        multiplier = 0.0    # Rompimento
                        risk = "🔴 Sair"
                
                points_earned = base_pts * multiplier
                score += points_earned
                
                details[f"ema_{period}"] = {
                    "valor": ema_value,
                    "distancia_pct": distance_pct,
                    "pontos_base": base_pts,
                    "multiplicador": multiplier,
                    "pontos_finais": points_earned,
                    "risco": risk
                }
            
            logger.info(f"📍 Score posição: {score:.1f}/10")
            return float(score), {"details": details, "distances": distances}
            
        except Exception as e:
            logger.error(f"❌ Erro score posição: {str(e)}")
            return 0.0, {}
    
    def calculate_timeframe_scores(self, timeframe: str) -> Dict:
        """Calcula scores completos para um timeframe"""
        try:
            logger.info(f"🎯 Calculando scores {timeframe}...")
            
            # Definir intervalo
            interval = Interval.in_1_week if timeframe == "1W" else Interval.in_daily
            n_bars = 700 if timeframe == "1W" else 700  # Suficiente para EMA 610
            
            # Buscar dados
            df = self.fetch_ohlc_data(interval=interval, n_bars=n_bars)
            if df is None:
                raise Exception(f"Dados {timeframe} indisponíveis")
            
            # Calcular EMAs
            emas, current_price = self.calculate_emas(df)
            if not emas:
                raise Exception(f"EMAs {timeframe} não calculadas")
            
            # Calcular scores
            alignment_score, alignment_details = self.calculate_alignment_score(emas)
            position_score, position_details = self.calculate_position_score(current_price, emas)
            
            # Score consolidado (alinhamento + posição) / 2
            consolidated_score = (alignment_score + position_score) / 2
            
            return {
                "timeframe": timeframe,
                "emas": emas,
                "current_price": current_price,
                "scores": {
                    "alignment": alignment_score,
                    "position": position_score,
                    "consolidated": consolidated_score
                },
                "details": {
                    "alignment": alignment_details,
                    "position": position_details
                },
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"❌ Erro scores {timeframe}: {str(e)}")
            return {
                "timeframe": timeframe,
                "status": "error",
                "error": str(e)
            }
    
    def calculate_final_weighted_score(self, weekly_data: Dict, daily_data: Dict) -> Dict:
        """
        Calcula score final ponderado: 70% semanal + 30% diário
        """
        try:
            if (weekly_data.get("status") != "success" or 
                daily_data.get("status") != "success"):
                raise Exception("Dados inválidos para ponderação")
            
            weekly_score = weekly_data["scores"]["consolidated"]
            daily_score = daily_data["scores"]["consolidated"]
            
            # Ponderação conforme documentação
            final_score = (weekly_score * 0.7) + (daily_score * 0.3)
            
            logger.info(f"🎯 Score final: {final_score:.2f} (70% × {weekly_score:.2f} + 30% × {daily_score:.2f})")
            
            return {
                "final_score": round(final_score, 2),
                "weights": {"weekly": 0.7, "daily": 0.3},
                "components": {
                    "weekly_score": weekly_score,
                    "daily_score": daily_score
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Erro score ponderado: {str(e)}")
            return {"error": str(e)}

def get_complete_ema_analysis() -> Dict:
    """
    Função principal - retorna análise completa EMAs
    """
    try:
        logger.info("🚀 Iniciando análise completa EMAs...")
        
        calculator = EMACalculator()
        
        # Calcular para ambos timeframes
        weekly_data = calculator.calculate_timeframe_scores("1W")
        daily_data = calculator.calculate_timeframe_scores("1D")
        
        # Score final ponderado
        final_weighted = calculator.calculate_final_weighted_score(weekly_data, daily_data)
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "weekly": weekly_data,
            "daily": daily_data,
            "final_weighted": final_weighted,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro análise completa: {str(e)}")
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "error",
            "error": str(e)
        }