# Sistema BTC - Três Camadas

## CAMADA 1: TENDÊNCIA (CONTEXTO MACRO)

### Estados de Tendência:
- **BULL FORTE (80-100)**: EMA21 > EMA55 > EMA100 > EMA200 + ADX > 25
- **BULL (60-79)**: EMA21 > EMA55 > EMA200 + MACD positivo
- **NEUTRO (40-59)**: EMAs mistas ou flat
- **BEAR (20-39)**: EMA21 < EMA55 < EMA200 + MACD negativo
- **BEAR FORTE (0-19)**: EMA21 < EMA55 < EMA100 < EMA200 + ADX > 25

## CAMADA 2: SCORE DE PREÇO (0-10)

| Score | Distância EMA200 | RSI Mensal |
|-------|------------------|------------|
| 10 | < -20% | < 40 |
| 8-9 | -20% a 0% | 40-45 |
| 6-7 | 0% a +50% | 45-60 |
| 4-5 | +50% a +110% | 60-70 |
| 2-3 | +110% a +150% | 70-75 |
| 0-1 | > +150% | > 75 |

## MATRIZ COMBINATÓRIA DE EXECUÇÃO

### BULL FORTE + Score
- **Score 8-10**: Alavancagem 3x IMEDIATA
- **Score 6-7**: Alavancagem 2x + DCA agressivo
- **Score 4-5**: Hold 100% + trailing stop 3%
- **Score 2-3**: RP 60% em 24h
- **Score 0-1**: SAIR 80% HOJE

### BULL + Score
- **Score 8-10**: Alavancagem 2x + all-in
- **Score 6-7**: Posição 100% sem alavancagem
- **Score 4-5**: Hold 80% + stop loss
- **Score 2-3**: RP 40% gradual (3 dias)
- **Score 0-1**: RP 70% imediato

### NEUTRO + Score
- **Score 8-10**: DCA 100% em 3 tranches
- **Score 6-7**: Posição 70% + aguardar
- **Score 4-5**: Manter 50% líquido
- **Score 2-3**: Reduzir para 30%
- **Score 0-1**: Short 30% hedge

### BEAR + Score
- **Score 8-10**: Contra-trend 100% (sem alavancagem)
- **Score 6-7**: Acumular 60% silencioso
- **Score 4-5**: Cash 70% + ordens baixas
- **Score 2-3**: Short 40% swing
- **Score 0-1**: Short 60% + puts

### BEAR FORTE + Score
- **Score 8-10**: ALL-IN + Alavancagem 2x (reversão)
- **Score 6-7**: DCA máximo 80%
- **Score 4-5**: Aguardar com 80% cash
- **Score 2-3**: Hedge 50% posição
- **Score 0-1**: Hedge 100% ou flat

## CAMADA 3: SINAIS TÁTICOS (TIMING)

### 🟢 EXECUTAR COMPRA AGORA
- Hash Ribbons virando verde
- RSI 4h < 30 + divergência
- Exchange < 11% + volume spike
- ETF inflow > $500M

### 🔴 EXECUTAR VENDA AGORA
- Exchange inflow > $2B/24h
- Funding > 0.10% sustentado
- Dormancy > 1M BTC
- ETF outflow > $500M

### ⚡ AGUARDAR (1-3 dias)
- Bollinger squeeze
- Volume < 30% média
- Sem sinais claros

## EXECUÇÃO FINAL

1. **Identificar Tendência** (semanal)
2. **Calcular Score** (2x semana)
3. **Localizar na Matriz** = Ação base
4. **Verificar Sinais Táticos** (diário)
   - Sinal verde/vermelho = executar HOJE
   - Sem sinal = seguir prazo da matriz

### Exemplo Atual:
- Tendência: BULL FORTE (EMAs alinhadas)
- Score: 2 (118% acima EMA200)
- **Matriz: RP 60% em 24h**
- Sinal tático: Aguardando
- **Execução: Vender 60% nos próximos dias**

## STOP ATR MÓVEL (Proteção de Lucros)

### Quando Usar:
- Já posicionado e alavancado
- Score indica distribuir mas sem sinais táticos claros
- Mercado ainda em tendência forte

### Configuração:
```
Stop = Máxima - (ATR14 × Multiplicador)

BULL FORTE:
- Score 8-10: 5.0 × ATR
- Score 6-7: 4.0 × ATR
- Score 4-5: 3.0 × ATR
- Score 2-3: 2.5 × ATR
- Score 0-1: 2.0 × ATR

BEAR ou NEUTRO: -0.5 no multiplicador
```

### Ajustes:
- Recalcular diariamente usando nova máxima
- Stop só sobe, nunca desce (ratchet)
- Se volatilidade > 4%: adicionar 0.5 ao multiplicador

### Exemplo Prático:
- BTC em $100k, ATR = $2k
- Score 2 em Bull Forte = 2.5 × ATR
- Stop = $100k - ($2k × 2.5) = $95k
- Se BTC subir para $105k, stop sobe para $100k

**Vantagem**: Captura continuação inesperada enquanto protege lucros.