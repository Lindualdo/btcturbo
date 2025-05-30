# 📊 Documentação de Indicadores On-Chain e Técnicos BTC (Versão Pública)
Objetibo: gerar os indicadores de forma confiável nível padrão ouro (Glasnode)
Coletar dados reais - Sem dados fixo (Hardcoded) - sem suposições -  fallback para fontes de coleta -  não encontrou gera erro

---

## 1. MVRV Z-Score

**Descrição:**  
Mede o quão valorizado/desvalorizado o Bitcoin está em relação ao seu valor realizado (quanto foi pago em média por cada BTC em circulação), ajustado pela volatilidade histórica.

**Fórmula:**  
`MVRV Z-Score = (Market Cap - Realized Cap) / StdDev(Market Cap)`

**Onde buscar os dados:**
- **Market Cap:** CoinGecko, CoinMarketCap, Blockchair
- **Realized Cap:** Glassnode (grátis limitado), IntoTheBlock (grátis limitado), ou cálculo manual via blocos/UTXO (blockchain explorer)
- **Desvio padrão (StdDev):** Calcule a série histórica do Market Cap, usando dados diários (CoinGecko/CMC/Blockchair)

**Como calcular (passo a passo):**
1. Pegue o valor atual do Market Cap do BTC (preço x supply circulante).
2. Pegue o Realized Cap (se disponível, ou some o preço pago por cada BTC em circulação – geralmente só nas plataformas especializadas).
3. Calcule o desvio padrão (StdDev) do Market Cap em toda a série histórica disponível.
4. Subtraia o Realized Cap do Market Cap.
5. Divida o resultado pelo desvio padrão calculado.

---

## 2. Realized Price Ratio

**Descrição:**  
Mostra o quanto o preço atual do Bitcoin está acima ou abaixo do preço médio "realizado" (o preço médio de compra das moedas em circulação).

**Fórmula:**  
`Realized Price Ratio = Preço BTC / Realized Price`

**Onde buscar os dados:**
- **Preço BTC:** CoinGecko, CoinMarketCap, TradingView
- **Realized Price:** Glassnode (free limitado), LookIntoBitcoin

**Como calcular (passo a passo):**
1. Obtenha o preço atual do Bitcoin.
2. Obtenha o Realized Price (pode usar Glassnode free ou LookIntoBitcoin).
3. Divida o preço atual pelo Realized Price.

---

## 3. Puell Multiple

**Descrição:**  
Avalia o quanto os mineradores estão recebendo em relação à média histórica. Valores muito altos/baixos sugerem extremos de mercado.

**Fórmula:**  
`Puell Multiple = Emissão diária em USD / Média móvel de 365 dias da emissão diária em USD`

**Onde buscar os dados:**
- **Emissão diária em USD:** Blockchain.com (Receita de mineradores), Blockchair
- **Média móvel 365 dias:** Calcule manualmente a média móvel usando dados históricos de emissão

**Como calcular (passo a passo):**
1. Pegue quanto foi minerado em BTC nas últimas 24h e multiplique pelo preço do BTC (valor em USD).
2. Calcule a média da emissão diária em USD dos últimos 365 dias.
3. Divida a emissão diária atual pela média móvel anual.

---

## 4. Funding Rates

**Descrição:**  
Taxa periódica paga entre traders em contratos perpétuos de futuros (paga/recebe conforme posição). Sinaliza sentimento de euforia/pânico.

**Fórmula:**  
*Não tem fórmula fixa (é a taxa publicada pelas exchanges, normalmente a cada 8h).*

**Onde buscar os dados:**
- [Coinglass](https://coinglass.com)
- [Coinalyze](https://coinalyze.net)
- Binance/Bybit/OKX (direto via API/website)

**Como calcular (passo a passo):**
1. Consulte o painel da Coinglass ou Coinalyze, filtro para BTC.
2. Pegue o valor atual ou média das últimas 24h/7d (como preferir).
3. Use diretamente o valor mostrado.

---

## 5. Exchange Netflow 7D

**Descrição:**  
Saldo líquido de entradas e saídas de BTC nas exchanges em 7 dias. Sinaliza pressão de compra/venda.

**Fórmula:**  
`Netflow 7D = Entradas BTC nas exchanges (7d) - Saídas BTC das exchanges (7d)`

**Onde buscar os dados:**
- [CryptoQuant](https://cryptoquant.com/asset/btc/chart/exchange-flows/exchange-netflow-total)
- Glassnode (free limitado)
- IntoTheBlock (só parte do dado)

**Como calcular (passo a passo):**
1. Pegue o total de BTC enviados para exchanges nos últimos 7 dias.
2. Pegue o total de BTC retirados das exchanges nos últimos 7 dias.
3. Subtraia: (Entradas - Saídas).
   - Valor negativo = pressão de compra
   - Valor positivo = pressão de venda

---

## 6. Long/Short Ratio

**Descrição:**  
Mostra a razão entre posições compradas (long) e vendidas (short) nos futuros. Sentimento de mercado (otimismo/pessimismo).

**Fórmula:**  
`Long/Short Ratio = Posições Longas Abertas / Posições Curtas Abertas`

**Onde buscar os dados:**
- Coinglass
- Coinalyze
- Direto das exchanges (Binance Futures, Bybit, OKX)

**Como calcular (passo a passo):**
1. Consulte Coinglass/Coinalyze para BTC.
2. Pegue o número total de contratos longos e contratos curtos abertos.
3. Divida o número de longs pelo número de shorts.

---

## 7. RSI Semanal

**Descrição:**  
Índice de Força Relativa calculado no gráfico semanal. Mede sobrecompra/sobrevenda.

**Fórmula:**  
`RSI = 100 - (100 / (1 + RS))`  
Onde: `RS = Média dos ganhos / Média das perdas (últimos 14 candles)`

**Onde buscar os dados:**
- TradingView (gráfico semanal, RSI padrão)
- CoinMarketCap (painéis de análise técnica)

**Como calcular (passo a passo):**
1. Abra o gráfico BTCUSD no TradingView.
2. Altere para período semanal (“1W”).
3. Adicione o indicador RSI (default = 14).
4. Leia o valor exibido na plataforma.
