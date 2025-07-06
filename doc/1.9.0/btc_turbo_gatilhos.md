# BTC TURBO - SISTEMA DE GATILHOS E ALERTAS

## 1. IDENTIFICAÇÃO DE CONGESTÃO

### Indicadores Primários
- **Bollinger Bands (Diário)**
  - Largura < 5%: Congestão extrema
  - Largura < 10%: Congestão normal
  - Squeeze por 7+ dias: Breakout iminente

- **ATR/Preço (14 dias)**
  - < 2%: Baixa volatilidade
  - < 1.5%: Compressão extrema
  - Alerta: Queda 50% em 7 dias

- **Volume**
  - < 70% média 30d: Congestão confirmada
  - Spike > 150%: Possível breakout

### Ações em Congestão
- Reduzir alavancagem em 0.5x
- Preparar ordens nos extremos do range
- Monitorar convergência de médias móveis

## 2. ANTECIPAÇÃO DE BREAKOUTS

### Sinais Técnicos
- **VPVR (Volume Profile)**
  - Rompimento de HVN (High Volume Node)
  - Preço em LVN (Low Volume Node) = movimento rápido

- **OBV (On Balance Volume)**
  - Divergência alta com preço = Breakout bullish
  - Nova máxima antes do preço = Confirmação

- **Ichimoku (Diário)**
  - Preço > Kumo + Tenkan > Kijun = Bull
  - Kumo twist ahead = Mudança tendência

### Sinais On-chain
- **Exchange Netflows**
  - Saídas > 10k BTC/dia = Bullish
  - Entradas > 10k BTC/dia = Bearish

- **Spent Output Age Bands**
  - Moedas 6m+ movendo = Alerta
  - Moedas 1y+ movendo = Perigo

## 3. AJUSTES DINÂMICOS DE ALAVANCAGEM

### RSI Mensal
- > 80: Reduzir 1x da alavancagem atual
- > 85: Máximo 1x permitido
- < 30: Aumentar 0.5x (se score on-chain > 60)

### Distância EMA 200 Semanal
- > 200%: Reduzir 0.5x
- > 250%: Reduzir 1x
- > 300%: Máximo 1x permitido
- < 50%: Aumentar 0.5x (se tendência bull)

### Funding Rate (perpétuos)
- > 0.1%/8h: Reduzir 0.5x
- > 0.2%/8h: Máximo 1x
- < -0.05%/8h: Oportunidade long

## 4. ALERTAS DE RISCO

### Movimentação de Baleias
- **Whale Alert (1000+ BTC)**
  - Exchange deposits > 5k BTC = Alerta vermelho
  - Múltiplas transações/hora = Possível dump

- **Dormancy Flow**
  - Spike > 500k = Holders antigos vendendo
  - Tendência crescente 3d = Reduzir exposição

### Mineradores
- **Hash Ribbons**
  - Capitulação (MA30 < MA60) = Oportunidade
  - Recuperação = Sinal de compra forte

- **Miner Reserve**
  - Queda > 5k BTC/mês = Pressão vendedora
  - Estável/crescente = Bullish

### Liquidações
- **Open Interest**
  - Crescimento > 20%/semana = Sobreaquecido
  - Funding + OI alto = Flush iminente

- **Liquidation Heatmap**
  - Clusters > $1B próximos = Imã de preço
  - Wicks para clusters = Oportunidade

## 5. SINAIS DE EXAUSTÃO

### Topo
- **TD Sequential**: 9 ou 13 sell setup
- **Divergência RSI** diário + semanal
- **Volume** decrescente em novas máximas
- **Long/Short Ratio** > 2.5
- **Greed Index** > 85 por 7+ dias

### Fundo
- **TD Sequential**: 9 ou 13 buy setup
- **RSI** < 30 em múltiplos timeframes
- **Volume** climático em sell-off
- **Long/Short Ratio** < 0.7
- **Fear Index** < 20 por 7+ dias

## 6. SISTEMA DE PRIORIDADE

### 🔴 Ação Imediata (< 1 hora)
- Exchange inflow > 10k BTC
- Funding > 0.2%
- Liquidation cluster < 3% distância
- RSI > 85 + Score on-chain < 50

### 🟡 Ação em 24h
- Divergência OBV
- Hash ribbon capitulação
- Bollinger squeeze 7+ dias
- Score on-chain mudou faixa

### 🟢 Monitorar
- SOAB moedas antigas
- Tendência dormancy
- Convergência médias
- Volume decrescente

## 7. CHECKLIST PRÉ-BREAKOUT

□ Bollinger Bands contraídas < 7%  
□ Volume > 50% abaixo média  
□ RSI entre 45-55 (neutro)  
□ OBV em nova máxima/mínima  
□ Exchange netflow favorável  
□ Funding rate neutro  
□ Liquidation clusters identificados  

**3+ checks = Preparar para movimento**

## 8. PROTEÇÃO ADICIONAL

### Stop Dinâmico por Volatilidade
| ATR/Preço | Stop Loss |
|-----------|-----------|
| > 5% | -12% posição |
| 3-5% | -10% posição |
| 2-3% | -8% posição |
| < 2% | -6% posição |

### Circuit Breaker
- Queda > 15% em 24h: Zerar alavancagem
- Queda > 25% em 48h: Reduzir satélite 50%
- Exchange hack/FUD: Exit imediato

## 9. ALERTAS AUTOMATIZADOS

### Configurar Notificações
1. **TradingView**: RSI, Bollinger, Volume
2. **Glassnode**: SOAB, Exchange flows, Dormancy
3. **CryptoQuant**: Miner flows, Funding, OI
4. **Whale Alert**: Transações > 1000 BTC
5. **Coinglass**: Liquidation map, Long/Short

### Frequência de Revisão
- **Horário**: Funding rate, liquidations
- **Diário**: RSI, distância EMA, volume
- **Semanal**: Hash ribbons, SOAB, tendências
- **Mensal**: Macro scores, ciclo geral