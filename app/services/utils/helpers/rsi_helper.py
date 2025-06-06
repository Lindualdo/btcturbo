# app/services/utils/helpers/rsi_helper.py

import logging

def obter_rsi_diario():
    """Busca RSI Diário via TradingView"""
    try:
        from app.services.utils.helpers.trandview_helper import get_tv_datafeed
        from tvDatafeed import Interval
        
        tv = get_tv_datafeed()
        
        # Buscar dados diários do BTC para calcular RSI
        df = tv.get_hist(
            symbol='BTCUSDT',
            exchange='BINANCE',
            interval=Interval.in_daily,
            n_bars=30  # 30 dias para calcular RSI de 14 períodos
        )
        
        if df is not None and not df.empty and len(df) >= 14:
            # Calcular RSI manualmente
            closes = df['close']
            delta = closes.diff()
            
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            
            avg_gain = gain.rolling(window=14).mean()
            avg_loss = loss.rolling(window=14).mean()
            
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            
            # Pegar último valor
            rsi_atual = float(rsi.iloc[-1])
            
            # Validação
            if 0 <= rsi_atual <= 100:
                logging.info(f"✅ RSI Diário obtido via TradingView: {rsi_atual:.1f}")
                return rsi_atual
            else:
                raise ValueError(f"RSI inválido: {rsi_atual}")
        else:
            raise Exception("Dados insuficientes do TradingView")
            
    except Exception as e:
        logging.error(f"❌ Erro obtendo RSI Diário via TradingView: {str(e)}")
        raise Exception(f"RSI Diário indisponível: {str(e)}")

def obter_ema144_distance():
    """Busca distância do preço em relação à EMA 144"""
    try:
        from app.services.scores import tecnico
        
        dados_tecnico = tecnico.calcular_score()
        if dados_tecnico.get("status") == "success":
            # Tentar buscar da estrutura detalhada primeiro
            if "indicadores" in dados_tecnico and "Sistema_EMAs" in dados_tecnico["indicadores"]:
                detalhes = dados_tecnico["indicadores"]["Sistema_EMAs"].get("detalhes", {})
                semanal = detalhes.get("semanal", {})
                distancias = semanal.get("distancias", {})
                
                # Buscar EMA 144 nas distâncias
                for key, value in distancias.items():
                    if "144" in key and isinstance(value, str) and "%" in value:
                        try:
                            # Extrair percentual: "+17.2%" -> 17.2
                            distance = float(value.replace("%", "").replace("+", ""))
                            logging.info(f"✅ EMA144 distance obtida: {distance:+.1f}%")
                            return distance
                        except:
                            continue
            
            # Fallback: usar score técnico como proxy
            score = dados_tecnico.get("score_consolidado", 5)
            if score > 7:
                return 15.0
            elif score > 5:
                return 5.0
            elif score > 3:
                return -5.0
            else:
                return -15.0
                
        raise Exception("Dados técnicos indisponíveis")
        
    except Exception as e:
        logging.error(f"❌ Erro obtendo EMA144 distance: {str(e)}")
        raise Exception(f"EMA144 distance indisponível: {str(e)}")