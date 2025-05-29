# BTC Hold Alavancado - Sistema de Score v4.0
-Objetivo: Sistema modular de análise de indicadores do BTC com score e alertas automatizados.

## 📊 Estrutura do Sistema v 3.0

```
SISTEMA v3.0
├── Ciclo (40%)
│   ├── MVRV Z-Score (20%)
│   ├── Realized Price Ratio (15%)
│   └── Puell Multiple (5%)
├── Momentum (25%)
│   ├── RSI Semanal (10%)
│   ├── Funding Rates 7D (8%)
│   ├── Open Interest Change 30D (4%)
│   └── Long/Short Ratio (3%)
├── Risco (15%)
│   ├── Distância do Liquidation (6%)
│   ├── Health Factor AAVE (4%)
│   ├── Exchange Netflow 7D (3%)
│   └── Stablecoin Supply Ratio (2%)
└── Técnico (20%)
    ├── Sistema EMAs Multi-TF (15%)
    │   ├── Estrutura/Alinhamento EMAs (7%)
    │   └── Posição do Preço vs EMAs (8%)
    └── Padrões Gráficos (5%)

```
---

## 📊 Estrutura do Sistema v 4.0

```
SISTEMA v4.0 FINAL
├── CICLO (40%)
│   ├── MVRV Z-Score (20%)
│   ├── Realized Price Ratio (15%)
│   └── Puell Multiple (5%)
│
├── MOMENTUM (30%)
│   ├── RSI Semanal (10%)
│   ├── Funding Rates (8%)
│   ├── OI Change (4%)
│   ├── Long/Short Ratio (3%)
│   ├── Exchange Netflow (3%)
│   └── SSR (2%)
│
├── RISCO (10%) # Já ajustado
│   ├── Distância Liquidação (5%)
│   └── Health Factor (5%)
│
└── TÉCNICO (20%)
    ├── Sistema EMAs (15%)
    └── Padrões Gráficos (5%)

+ ALERTAS SISTÊMICOS (sem score)
  ├── WBTC Depeg
  ├── Arbitrum Status
  └── AAVE Protocol

```
---


## 🎯 Escala de Classificação (0-10)

| Score | Classificação | Descrição | Kelly % |
|-------|--------------|-----------|---------|
| 0-2 | **Crítico** | Risco extremo, ação imediata | 0% |
| 2-4 | **Ruim** | Condições desfavoráveis | 10% |
| 4-6 | **Neutro** | Mercado equilibrado | 25% |
| 6-8 | **Bom** | Condições favoráveis | 50% |
| 8-10 | **Ótimo** | Oportunidade excepcional | 75% |

---

## 📈 1. CICLO (40% do peso total)

### MVRV Z-Score (20%)
**Fórmula**: `(Market Value - Realized Value) / Std Dev`
**Fonte**: Glassnode, CryptoQuant

| Z-Score | Score | Classificação |
|---------|-------|--------------|
| < 0 | 9-10 | Ótimo |
| 0-2 | 7-8 | Bom |
| 2-4 | 5-6 | Neutro |
| 4-6 | 3-4 | Ruim |
| > 6 | 0-2 | Crítico |

### Realized Price Ratio (15%)
**Fórmula**: `Preço BTC / Realized Price`
**Fonte**: Glassnode, LookIntoBitcoin

| Ratio | Score | Classificação |
|-------|-------|--------------|
| < 0.7 | 9-10 | Ótimo |
| 0.7-1.0 | 7-8 | Bom |
| 1.0-1.5 | 5-6 | Neutro |
| 1.5-2.5 | 3-4 | Ruim |
| > 2.5 | 0-2 | Crítico |

### Puell Multiple (5%) [NOVO]
**Fórmula**: `(Mineração Diária USD) / (MA 365 dias)`
**Fonte**: Glassnode, LookIntoBitcoin

| Multiple | Score | Classificação |
|----------|-------|--------------|
| < 0.5 | 9-10 | Ótimo |
| 0.5-1.0 | 7-8 | Bom |
| 1.0-2.0 | 5-6 | Neutro |
| 2.0-4.0 | 3-4 | Ruim |
| > 4.0 | 0-2 | Crítico |

---

## 📊 2. MOMENTUM (25% do peso total)

### RSI Semanal (10%)
**Fonte**: TradingView, Glassnode

| RSI | Score | Classificação |
|-----|-------|--------------|
| < 30 | 9-10 | Ótimo |
| 30-45 | 7-8 | Bom |
| 45-55 | 5-6 | Neutro |
| 55-70 | 3-4 | Ruim |
| > 70 | 0-2 | Crítico |

### Funding Rates - Média 7D (8%)
**Fonte**: Coinglass, Glassnode

| Funding Rate | Score | Classificação |
|--------------|-------|--------------|
| < -0.05% | 9-10 | Ótimo |
| -0.05% a 0% | 7-8 | Bom |
| 0% a 0.02% | 5-6 | Neutro |
| 0.02% a 0.1% | 3-4 | Ruim |
| > 0.1% | 0-2 | Crítico |

### Open Interest Change 30D (4%)
**Fórmula**: `(OI Atual - OI 30D atrás) / OI 30D atrás × 100`

| OI Change % | Score | Classificação |
|-------------|-------|--------------|
| < -30% | 9-10 | Ótimo |
| -30% a -10% | 7-8 | Bom |
| -10% a +20% | 5-6 | Neutro |
| +20% a +50% | 3-4 | Ruim |
| > +50% | 0-2 | Crítico |

### Long/Short Ratio (3%) [NOVO]
**Fonte**: Coinglass, Binance

| L/S Ratio | Score | Classificação |
|-----------|-------|--------------|
| < 0.8 | 9-10 | Ótimo |
| 0.8-0.95 | 7-8 | Bom |
| 0.95-1.05 | 5-6 | Neutro |
| 1.05-1.3 | 3-4 | Ruim |
| > 1.3 | 0-2 | Crítico |

---

## ⚠️ 3. RISCO (15% do peso total)

### Distância do Liquidation (6%)
**Fórmula**: `((Preço Atual - Preço Liquidação) / Preço Atual) × 100`

| Distância % | Score | Classificação |
|-------------|-------|--------------|
| > 50% | 9-10 | Ótimo |
| 30-50% | 7-8 | Bom |
| 20-30% | 5-6 | Neutro |
| 10-20% | 3-4 | Ruim |
| < 10% | 0-2 | Crítico |

### Health Factor AAVE (4%)

| Health Factor | Score | Classificação |
|---------------|-------|--------------|
| > 2.0 | 9-10 | Ótimo |
| 1.5-2.0 | 7-8 | Bom |
| 1.3-1.5 | 5-6 | Neutro |
| 1.1-1.3 | 3-4 | Ruim |
| < 1.1 | 0-2 | Crítico |

### Exchange Netflow 7D (3%)
**Fonte**: CryptoQuant, Glassnode

| Netflow | Score | Classificação |
|---------|-------|--------------|
| < -50k BTC | 9-10 | Ótimo |
| -50k a -10k | 7-8 | Bom |
| -10k a +10k | 5-6 | Neutro |
| +10k a +50k | 3-4 | Ruim |
| > +50k BTC | 0-2 | Crítico |

### Stablecoin Supply Ratio (2%) [NOVO]
**Fórmula**: `Market Cap Stablecoins / Market Cap BTC`

| SSR | Score | Classificação |
|-----|-------|--------------|
| > 15% | 9-10 | Ótimo |
| 10-15% | 7-8 | Bom |
| 5-10% | 5-6 | Neutro |
| 2-5% | 3-4 | Ruim |
| < 2% | 0-2 | Crítico |

---

## 📉 4. TÉCNICO (20% do peso total)

### Sistema EMAs Multi-Timeframe (15%)

#### Metodologia de Cálculo por Timeframe

**A. Bloco Alinhamento/Estrutura das EMAs (7%)**

| Par de EMAs | Representa | Pontuação |
|-------------|------------|-----------|
| EMA 17 > EMA 34 | Curtíssimo prazo | +1 ponto |
| EMA 34 > EMA 144 | Curto prazo | +2 pontos |
| EMA 144 > EMA 305 | Médio prazo | +3 pontos |
| EMA 305 > EMA 610 | Longo prazo | +4 pontos |

**Pontuação máxima**: 10 pontos

**B. Bloco Posição do Preço vs EMAs (8%)**

| EMA | Função Técnica | Pontuação |
|-----|----------------|-----------|
| Preço > EMA 17 | Momentum imediato | +1 |
| Preço > EMA 34 | Tendência curta | +1 |
| Preço > EMA 144 | Tendência média | +2 |
| Preço > EMA 305 | Macro estrutura | +3 |
| Preço > EMA 610 | Base de ciclo | +3 |

**Pontuação máxima**: 10 pontos

#### Consolidação Multi-Timeframe

| Timeframe | Peso | Importância |
|-----------|------|-------------|
| 1W (Semanal) | 50% | Estrutura principal |
| 1D (Diário) | 25% | Tendência primária |
| 4H | 15% | Médio prazo |
| 1H | 10% | Curto prazo |

**Fórmula de Cálculo**:
```
Score_TF = (Alinhamento + Posição) / 20 × 10
Score_Final = (1W × 0.5) + (1D × 0.25) + (4H × 0.15) + (1H × 0.10)
```

#### Interpretação do Score EMAs

| Score | Classificação | Descrição |
|-------|--------------|-----------|
| 8.1-10.0 | Tendência Forte | Bull market confirmado |
| 6.1-8.0 | Correção Saudável | Pullback em tendência de alta |
| 4.1-6.0 | Neutro | Lateralização ou transição |
| 2.1-4.0 | Reversão | Mudança de tendência |
| 0.0-2.0 | Bear Confirmado | Tendência de baixa estabelecida |

### Padrões Gráficos (5%)
**Análise**: Manual ou algoritmo de detecção

| Padrão | Score | Confiabilidade |
|--------|-------|----------------|
| Double Bottom / Inverse H&S | 8-10 | Alta |
| Bull Flag / Ascending Triangle | 7-8 | Média-Alta |
| Sem padrão claro | 4-6 | N/A |
| Bear Flag / Descending Triangle | 2-3 | Média-Alta |
| Head & Shoulders / Double Top | 0-2 | Alta |

---

## 🔔 Sistema de Alertas Aprimorado

### Alertas Críticos
```javascript
// Score Based
if (score < 2) alert("CRÍTICO: Zerar alavancagem imediatamente");
if (score_change_24h > 3) alert("Mudança drástica de regime");

// Risk Based
if (health_factor < 1.15) alert("PERIGO: Liquidação próxima");
if (dist_liquidation < 15) alert("ATENÇÃO: Revisar posição");

// Market Based
if (funding_rate > 0.1) alert("EUFORIA: Considerar redução");
if (mvrv_z > 6) alert("TOPO: Preparar saída gradual");

// Technical Based
if (price_crosses_ema200) alert("Mudança de tendência principal");
if (ema_death_cross) alert("Death Cross: Bear market provável");
```

### Alertas de Divergência
```javascript
// Divergência Alta-Baixa
if (price_new_high && rsi < 50) {
    alert("DIVERGÊNCIA NEGATIVA: Topo provável");
}

// Divergência Volume
if (price_up && volume_down) {
    alert("Rally sem volume: Cautela");
}

// Divergência On-Chain
if (price_up && exchange_inflow > 50k) {
    alert("Distribuição detectada");
}
```

### Alertas de Oportunidade
```javascript
// Capitulação
if (mvrv_z < 0 && funding < -0.1) {
    alert("CAPITULAÇÃO: Oportunidade histórica");
}

// Acumulação
if (exchange_outflow > 50k && rsi < 40) {
    alert("Smart money acumulando");
}
```

---

## ⚖️ Ajustes Dinâmicos de Peso

### Por Regime de Mercado
```javascript
function ajustarPesos(mvrv_z_score) {
    if (mvrv_z_score < 0) {
        // Bear Extremo
        return {
            ciclo: 0.50,      // +10%
            momentum: 0.20,   // -5%
            risco: 0.10,      // -5%
            tecnico: 0.20     // 0%
        };
    } else if (mvrv_z_score > 6) {
        // Bull Extremo
        return {
            ciclo: 0.30,      // -10%
            momentum: 0.30,   // +5%
            risco: 0.25,      // +10%
            tecnico: 0.15     // -5%
        };
    } else {
        // Neutro
        return {
            ciclo: 0.40,
            momentum: 0.25,
            risco: 0.15,
            tecnico: 0.20
        };
    }
}
```

### Por Volatilidade
```javascript
function ajustarPorVolatilidade(btc_volatility_30d) {
    if (btc_volatility_30d > 80) {
        // Alta volatilidade
        peso_risco *= 1.5;
        peso_tecnico *= 1.2;
    } else if (btc_volatility_30d < 30) {
        // Baixa volatilidade
        peso_ciclo *= 1.2;
        peso_momentum *= 0.8;
    }
}
```

---

## 📊 Score de Volatilidade (Modificador)

### Bitcoin Volatility Index (BVOL)
```javascript
function calcularModificadorVolatilidade(bvol) {
    if (bvol < 30) return 1.1;       // Baixa vol = bonus
    if (bvol < 50) return 1.0;       // Normal
    if (bvol < 80) return 0.9;       // Alta vol = penalidade
    if (bvol >= 80) return 0.8;      // Vol extrema
}

// Aplicação
score_final = score_base * modificador_volatilidade;
kelly_allocation = kelly_base * modificador_volatilidade;
```

---

## 🎯 Modelo de Alocação Core-Satellite

### Estrutura Base
```
PATRIMÔNIO TOTAL BTC
├── Core Position (50%) - HOLD PURO
│   └── Nunca alavancado
└── Satellite Position (50%) - HOLD ALAVANCADO
    └── Aplicar sistema de score
```

### Tabela de Aplicação Kelly
| Score | Kelly % | Core (BTC) | Satellite (BTC) | Total Exposição | Alavancagem |
|-------|---------|------------|-----------------|-----------------|-------------|
| 0-2   | 0%      | 1.0        | 0.0             | 1.0x            | 1.0x        |
| 2-4   | 10%     | 1.0        | 0.1             | 1.07x           | 1.07x       |
| 4-6   | 25%     | 1.0        | 0.25            | 1.17x           | 1.17x       |
| 6-8   | 50%     | 1.0        | 0.50            | 1.35x           | 1.35x       |
| 8-10  | 75%     | 1.0        | 0.75            | 1.53x           | 1.53x       |

---

## 📋 Padrão de Saída JSON

```json
{
  "timestamp": "2025-05-25T14:30:00Z",
  "score_final": 5.85,
  "score_ajustado": 5.27,
  "modificador_volatilidade": 0.9,
  "classificacao_geral": "Neutro",
  "kelly_allocation": "25%",
  "acao_recomendada": "Manter posição conservadora",
  "alertas_ativos": [
    "Volatilidade elevada",
    "EMA200 como resistência"
  ],
  "pesos_dinamicos": {
    "ciclo": 0.40,
    "momentum": 0.25,
    "risco": 0.15,
    "tecnico": 0.20
  },
  "blocos": {
    "ciclo": {
      "peso": "40%",
      "score": 2.34,
      "indicadores": {
        "MVRV_Z": { "valor": 2.1, "score": 6.0 },
        "Realized_Ratio": { "valor": 1.3, "score": 5.5 },
        "Puell_Multiple": { "valor": 1.2, "score": 5.0 }
      }
    },
    "momentum": {
      "peso": "25%",
      "score": 1.46,
      "indicadores": {
        "RSI_Semanal": { "valor": 52, "score": 5.5 },
        "Funding_Rates": { "valor": "0.015%", "score": 5.5 },
        "OI_Change": { "valor": "+12%", "score": 5.5 },
        "Long_Short_Ratio": { "valor": 0.98, "score": 6.0 }
      }
    },
    "risco": {
      "peso": "15%",
      "score": 0.93,
      "indicadores": {
        "Dist_Liquidacao": { "valor": "35%", "score": 7.0 },
        "Health_Factor": { "valor": 1.7, "score": 7.5 },
        "Exchange_Netflow": { "valor": "-5k", "score": 6.0 },
        "Stablecoin_Ratio": { "valor": "8%", "score": 6.0 }
      }
    },
    "tecnico": {
      "peso": "20%",
      "score": 1.12,
      "detalhamento": {
        "sistema_emas": {
          "peso": "15%",
          "score_consolidado": 9.6,
          "timeframes": {
            "1W": { "score": 10.0, "peso": "50%" },
            "1D": { "score": 10.0, "peso": "25%" },
            "4H": { "score": 9.0, "peso": "15%" },
            "1H": { "score": 7.5, "peso": "10%" }
          },
          "componentes": {
            "alinhamento": { "valor": "Bull perfeito", "score": 9.5 },
            "posicao": { "valor": "Acima de todas EMAs", "score": 9.7 }
          }
        },
        "padroes_graficos": {
          "peso": "5%",
          "padrao": "Bull Flag",
          "score": 7.0
        }
      }
    }
  }
}
```

---

## 🚨 Circuit Breakers

### Triggers Automáticos
| Condição | Ação | Prioridade |
|----------|------|------------|
| Score < 2 por 24h | Zerar alavancagem | CRÍTICA |
| HF < 1.2 | Deleveraging 50% | URGENTE |
| Queda > 15% em 4h | Pausar sistema 24h | ALTA |
| Funding > 0.3% por 3 dias | Máximo 25% alavancagem | MÉDIA |
| Score muda > 3 pontos em 24h | Revisão manual obrigatória | ALTA |

---

## 📝 Notas de Implementação

1. **Frequência de Cálculo**: 
   - Completo: 2x ao dia (00h e 12h UTC)
   - Health Factor: A cada hora
   - Alertas críticos: Real-time

2. **Prioridade de Dados**:
   - Tier 1: MVRV, Sistema EMAs, Health Factor
   - Tier 2: RSI, Funding, Exchange Flow
   - Tier 3: Padrões, Puell, Stablecoin

3. **Fallback**:
   - Se indicador indisponível, usar peso 0
   - Recalcular proporcionalmente outros

4. **Sistema EMAs**:
   - Fonte principal: TradingView
   - EMAs utilizadas: 17, 34, 144, 305, 610
   - Timeframes: 1W, 1D, 4H, 1H

---

*Versão 3.0 - Sistema com EMAs Multi-Timeframe Integrado*
*Atualizada em 26/05/2025*