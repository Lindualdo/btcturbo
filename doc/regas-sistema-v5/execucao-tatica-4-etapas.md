# 🎯 Fluxo Principal - 4 Etapas - Execução tática - BTCTURBO v5.3

```
1. IDENTIFICAR CICLO → 2. VALIDAR PERMISSÕES → 3. DETECTAR SETUP → 4. EXECUTAR
```

## 📊 Etapa 1: Identificação do Ciclo de Mercado

### Definição do Ciclo
| Score Mercado | MVRV | Ciclo | Estratégia Macro |
|---------------|------|-------|------------------|
| 0-20 | <0.8 | **BOTTOM** | All-in gradual |
| 20-40 | 0.8-1.2 | **ACUMULAÇÃO** | Compras agressivas |
| 40-60 | 1.2-2.0 | **BULL INICIAL** | Compras moderadas |
| 60-80 | 2.0-3.0 | **BULL MADURO** | Hold + Realizações |
| 80-100 | >3.0 | **EUFORIA/TOPO** | Realizar gradual |

### Parâmetros por Ciclo
| Ciclo | Max Alavancagem | Max Exposição | Stop Sugerido | Tamanho Operação |
|-------|-----------------|---------------|---------------|------------------|
| BOTTOM | 3.0x | 100% | -20% ou MA | 40-50% |
| ACUMULAÇÃO | 2.5x | 90% | -15% ou MA | 30-40% |
| BULL INICIAL | 2.5x | 100% | -12% ou MA | 20-30% |
| BULL MADURO | 2.0x | 80% | -10% ou ATR | 15-25% |
| EUFORIA/TOPO | 1.5x | 60% | -8% ou ATR | Realize 20-40% |

---

## ✅ Etapa 2: Validações (Gate System) - REVISADO

```
├── 1. CICLO PERMITE?
│   ├── Qualquer ciclo → Permitido (direção muda)
│   └── Verificar direção do ciclo
│
├── 2. RISCO OK? (Score > 40)
│   ├── Não → Reduzir/Sair
│   └── Sim → Continua
│
├── 3. HEALTH FACTOR OK? (HF > 1.2)
│   ├── HF < 1.2 → Reduzir 50-80%
│   ├── HF 1.2-1.5 → Cautela
│   └── HF > 1.5 → Seguro
│
└── 4. TEM MARGEM?
    ├── Capital livre < 5% → Bloqueado
    ├── Alavancagem no limite → Ajustar primeiro
    └── OK → Verificar Setups
```

---

## 🎯 Etapa 3: Matriz de Setups (Timeframe 4H)

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

## 📋 Etapa 4: Tabela de Decisão Final (REVISADA)

### Decisões por Ciclo + Setup

| Ciclo | Setup 4H Detectado | Decisão | Prioridade |
|-------|-------------------|---------|------------|
| **BOTTOM** | Oversold extremo | Comprar 40-50% | Máxima |
| **BOTTOM** | Qualquer compra | Comprar 30-40% | Alta |
| **ACUMULAÇÃO** | Pullback | Comprar 30-35% | Alta |
| **ACUMULAÇÃO** | Rompimento | Comprar 25% | Alta |
| **BULL INICIAL** | Pullback | Comprar 20-25% | Média |
| **BULL INICIAL** | Teste suporte | Comprar 20% | Média |
| **BULL MADURO** | Pullback forte | Comprar 15% | Baixa |
| **BULL MADURO** | Resistência/Exaustão | Realizar 25-30% | Alta |
| **EUFORIA/TOPO** | Qualquer compra | IGNORAR | - |
| **EUFORIA/TOPO** | Qualquer venda | Realizar 30-40% | Máxima |

### Hierarquia de Decisão (Timeframe Conflito)
1. **Ciclo (Semanal)** define direção permitida
2. **Setup 4H** define timing de entrada
3. **Conflito?** Ciclo sempre prevalece

---

## 🚨 Overrides Especiais (REVISADOS)

### Proteção Absoluta (Ignora tudo)
- Health Factor < 1.2 → Reduzir 50-80%
- Score Risco < 30 → Reduzir 50%
- Flash Crash > 25% → Avaliar liquidez/oportunidade

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