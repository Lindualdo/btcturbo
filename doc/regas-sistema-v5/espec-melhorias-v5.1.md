# Sistema BTC Hold Alavancado - Melhorias v5.1

## 📊 1. Ajuste de Pesos - Bloco CICLO

### Alteração: Substituir MVRV Z-Score por combinação MVRV + NUPL

**De:**
```
CICLO
├── MVRV Z-Score (25%)
├── Realized Price Ratio (20%)
└── Puell Multiple (5%)
```

**Para:**
```
CICLO
├── MVRV Z-Score (15%)    ← Reduzido
├── NUPL (10%)            ← Novo
├── Realized Price Ratio (20%)
└── Puell Multiple (5%)
```

**Justificativa:**
- MVRV tem lag significativo em topos (10-20% após pico)
- NUPL mais responsivo: >0.75 = euforia clara
- Diversificação reduz dependência de indicador único
- Histórico: MVRV errou topos 2021 e 2024

---

## 📈 2. Ajuste de Pesos - Sistema Geral

### Alteração: Aumentar peso da Análise Técnica

**De:**
```
├── CICLO: 50%
├── MOMENTUM: 20%
└── TÉCNICO: 30%
```

**Para:**
```
├── CICLO: 40%      ← Reduzido
├── MOMENTUM: 20%   ← Mantém
└── TÉCNICO: 40%    ← Aumentado
```

**Justificativa:**
- AT antecipa movimentos on-chain
- Setup atual (4 ATHs semanais) não capturado com peso 30%
- Price action é leading indicator
- Sistema atual muito conservador para momentum claro

```python
# NUPL > 0.75 = euforia/topo (score 1-2)
# NUPL 0.5-0.75 = sobrecomprado (score 3-4)  
# NUPL 0.25-0.5 = neutro (score 5-6)
# NUPL 0-0.25 = acumulação (score 7-8)
# NUPL < 0 = oversold extremo (score 9-10)
```

---

## 🎯 3. Modificadores de Momentum

### Novo: Bônus por Momentum Semanal

### trocar Exchange Net Flow por STH-SOPR manter mesmo peso

```python
def calcular_bonus_momentum():
    bonus = 0
    
    # Velas verdes consecutivas
    if consecutive_green_weekly >= 3:
        bonus += 5
        
    # ATH semanal
    if weekly_close == all_time_high:
        bonus += 3
        
    # Defesa de suporte psicológico
    if tested_and_held_round_number:
        bonus += 2
        
    return min(bonus, 10)  # Máximo 10 pontos
```

**Aplicação:** 
- Score Final = Score Base + Bonus Momentum
- Captura força técnica não refletida em on-chain

---

## 🔔 4. Novos Alertas Prioritários

### 4.1 Alertas de Oportunidade Técnica
```python
# Setup Técnico Forte
if consecutive_weekly_ath >= 3:
    alert("📈 Setup técnico forte - 3+ ATHs semanais")
    
if golden_cross_4h and score < 60:
    alert("⚡ Golden cross 4H com score neutro - divergência")
    
if price_test_psychological and held:
    alert("💪 Suporte psicológico defendido - força compradora")
```

### 4.2 Alertas de Divergência
```python
# Técnica vs On-chain
if technical_score > 80 and cycle_score < 50:
    alert("🔄 Divergência: Técnica forte, on-chain fraco")
    
if ema_alignment_perfect and mvrv > 3:
    alert("⚠️ EMAs perfeitas mas MVRV alto - cautela")
```

### 4.3 Alertas de Execução
```python
# Zona neutra com oportunidade
if ema_distance < 10 and rsi > 70:
    alert("📊 RSI alto em zona neutra - realizar parcial")
    
if ema_distance < 10 and rsi < 40:
    alert("🛒 RSI baixo em zona neutra - oportunidade compra")
```

---

## 💾 5. Indicadores no JSON de Análise

### Adicionar bloco `indicadores_timing`:

```json
{
    "indicadores_timing": {
        "bbw": {
            "valor": 7.2,
            "classificacao": "normal",
            "dias_comprimido": 0,
            "alerta_ativo": false
        },
        "mvrv": {
            "valor": 2.24,
            "z_score": 2.5,
            "fase": "bull_medio"
        },
        "funding_rate": {
            "atual": 0.042,
            "media_7d": 0.031,
            "tendencia": "estavel"
        },
        "momentum_semanal": {
            "velas_verdes_consecutivas": 4,
            "ath_semanal": true,
            "bonus_aplicado": 8
        }
    }
}
```

---

## 📝 6. Regras de Override

### Quando aplicar entrada discricional:

1. **Override Técnico Forte**
   - 4+ semanas ATH
   - EMAs alinhadas todos timeframes
   - Volume crescente
   - → Entrada 25% mesmo com score < 60

2. **Override de Proteção**
   - Qualquer alerta crítico
   - Health Factor < 1.5
   - → Reduzir independente de score

---

## 🚀 Implementação Prioritária

### Fase 1 (Imediato):
1. ✅ Sistema de alertas críticos (já implementado)
2. ⏳ Adicionar alertas de oportunidade técnica
3. ⏳ Incluir indicadores_timing no JSON

### Fase 2 (1 semana):
1. ⏳ Ajustar pesos MVRV/NUPL
2. ⏳ Implementar bonus momentum
3. ⏳ Webhook Telegram

### Fase 3 (2 semanas):
1. ⏳ Aumentar peso técnico para 40%
2. ⏳ Dashboard básico
3. ⏳ Histórico de alertas

---

## 📊 Impacto Esperado

Com as alterações:
- Score atual subiria de 57 para ~64
- Captura melhor momentos como atual
- Mantém proteção em extremos
- Balanceia leading (técnica) com lagging (on-chain)

---

# Tabela de Score SOPR (Spent Output Profit Ratio)

## Indicador: SOPR
**Fonte:** Glassnode  
**Endpoint:** `/v1/metrics/indicators/sopr`  
**Peso no Sistema:** 10% (dentro do bloco Momentum que tem peso 20%)

## Tabela de Conversão SOPR → Score

| Faixa SOPR | Score | Classificação | Interpretação de Mercado |
|------------|-------|---------------|--------------------------|
| < 0.90 | 10 | Capitulação Extrema | Pânico total, fundo histórico provável |
| 0.90 - 0.93 | 9 | Capitulação Forte | Vendas com grandes perdas |
| 0.93 - 0.95 | 8 | Capitulação | Pressão vendedora intensa |
| 0.95 - 0.97 | 7 | Pressão Alta | Realizando perdas moderadas |
| 0.97 - 0.99 | 6 | Pressão Moderada | Vendas no prejuízo leve |
| 0.99 - 1.00 | 5 | Pressão Leve | Mercado indeciso |
| 1.00 - 1.01 | 5 | Neutro | Equilíbrio entre lucro/perda |
| 1.01 - 1.02 | 4 | Realização Leve | Pequenos lucros realizados |
| 1.02 - 1.03 | 3 | Realização Moderada | Tomada de lucro saudável |
| 1.03 - 1.05 | 2 | Realização Alta | Forte tomada de lucro |
| 1.05 - 1.08 | 1 | Ganância | Realização excessiva |
| > 1.08 | 0 | Ganância Extrema | Euforia, topo local provável |

## Fórmula de Cálculo

```python
def calcular_score_sopr(valor_sopr):
    if valor_sopr < 0.90:
        return 10
    elif valor_sopr < 0.93:
        return 9
    elif valor_sopr < 0.95:
        return 8
    elif valor_sopr < 0.97:
        return 7
    elif valor_sopr < 0.99:
        return 6
    elif valor_sopr <= 1.01:
        return 5
    elif valor_sopr < 1.02:
        return 4
    elif valor_sopr < 1.03:
        return 3
    elif valor_sopr < 1.05:
        return 2
    elif valor_sopr < 1.08:
        return 1
    else:
        return 0
```

## Interpretação para Trading

### Zonas de Ação
- **Score 8-10**: Zona de compra agressiva (capitulação)
- **Score 6-7**: Zona de compra moderada
- **Score 4-5**: Zona neutra (aguardar)
- **Score 2-3**: Zona de realização parcial
- **Score 0-1**: Zona de redução/saída

### Combinação com Outros Indicadores
- SOPR < 0.97 + RSI < 30 = **Setup de fundo forte**
- SOPR > 1.05 + RSI > 70 = **Setup de topo provável**
- SOPR ~1.00 = **Usar outros indicadores para decisão**

## Notas Importantes

1. **Filtragem de Ruído**: Ignorar picos extremos únicos (>1.5 ou <0.5)
2. **Confirmação**: Sempre confirmar com pelo menos 2 dias consecutivos na mesma zona
3. **Timeframe**: Usar dados diários, não intraday
4. **Limitações**: SOPR pode dar sinais falsos em mercados laterais prolongados

---

*Última atualização: Sistema v5.1*

*Documento de melhorias v5.1 - Sistema mais responsivo mantendo proteções*