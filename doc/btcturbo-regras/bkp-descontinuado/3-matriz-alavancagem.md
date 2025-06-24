# Matriz Definitiva de Alavancagem - BTC Hold

## 🎯 Regra Única: QUANTO POSSO ALAVANCAR?

### Passo 2: Calcular Alavancagem Máxima

| MVRV | RSI Mensal | Score Mercado | Alavancagem Máxima |
|------|------------|---------------|-------------------|
| < 1.0 | < 30 | > 70 | **3.0x** |
| < 1.0 | < 30 | 50-70 | **2.5x** |
| < 1.0 | 30-50 | > 60 | **2.5x** |
| 1.0-2.0 | 30-50 | > 60 | **2.5x** |
| 1.0-2.0 | 50-70 | > 60 | **2.0x** |
| 2.0-3.0 | 30-70 | > 50 | **2.0x** |
| 2.0-3.0 | > 70 | > 50 | **1.5x** |
| > 3.0 | Qualquer | Qualquer | **1.5x** |
| Qualquer | > 80 | Qualquer | **1.5x** |

---

### Passo 3: Aplicar Redutor por Score de Mercado

| Score Mercado | Fator Redutor |
|---------------|---------------|
| 40-50 | 0.5x |
| 50-60 | 0.8x |
| 60-70 | 1.0x |
| 70-80 | 1.0x |
| > 80 | 0.8x (proteção topo) |

**Fórmula Final:**
```
Alavancagem Permitida = Alavancagem Máxima × Fator Redutor
```

---

## 📊 Exemplos Práticos

### Exemplo 1: Bull Market Inicial
- Score Risco: 80 ✓
- Score Mercado: 65 ✓
- MVRV: 1.5
- RSI Mensal: 45
- **Resultado: 2.5x × 1.0 = 2.5x**

### Exemplo 2: Correção em Bull
- Score Risco: 75 ✓
- Score Mercado: 55 ✓
- MVRV: 2.2
- RSI Mensal: 52
- **Resultado: 2.0x × 0.8 = 1.6x**

### Exemplo 3: Mercado Neutro
- Score Risco: 60 ✓
- Score Mercado: 45 ✓
- MVRV: 2.5
- RSI Mensal: 55
- **Resultado: 2.0x × 0.5 = 1.0x**

### Exemplo 4: Bear Market
- Score Risco: 70 ✓
- Score Mercado: 35 ❌
- **Resultado: 0x (BLOQUEADO)**

---

## 🚨 Regras de Proteção Adicional

1. **Acumulação prolongada**: Se Score 45-55 por >8 semanas → Máximo 1.0x
2. **Volatilidade extrema**: Se mudança diária >15% → Reduzir 0.5x temporário
3. **Divergência componentes**: Se diferença >30 pontos entre ciclo/momentum/técnico → Máximo 1.5x

---

## ✅ Resposta Rápida

**Posso alavancar?**
1. Todos os gates OK? → SIM, continue
2. Algum gate falhou? → NÃO, 0x

**Quanto posso?**
1. Olhe tabela MVRV × RSI × Score
2. Aplique redutor do Score Mercado
3. Resultado = sua alavancagem máxima

---

*Tabela única e definitiva - Sem conflitos ou ambiguidades*