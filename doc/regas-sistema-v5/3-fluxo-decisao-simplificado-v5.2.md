# Fluxo de Decisão Simplificado - BTCTURBO Hold Alavancado

## 🎯 Fluxo Principal - 4 Etapas

```
1. IDENTIFICAR CICLO → 2. VALIDAR PERMISSÕES → 3. DETECTAR SETUP → 4. EXECUTAR
```

---

## 📊 Etapa 1: Identificação do Ciclo de Mercado

### Definição do Ciclo
| Score Mercado | MVRV | Ciclo | Estratégia Macro |
|---------------|------|-------|------------------|
| 0-30 | >3.0 | **BEAR** | Fora do mercado |
| 30-50 | 2.5-3.0 | **ACUMULAÇÃO** | Compras pequenas |
| 50-70 | 1.5-2.5 | **BULL INICIAL** | Compras agressivas |
| 70-85 | 1.0-2.0 | **BULL MADURO** | Hold + Realizações |
| 85-100 | <1.0 | **EUFORIA/BOTTOM** | Realize ou All-in |

### Parâmetros por Ciclo
| Ciclo | Max Alavancagem | Max Exposição | Stop Loss | Tamanho Operação |
|-------|-----------------|---------------|-----------|------------------|
| BEAR | 0x | 0% | - | - |
| ACUMULAÇÃO | 1.0x | 50% | -15% | 10-20% |
| BULL INICIAL | 2.5x | 100% | -12% | 30-50% |
| BULL MADURO | 2.0x | 80% | -10% | 20-30% |
| EUFORIA | 1.5x | 60% | -8% | Realize 20-40% |

---

## ✅ Etapa 2: Validações (Gate System)

```
├── 1. CICLO PERMITE?
│   ├── BEAR → Bloqueado para compras
│   └── Outros → Continua
│
├── 2. RISCO OK? (Score > 50)
│   ├── Não → Reduzir/Sair
│   └── Sim → Continua
│
├── 3. TEM MARGEM?
│   ├── Capital livre < 5% → Bloqueado
│   ├── Alavancagem no limite → Ajustar primeiro
│   └── OK → Continua
│
└── 4. PASSOU TUDO? → Verificar Setups
```

---

## 🎯 Etapa 3: Matriz de Setups (Timeframe 4H)

### Setups de COMPRA
| Setup | Condições 4H | Condições Diário | Ação | Tamanho |
|-------|--------------|------------------|------|---------|
| **Pullback Tendência** | RSI < 45 + EMA144 ±3% | Tendência alta | COMPRAR | 30% |
| **Teste Suporte** | Toca EMA144 + Bounce | Volume alto | COMPRAR | 25% |
| **Rompimento** | Fecha acima resistência | Alinhamento OK | COMPRAR | 20% |
| **Oversold Extremo** | RSI < 30 | Não em bear | COMPRAR | 40% |

### Setups de VENDA
| Setup | Condições 4H | Condições Diário | Ação | Tamanho |
|-------|--------------|------------------|------|---------|
| **Resistência** | RSI > 70 + Topo range | EMA144 > +15% | REALIZAR | 25% |
| **Exaustão** | 3 topos + Volume ↓ | RSI > 65 | REALIZAR | 30% |
| **Take Profit** | Lucro > 30% posição | Qualquer | REALIZAR | 20% |
| **Stop Gain** | Target atingido | Qualquer | REALIZAR | 50% |

---

## 📋 Etapa 4: Tabela de Decisão Final

### Decisões por Ciclo + Setup

| Ciclo | Setup 4H Detectado | Decisão | Prioridade |
|-------|-------------------|---------|------------|
| **BEAR** | Qualquer | IGNORAR | - |
| **ACUMULAÇÃO** | Pullback | Comprar 10-15% | Baixa |
| **ACUMULAÇÃO** | Oversold extremo | Comprar 20% | Média |
| **BULL INICIAL** | Pullback | Comprar 30-40% | Alta |
| **BULL INICIAL** | Rompimento | Comprar 25% | Alta |
| **BULL MADURO** | Pullback | Comprar 20% | Média |
| **BULL MADURO** | Resistência/Exaustão | Realizar 25-30% | Alta |
| **EUFORIA** | Qualquer compra | IGNORAR | - |
| **EUFORIA** | Qualquer venda | Realizar 30-40% | Máxima |

### Sem Setup Detectado
| Ciclo | Ação Default | Frequência Check |
|-------|--------------|------------------|
| BEAR | Aguardar | Semanal |
| ACUMULAÇÃO | Monitorar de perto | Diário |
| BULL INICIAL | Manter posição | 2x dia |
| BULL MADURO | Manter + Stops | Diário |
| EUFORIA | Realizar gradual | 2x dia |

---

## 🚨 Overrides Especiais (Exceções)

### Proteção Absoluta (Ignora tudo)
- Health Factor < 1.3 → Reduzir 80%
- Score Risco < 30 → Fechar tudo
- Flash Crash > 20% → Avaliar liquidez

### Oportunidades Raras (Ignora ciclo)
- MVRV < 0.5 + RSI < 20 → All-in histórico
- 5+ semanas ATH + Correção > 15% → Compra agressiva
- Capitulação (volume 5x + queda 30%) → Comprar máximo permitido

---

## 📱 Widget Decisão Simplificada

```
┌─────────────────────────────────┐
│ CICLO: BULL INICIAL             │
│ Alavancagem: 1.6x/2.5x ✅       │
│                                 │
│ 💡 AÇÃO AGORA:                  │
│ [COMPRAR 30%]                   │
│ "Pullback 4H detectado"         │
│                                 │
│ Confiança: ⭐⭐⭐⭐             │
│ Próxima revisão: 4 horas        │
└─────────────────────────────────┘
```

---

## 🔄 Frequência de Revisão

| Ciclo | Frequência | Foco |
|-------|------------|------|
| BEAR | Semanal | Mudança de ciclo |
| ACUMULAÇÃO | Diária | Breakouts |
| BULL INICIAL | 12h | Oportunidades |
| BULL MADURO | Diária | Realizações |
| EUFORIA | 8h | Saídas |

---

*Sistema simplificado mantendo robustez - Foco em execução clara*