## Análise 4: Execução Tática
**Pergunta:** "Quando e quanto adicionar/realizar?"

#### Matriz de Decisão EMA 144 + RSI Diário

| Distância EMA 144 | RSI Diário | Ação | Tamanho | Justificativa |
|-------------------|------------|------|---------|---------------|
| > +20% | > 70 | **REALIZAR** | 40% | Extremo sobrecomprado |
| > +20% | 50-70 | **REALIZAR** | 25% | Muito esticado |
| > +20% | < 50 | **HOLD** | 0% | Divergência, aguardar |
| +10% a +20% | > 70 | **REALIZAR** | 25% | Sobrecomprado |
| +10% a +20% | 50-70 | **HOLD** | 0% | Tendência saudável |
| +10% a +20% | < 50 | **HOLD** | 0% | Momentum fraco |
| -5% a +10% | Qualquer | **HOLD** | 0% | Zona neutra |
| -10% a -5% | > 50 | **HOLD** | 0% | Sem confirmação |
| -10% a -5% | < 50 | **ADICIONAR** | 35% | Desconto + oversold |
| < -10% | > 30 | **ADICIONAR** | 50% | Grande desconto |
| < -10% | < 30 | **ADICIONAR** | 75% | Capitulação |

---

## 📊 Matriz Completa de Cenários

### Cenário 1: Bull Market Inicial
```
Contexto: Bitcoin saindo de acumulação
├── Score Mercado: 75 ✅
├── Score Risco: 85 ✅
├── MVRV: 1.5 (Max 2.5x)
├── EMA 144: Preço +5%
└── RSI Diário: 45

AÇÃO: Entrar com 2.0x alavancagem
STOP: -12% do patrimônio
TARGET: Aguardar EMA +15%
```

### Cenário 2: Bull Market Maduro
```
Contexto: Tendência estabelecida há meses
├── Score Mercado: 68 ✅
├── Score Risco: 75 ✅
├── MVRV: 2.5 (Max 2.0x)
├── EMA 144: Preço +18%
└── RSI Diário: 72

AÇÃO: Realizar 25% da posição
MANTER: 1.5x alavancagem
ALERTA: Preparar mais realizações
```

### Cenário 3: Topo Formando
```
Contexto: Euforia de mercado
├── Score Mercado: 62 ✅
├── Score Risco: 70 ✅
├── MVRV: 3.5 (Max 1.5x)
├── EMA 144: Preço +25%
└── RSI Diário: 78

AÇÃO: Realizar 40% imediato
REDUZIR: Para 1.0-1.5x max
STOP: Apertado em -8%
```

### Cenário 4: Correção em Bull
```
Contexto: Pullback saudável
├── Score Mercado: 65 ✅
├── Score Risco: 80 ✅
├── MVRV: 2.2 (Max 2.0x)
├── EMA 144: Preço -7%
└── RSI Diário: 42

AÇÃO: Adicionar 35% posição
ALVO: 2.0x alavancagem
PRAZO: DCA em 3 dias
```

### Cenário 5: Início Bear Market
```
Contexto: Quebra de estrutura
├── Score Mercado: 38 ❌
├── Score Risco: 65 ✅
├── MVRV: 2.0
├── EMA 144: Preço -5%
└── RSI Diário: 35

AÇÃO: Reduzir 50% posição
IGNORAR: Sinais de compra
MODO: Preservação capital
```

### Cenário 6: Bear Market Profundo
```
Contexto: Capitulação geral
├── Score Mercado: 25 ❌
├── Score Risco: 45 ⚠️
├── MVRV: 0.8
├── EMA 144: Preço -20%
└── RSI Diário: 22

AÇÃO: Zerar alavancagem
ESTRATÉGIA: Acumular spot apenas
AGUARDAR: Score > 60
```

### Cenário 7: Risco Crítico
```
Contexto: Posição em perigo
├── Score Mercado: 70 ✅
├── Score Risco: 35 ❌
├── Health Factor: 1.25
├── Dist. Liquidação: 18%
└── Qualquer RSI

AÇÃO: Reduzir 70% URGENTE
PRIORIDADE: Salvar capital
PRAZO: Imediato
```

### Cenário 8: Volatilidade Comprimida
```
Contexto: Mercado lateral extenso
├── Score Mercado: 55 ⚠️
├── Score Risco: 75 ✅
├── BBW: 4% há 2 semanas
├── Volume: Decrescente
└── RSI: 48-52 (neutro)

AÇÃO: Preparar capital
ESTRATÉGIA: 50% dry powder
ALERTA: Breakout iminente
```