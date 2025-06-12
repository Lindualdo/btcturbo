# app/services/utils/helpers/rsi_helper.py - SIMPLIFICADO
import logging  # ← ADICIONAR ESTA LINHA
from app.services.utils.helpers.tradingview.tradingview_helper import get_rsi_current
from tvDatafeed import Interval

logger = logging.getLogger(__name__)  # ← ADICIONAR ESTA LINHA

def obter_rsi_diario():
    """RSI Diário via TradingView helper unificado"""
    try:
        logger.info("📊 Buscando RSI Diário via TradingView helper...")
        
        rsi_diario = get_rsi_current(
            symbol='BTCUSDT',
            exchange='BINANCE', 
            timeframe=Interval.in_daily,
            period=14
        )
        
        logger.info(f"✅ RSI Diário obtido: {rsi_diario:.1f}")
        return rsi_diario
            
    except Exception as e:
        logger.error(f"❌ Erro obtendo RSI Diário: {str(e)}")
        raise Exception(f"RSI Diário indisponível: {str(e)}")

def obter_rsi_mensal():
    """
    SIMPLIFICADO: RSI Mensal via TradingView helper unificado
    """
    try:
        logging.info("📊 Buscando RSI Mensal via TradingView helper...")
        
        # Usar função unificada
        rsi_mensal = get_rsi_current(
            symbol='BTCUSDT',
            exchange='BINANCE',
            timeframe=Interval.in_monthly,
            period=14
        )
        
        logging.info(f"✅ RSI Mensal obtido: {rsi_mensal:.1f}")
        return rsi_mensal
        
    except Exception as e:
        logging.error(f"❌ Erro obtendo RSI Mensal: {str(e)}")
        raise Exception(f"RSI Mensal indisponível: {str(e)}")

def obter_rsi_mensal_para_alavancagem():
    """
    SIMPLIFICADO: Função específica para análise de alavancagem
    """
    try:
        rsi_mensal = obter_rsi_mensal()
        
        # Validação específica para tabela MVRV
        if not (0 <= rsi_mensal <= 100):
            raise ValueError(f"RSI Mensal fora do range: {rsi_mensal}")
        
        logging.info(f"✅ RSI Mensal para alavancagem: {rsi_mensal:.1f}")
        return rsi_mensal
        
    except Exception as e:
        logging.error(f"❌ RSI Mensal para alavancagem falhou: {str(e)}")
        raise Exception(f"RSI Mensal indisponível para análise alavancagem: {str(e)}")

def obter_rsi_com_detalhes(timeframe="daily"):
    """
    SIMPLIFICADO: RSI com informações detalhadas usando helper unificado
    """
    try:
        if timeframe == "monthly":
            rsi_valor = obter_rsi_mensal()
            tf_display = "Mensal"
        else:
            rsi_valor = obter_rsi_diario()
            tf_display = "Diário"
        
        # Classificar RSI
        if rsi_valor < 30:
            classificacao = "oversold"
            status = "🟢 Oversold - oportunidade compra"
        elif rsi_valor > 70:
            classificacao = "overbought"
            status = "🔴 Overbought - considerar venda"
        elif rsi_valor < 45:
            classificacao = "neutro_baixo"
            status = "🟡 Neutro baixo"
        elif rsi_valor > 55:
            classificacao = "neutro_alto"
            status = "🟡 Neutro alto"
        else:
            classificacao = "neutro"
            status = "⚪ Neutro"
        
        return {
            "rsi_valor": round(rsi_valor, 1),
            "timeframe": tf_display,
            "classificacao": classificacao,
            "status": status,
            "interpretacao": {
                "oversold": rsi_valor < 30,
                "overbought": rsi_valor > 70,
                "neutro": 30 <= rsi_valor <= 70
            },
            "timestamp": "utc_now"
        }
        
    except Exception as e:
        logging.error(f"❌ Erro RSI detalhado: {str(e)}")
        raise Exception(f"RSI detalhado indisponível: {str(e)}")

# COMPATIBILIDADE: Manter funções legadas
def obter_rsi_diario_original():
    """DEPRECATED: Use obter_rsi_diario()"""
    return obter_rsi_diario()