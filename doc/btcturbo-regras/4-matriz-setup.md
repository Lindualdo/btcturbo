# EXECUÇÃO TÁTICA

**Pergunta Central:** "Quando e quanto adicionar ou realizar?"

## Matriz de Setups (Timeframe 4H)

### Setups de COMPRA (quando ciclo permite)
| Setup | Condições 4H | Confirmação | Ação | Tamanho |
|-------|--------------|-------------|------|---------|
| **Pullback Tendência** | RSI < 45 + EMA144 ±3% | Volume médio+ | COMPRAR | 30% |
| **Teste Suporte** | Toca EMA144 + Bounce | Martelo/Doji | COMPRAR | 25% |
| **Rompimento** | Fecha acima resistência | Volume alto | COMPRAR | 20% |
| **Oversold Extremo** | RSI < 30 | Divergência+ | COMPRAR | 40% |

### Setups de VENDA (quando ciclo sugere)
| Setup | Condições 4H | Confirmação | Ação | Tamanho |
|-------|--------------|-------------|------|---------|
| **Resistência** | RSI > 70 + Topo range | Rejeição | REALIZAR | 25% |
| **Exaustão** | 3 topos + Volume ↓ | Bear div | REALIZAR | 30% |
| **Take Profit** | Lucro > 30% posição | Qualquer | REALIZAR | 20% |
| **Stop Gain** | Target atingido | Qualquer | REALIZAR | 50% |

---



### Oportunidades Raras (Força entrada)
- MVRV < 0.7 + RSI < 25 → All-in histórico
- Capitulação (volume 5x + queda 30%) → Comprar máximo permitido
- 3+ meses lateralizado + rompimento → Entrada agressiva

---

## 🔧 SEÇÃO OPERACIONAL - Sugestões de Implementação

### 1. Gestão de Stop Loss

#### Opção A: Stop por Estrutura (Price Action)
- **Bottom/Acumulação**: Abaixo da mínima da semana
- **Bull Inicial**: Abaixo do último pivot de alta
- **Bull Maduro**: Abaixo da EMA 34 semanal
- **Euforia**: Stop mais apertado, abaixo da EMA 17

#### Opção B: Stop por ATR (Dinâmico)
```
Stop Distance = ATR(14) × Multiplicador
- Bottom: 2.5 × ATR
- Acumulação: 2.0 × ATR  
- Bull: 1.5 × ATR
- Euforia: 1.0 × ATR
```

#### Opção C: Stop Móvel por Médias
- Posição longa: Stop abaixo da EMA mais relevante
  - Agressivo: EMA 17 (4H)
  - Moderado: EMA 34 (Diário)
  - Conservador: EMA 144 (Semanal)

### 2. Rotina Operacional Sugerida

#### Check Matinal (5 min)
1. Verificar Health Factor
2. Score de Mercado mudou de faixa?
3. Algum alerta de preço atingido?

#### Análise 4H (10 min)
1. Setup formando no gráfico?
2. Confluência com ciclo atual?
3. Ajustar stops se necessário

#### Revisão Semanal (30 min)
1. Recalcular todos os scores
2. Reavaliar ciclo de mercado
3. Planejar semana (níveis de entrada/saída)
4. Ajustar tamanho de posição se mudou ciclo

### 3. Sistema de Alertas Recomendados

#### Alertas Críticos
- Health Factor < 1.3
- Score Risco < 40
- Mudança de ciclo
- Stop loss se aproximando

#### Alertas Táticos
- RSI 4H < 30 ou > 70
- Preço nas EMAs chave
- Setup 4H detectado
- Target de lucro atingido

### 4. Registro e Melhoria Contínua

#### Trade Journal Mínimo
- Data/hora entrada
- Ciclo no momento
- Setup usado
- Tamanho posição
- Stop definido
- Resultado
- Observações

#### Métricas de Performance
- Win rate por ciclo
- Win rate por setup
- Risco/retorno médio
- Drawdown máximo por ciclo

---

## 📱 Widget Decisão Simplificada (ATUALIZADO)

```
┌─────────────────────────────────┐
│ CICLO: BULL INICIAL             │
│ MVRV: 1.45                      │
│ Alavancagem: 1.8x/2.5x ✅       │
│ Health Factor: 1.85 ✅          │
│                                 │
│ 💡 AÇÃO AGORA:                  │
│ [COMPRAR 25%]                   │
│ "Pullback na EMA144 4H"         │
│                                 │
│ Stop sugerido: $92,500 (-8%)    │
│ Próxima revisão: 4 horas        │
└─────────────────────────────────┘
```

---

*Sistema v5.3 - Correções aplicadas + Seção operacional adicionada*