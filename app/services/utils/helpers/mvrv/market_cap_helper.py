# app/services/utils/helpers/market_cap_helper.py

import requests
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

def get_btc_price() -> Tuple[float, str]:
    """
    Busca preço atual do BTC com fallback entre fontes
    Retorna: (price, fonte_usada)
    """
    
    sources = [
        {
            "name": "CoinGecko",
            "url": "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd",
            "parser": lambda r: r.json()["bitcoin"]["usd"]
        },
        {
            "name": "Binance",
            "url": "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT",
            "parser": lambda r: float(r.json()["price"])
        },
        {
            "name": "CoinMarketCap",
            "url": "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?symbol=BTC",
            "parser": lambda r: r.json()["data"]["BTC"]["quote"]["USD"]["price"]
        }
    ]
    
    for source in sources:
        try:
            logger.info(f"🔍 Buscando preço BTC via {source['name']}")
            
            response = requests.get(source["url"], timeout=10)
            response.raise_for_status()
            
            price = source["parser"](response)
            price = float(price)
            
            # Validação básica: BTC deve estar entre $10k e $200k
            if 10000 <= price <= 200000:
                logger.info(f"✅ Preço BTC: ${price:,.2f} (fonte: {source['name']})")
                return price, source['name']
            else:
                logger.warning(f"⚠️ Preço inválido via {source['name']}: ${price:,.2f}")
                
        except Exception as e:
            logger.warning(f"❌ Falha em {source['name']}: {str(e)}")
            continue
    
    raise Exception("Todas as fontes de preço BTC falharam")


def get_btc_supply() -> Tuple[float, str]:
    """
    Busca supply circulante do BTC
    Retorna: (supply, fonte_usada)
    """
    
    sources = [
        {
            "name": "CoinGecko",
            "url": "https://api.coingecko.com/api/v3/coins/bitcoin",
            "parser": lambda r: r.json()["market_data"]["circulating_supply"]
        },
        {
            "name": "Blockchain.com",
            "url": "https://blockchain.info/q/totalbc",
            "parser": lambda r: float(r.text) / 100000000  # satoshis para BTC
        }
    ]
    
    for source in sources:
        try:
            logger.info(f"🔍 Buscando supply BTC via {source['name']}")
            
            response = requests.get(source["url"], timeout=10)
            response.raise_for_status()
            
            supply = source["parser"](response)
            supply = float(supply)
            
            # Validação: Supply deve estar entre 19M e 21M BTC
            if 19000000 <= supply <= 21000000:
                logger.info(f"✅ Supply BTC: {supply:,.0f} BTC (fonte: {source['name']})")
                return supply, source['name']
            else:
                logger.warning(f"⚠️ Supply inválido via {source['name']}: {supply:,.0f}")
                
        except Exception as e:
            logger.warning(f"❌ Falha em {source['name']}: {str(e)}")
            continue
    
    raise Exception("Todas as fontes de supply BTC falharam")


def get_current_market_cap() -> dict:
    """
    Calcula Market Cap atual do BTC
    Retorna: dict com valor, componentes e metadados
    """
    try:
        logger.info("🎯 Iniciando cálculo Market Cap BTC...")
        
        # Buscar componentes
        price, price_source = get_btc_price()
        supply, supply_source = get_btc_supply()
        
        # Calcular Market Cap
        market_cap = price * supply
        
        # Validação final: Market Cap entre $500B e $3T
        if not (0.5e12 <= market_cap <= 3e12):
            logger.warning(f"⚠️ Market Cap fora do range esperado: ${market_cap/1e12:.2f}T")
        
        result = {
            "market_cap_usd": market_cap,
            "market_cap_trilhoes": market_cap / 1e12,
            "componentes": {
                "btc_price": price,
                "btc_supply": supply,
                "price_source": price_source,
                "supply_source": supply_source
            },
            "validacao": {
                "price_range_ok": 10000 <= price <= 200000,
                "supply_range_ok": 19000000 <= supply <= 21000000,
                "market_cap_range_ok": 0.5e12 <= market_cap <= 3e12
            },
            "timestamp": "utc_now"
        }
        
        logger.info(f"✅ Market Cap calculado: ${market_cap/1e12:.2f}T")
        return result
        
    except Exception as e:
        logger.error(f"❌ Erro no cálculo Market Cap: {str(e)}")
        raise Exception(f"Falha no Market Cap: {str(e)}")


def compare_with_reference() -> dict:
    """
    Compara nosso Market Cap com fontes de referência
    """
    try:
        # Nosso cálculo
        our_mc = get_current_market_cap()
        
        # Referência CoinGecko
        ref_response = requests.get(
            "https://api.coingecko.com/api/v3/coins/bitcoin",
            timeout=10
        )
        ref_mc = ref_response.json()["market_data"]["market_cap"]["usd"]
        
        # Comparação
        diff_abs = abs(our_mc["market_cap_usd"] - ref_mc)
        diff_pct = diff_abs / ref_mc
        
        comparison = {
            "our_market_cap": our_mc["market_cap_usd"],
            "reference_market_cap": ref_mc,
            "difference_usd": diff_abs,
            "difference_percent": diff_pct,
            "status": "✅ PASS" if diff_pct < 0.05 else "⚠️ DIVERGÊNCIA",
            "acceptable": diff_pct < 0.05
        }
        
        logger.info(f"📊 Comparação Market Cap: {comparison['status']} ({diff_pct:.2%} diferença)")
        return comparison
        
    except Exception as e:
        logger.error(f"❌ Erro na comparação: {str(e)}")
        return {"error": str(e)}