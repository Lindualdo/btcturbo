# 📊 Documentação de Indicadores On-Chain e Técnicos BTC - v2.0
**Objetivo:** Coletar dados reais de fontes públicas e calcular indicadores com padrão Glassnode.  
**Princípios:** Sem hardcode, com fallback entre fontes, erro se não encontrar dados.

---

## 1. MVRV Z-Score

**Descrição:**  
Mede o quão valorizado/desvalorizado o Bitcoin está em relação ao seu valor realizado, ajustado pela volatilidade histórica.

**Fórmula:**  
```
MVRV Z-Score = (Market Cap - Realized Cap) / StdDev(Market Cap - Realized Cap)
```

**Fontes de dados (ordem de prioridade):**
1. **Market Cap:** CoinGecko API → CoinMarketCap API → Blockchain.com
2. **Realized Cap:** CryptoQuant API (free tier) → Glassnode API (free tier) → Blockchain.com (cálculo UTXO)
3. **StdDev:** Calcular localmente com série histórica de (MC - RC)

**Implementação:**
```python
# 1. Obter Market Cap atual
market_cap = preço_btc * supply_circulante

# 2. Obter Realized Cap
realized_cap = soma(utxo_value * preço_quando_movido) / total_btc

# 3. Calcular série histórica (MC - RC) últimos 2 anos
historical_diff = market_cap_series - realized_cap_series

# 4. Calcular desvio padrão da série
std_dev = historical_diff.std()

# 5. Calcular Z-Score
mvrv_z = (market_cap - realized_cap) / std_dev
```

---

## 2. Realized Price Ratio

**Descrição:**  
Razão entre preço atual e preço médio de aquisição on-chain.

**Fórmula:**  
```
Realized Price Ratio = Preço BTC / (Realized Cap / Supply Circulante)
```

**Fontes de dados:**
1. **Preço BTC:** CoinGecko → Binance API → CoinMarketCap
2. **Realized Cap:** Mesmas fontes do MVRV
3. **Supply:** Blockchain.com API → CoinGecko

**Implementação:**
```python
# 1. Obter preço atual
current_price = get_btc_price()

# 2. Calcular Realized Price
realized_price = realized_cap / circulating_supply

# 3. Calcular ratio
ratio = current_price / realized_price
```

---

## 3. Puell Multiple

**Descrição:**  
Avalia receita dos mineradores vs média histórica.

**Fórmula:**  
```
Puell Multiple = Receita Diária Mineradores (USD) / MA365(Receita Diária)
```
*Receita = (Recompensa Bloco + Fees) × Preço BTC*

**Fontes de dados:**
1. **Recompensa diária:** Blockchain.com/charts/total-bitcoins → Blockchair API
2. **Fees diários:** Blockchain.com/charts/transaction-fees → Mempool.space API
3. **Preço histórico:** CoinGecko (365 dias)

**Implementação:**
```python
# 1. Obter emissão diária (últimas 24h)
blocks_24h = 144  # aproximado
block_reward = 6.25  # atualizar após halving
daily_btc = blocks_24h * block_reward + daily_fees_btc

# 2. Converter para USD
daily_usd = daily_btc * current_btc_price

# 3. Calcular MA365
ma365 = daily_revenue_series.rolling(365).mean().iloc[-1]

# 4. Calcular Puell
puell = daily_usd / ma365
```

---

## 4. Funding Rates

**Descrição:**  
Taxa média ponderada paga entre posições long/short em perpétuos.

**Fórmula:**  
```
Funding Rate Avg = Σ(FR_exchange × Volume_exchange) / Σ(Volume_exchange)
```

**Fontes de dados:**
1. **Agregado:** Coinglass API → Coinalyze API
2. **Individual:** Binance API + Bybit API + OKX API (calcular média ponderada)

**Implementação:**
```python
# 1. Coletar de múltiplas exchanges
exchanges = ['binance', 'bybit', 'okx']
weighted_sum = 0
total_volume = 0

for exchange in exchanges:
    fr = get_funding_rate(exchange)
    vol = get_perp_volume(exchange)
    weighted_sum += fr * vol
    total_volume += vol

# 2. Calcular média ponderada
avg_funding = weighted_sum / total_volume
```

---

## 5. Exchange Netflow 7D

**Descrição:**  
Fluxo líquido de BTC entrando/saindo das exchanges em 7 dias.

**Fórmula:**  
```
Netflow 7D = Σ(Inflows_7d) - Σ(Outflows_7d)
```

**Fontes de dados:**
1. **CryptoQuant API:** `/v1/btc/exchange_flows/netflow` (endpoint específico)
2. **Glassnode:** `/v1/metrics/exchanges/netflow_volume` (limitado)
3. **Blockchain análise:** Somar transações para/de endereços conhecidos de exchanges

**Implementação:**
```python
# 1. Via CryptoQuant (recomendado)
response = cryptoquant_api.get('/v1/btc/exchange_flows/netflow', 
                               params={'window': '7d'})
netflow_7d = response['data']['netflow_total']

# 2. Fallback manual
inflows = get_exchange_inflows(days=7)
outflows = get_exchange_outflows(days=7)
netflow_7d = inflows - outflows
```

---

## 6. Long/Short Ratio

**Descrição:**  
Razão entre contratos long e short abertos.

**Fórmula:**  
```
L/S Ratio = Open Interest Longs / Open Interest Shorts
```

**Fontes de dados:**
1. **Coinglass API:** `/api/futures/longShortRatio` (todos exchanges)
2. **Binance:** `/futures/data/globalLongShortAccountRatio`
3. **Agregação manual:** Somar OI de cada exchange

**Implementação:**
```python
# 1. Via Coinglass (agregado)
data = coinglass_api.get('/api/futures/longShortRatio', 
                        params={'symbol': 'BTC', 'interval': '7d'})
ls_ratio = data['ratio']

# 2. Via exchanges individuais
binance_ls = get_binance_ls_ratio()
bybit_ls = get_bybit_ls_ratio()
# Ponderar por volume OI de cada exchange
```

---

## 7. RSI Semanal

**Descrição:**  
Índice de Força Relativa no timeframe semanal.

**Fórmula:**  
```
RSI = 100 - (100 / (1 + RS))
RS = Média Ganhos(14) / Média Perdas(14)
```

**Fontes de dados:**
1. **OHLC Semanal:** CoinGecko `/coins/{id}/ohlc` → Binance API
2. **Cálculo:** pandas-ta library

**Implementação:**
```python
import pandas as pd
import pandas_ta as ta

# 1. Obter dados OHLC semanais (15+ semanas)
ohlc = get_weekly_ohlc(symbol='BTCUSDT', limit=20)

# 2. Calcular RSI
df = pd.DataFrame(ohlc)
df['rsi'] = ta.rsi(df['close'], length=14)

# 3. Valor atual
current_rsi = df['rsi'].iloc[-1]
```

---

## 📦 Configuração de Fallback

```python
INDICATORS_CONFIG = {
    'mvrv_z': {
        'sources': ['cryptoquant', 'glassnode', 'manual'],
        'cache_ttl': 3600,  # 1 hora
        'critical': True
    },
    'funding_rate': {
        'sources': ['coinglass', 'binance', 'weighted_avg'],
        'cache_ttl': 300,   # 5 min
        'critical': True
    }
}

def get_indicator_with_fallback(indicator_name):
    config = INDICATORS_CONFIG[indicator_name]
    
    for source in config['sources']:
        try:
            data = fetch_from_source(source, indicator_name)
            if validate_data(data):
                return data
        except Exception as e:
            log.warning(f"{source} failed: {e}")
            continue
    
    if config['critical']:
        raise DataUnavailableError(f"All sources failed for {indicator_name}")
    return None
```

---

## 🔧 Requisitos Técnicos

**Bibliotecas Python:**
```bash
pip install requests pandas pandas-ta numpy python-dotenv
```

**Rate Limits por Fonte:**
- CoinGecko Free: 50 calls/min
- Blockchain.com: 30 req/min
- CryptoQuant Free: 100/day
- Binance: 1200/min

**Cache Recomendado:**
- On-chain (MVRV, Realized): 1 hora
- Exchange flows: 15 minutos
- Funding/L-S: 5 minutos
- Preços: 1 minuto