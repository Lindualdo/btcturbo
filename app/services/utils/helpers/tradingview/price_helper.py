# app/services/utils/helpers/price_helper.py

import requests
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def get_btc_price() -> float:
    """Busca preço atual do BTC com fallback entre fontes"""
    
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
            
            if price > 10000:  # Validação básica
                logger.info(f"✅ Preço BTC obtido via {source['name']}: ${price:,.2f}")
                return price
            else:
                logger.warning(f"⚠️ Preço inválido via {source['name']}: {price}")
                
        except Exception as e:
            logger.warning(f"❌ Falha em {source['name']}: {str(e)}")
            continue
    
    raise Exception("Todas as fontes de preço BTC falharam")