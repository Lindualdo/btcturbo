#  BTC TURBO - Hold Alavancado - Visão Geral Executiva

## Objetivo Principal
Sistema quantitativo para gestão de posição alavancada em Bitcoin, focado em preservação de capital e captura de tendências de médio/longo prazo.

## Arquitetura: 4 Camadas de Análise

### 1️⃣ Análise de Mercado (Score 0-100)
**Pergunta Central:** "O mercado está favorável para estar posicionado?"

#### Bloco CICLO (40% do peso)
- **MVRV Z-Score** (30%): Relação entre valor de mercado e valor realizado
- **NUPL** (20%): Lucro/prejuízo não realizado da rede
- **Realized Price Ratio** (40%): Preço atual vs preço médio pago
- **Puell Multiple** (10%): Receita dos mineradores vs média histórica

#### Bloco MOMENTUM (20% do peso)
- **RSI Semanal** (40%): Força relativa de preços
- **Funding Rates 7D** (30%): Taxa de financiamento média
- **SOPR** (20%): Razão de lucro/prejuízo nas transações
- **Long/Short Ratio** (10%): Sentimento do mercado de futuros

#### Bloco TÉCNICO (40% do peso)
- **Sistema EMAs Multi-timeframe** (70%): Alinhamento de médias móveis exponenciais(17, 34, 144, 305, 610) semanal e diário +  posição do preço em relação as médias (50% para alinhamento e 50% para posição)
- **Bollinger Band Width** (30%): Medida de volatilidade/compressão

### 2️⃣ Gestão de Risco (Score 0-100)
**Pergunta Central:** "Minha posição atual está segura?"

- **Health Factor AAVE** (50%): Margem de segurança na plataforma
- **Distância até Liquidação** (50%): Percentual de queda até liquidação forçada

### 3️⃣ Dimensionamento de Alavancagem
**Pergunta Central:** "Qual alavancagem máxima posso usar?"

Baseado exclusivamente no MVRV:
- MVRV < 1.0: Máximo 3.0x (fase de acumulação)
- MVRV 1.0-2.0: Máximo 2.5x (bull inicial)
- MVRV 2.0-3.0: Máximo 2.0x (bull médio)
- MVRV > 3.0: Máximo 1.5x (zona de topo)

### 4️⃣ Execução Tática

**Pergunta Central:** "Quando e quanto adicionar ou realizar?"

## 🎯 Fluxo Principal - 4 Etapas

```
1. IDENTIFICAR CICLO → 2. VALIDAR PERMISSÕES → 3. DETECTAR SETUP → 4. EXECUTAR
```

---

## 📊 Etapa 1: Identificação do Ciclo de Mercado

**MVRV define o ciclo, Score de Mercado confirma condições**

## Tabela de Referência

| MVRV | Ciclo | Score Esperado | Interpretação se Score Diferente | Ação |
|------|-------|----------------|----------------------------------|------|
| < 0.8 | **BOTTOM** | 0-20 | Score alto = divergência bullish rara | Oportunidade histórica |
| 0.8-1.2 | **ACUMULAÇÃO** | 20-40 | Score alto = força interna se formando | Aumentar posições |
| 1.2-2.0 | **BULL INICIAL** | 40-70 | Score baixo = correção temporária | Comprar pullbacks |
| 2.0-3.0 | **BULL MADURO** | 50-80 | Score baixo = consolidação saudável | Manter com stops |
| > 3.0 | **EUFORIA/TOPO** | 60-100 | Score baixo = topo se formando | Realizar gradualment


### Divergências Notáveis - casos especiais

- **MVRV baixo + Score alto**: Início de novo ciclo bull (raro e poderoso)
- **MVRV alto + Score baixo**: Exaustão de tendência (sinal de topo)
- **MVRV médio + Score médio**: Mercado em equilíbrio (mais comum)


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