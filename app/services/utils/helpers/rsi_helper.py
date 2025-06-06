# app/services/utils/helpers/rsi_helper.py - CORRIGIDO

import logging

def obter_rsi_diario():
    """Busca RSI Diário via TradingView - CORRIGIDO"""
    try:
        from tvDatafeed import TvDatafeed, Interval
        from app.config import get_settings
        
        settings = get_settings()
        
        # Corrigido: remover auto_login e usar credenciais se disponíveis
        try:
            if settings.TV_USERNAME and settings.TV_PASSWORD:
                logging.info("🔗 Conectando TradingView com credenciais...")
                tv = TvDatafeed(
                    username=settings.TV_USERNAME,
                    password=settings.TV_PASSWORD
                )
            else:
                logging.info("🔗 Conectando TradingView sem login...")
                tv = TvDatafeed()  # Sem parâmetros - modo anônimo
        except Exception as e:
            logging.warning(f"⚠️ Falha login TradingView: {e} - tentando modo anônimo")
            tv = TvDatafeed()
        
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
    """Busca distância do preço em relação à EMA 144 - MELHORADO"""
    try:
        from app.services.utils.helpers.postgres.tecnico_helper import get_emas_detalhadas
        
        # Tentar buscar direto do PostgreSQL
        emas_data = get_emas_detalhadas()
        
        if emas_data:
            # Buscar EMA 144 semanal (preferência)
            semanal = emas_data.get("semanal", {})
            emas = semanal.get("emas", {})
            btc_price = emas_data.get("geral", {}).get("btc_price", 0)
            
            if emas.get(144) and btc_price > 0:
                ema_144 = emas[144]
                distance = ((btc_price - ema_144) / ema_144) * 100
                logging.info(f"✅ EMA144 distance calculada: {distance:+.1f}% (${btc_price:,.0f} vs ${ema_144:,.0f})")
                return distance
        
        # Fallback: buscar via PostgreSQL se disponível
        from app.services.scores import tecnico
        dados_tecnico = tecnico.calcular_score()
        
        if dados_tecnico.get("status") == "success":
            # Verificar se tem dados detalhados de EMAs
            indicadores = dados_tecnico.get("indicadores", {})
            if "Sistema_EMAs" in indicadores:
                detalhes = indicadores["Sistema_EMAs"].get("detalhes", {})
                semanal = detalhes.get("semanal", {})
                distancias = semanal.get("distancias", {})
                
                # Buscar EMA 144 nas distâncias
                for key, value in distancias.items():
                    if "144" in key and isinstance(value, str) and "%" in value:
                        try:
                            distance = float(value.replace("%", "").replace("+", ""))
                            logging.info(f"✅ EMA144 distance obtida via PostgreSQL: {distance:+.1f}%")
                            return distance
                        except:
                            continue
                
        raise Exception("Dados técnicos indisponíveis")
        
    except Exception as e:
        logging.error(f"❌ Erro obtendo EMA144 distance: {str(e)}")
        raise Exception(f"EMA144 distance indisponível: {str(e)}")