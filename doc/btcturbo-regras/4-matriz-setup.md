# EXECUÇÃO TÁTICA

**Pergunta Central:** "Quando e quanto adicionar ou realizar?"

## Matriz de Setups (Timeframe 4H)

### Setups de COMPRA
| Setup | Condições 4H | Confirmação | Ação | Tamanho |
|-------|--------------|-------------|------|---------|
| **Pullback Tendência** | RSI < 45 + EMA144 ±3% | Volume médio+ | COMPRAR | 30% |
| **Teste Suporte** | Toca EMA144 + Bounce | Martelo/Doji | COMPRAR | 25% |
| **Rompimento** | Fecha acima resistência | Volume alto | COMPRAR | 20% |
| **Oversold Extremo** | RSI < 30 | Divergência+ | COMPRAR | 40% |

### Setups de VENDA
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