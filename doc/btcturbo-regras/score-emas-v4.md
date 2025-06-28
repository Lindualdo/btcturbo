# Score Análise Técnica EMAs - versão do documento v4.0

## Composição Final
```
Score Técnico = (Score Alinhamento × 0.5) + (Score Expansão × 0.5)
```

## 1. Score Alinhamento (0-100)

| Condição | Pontos |
|----------|--------|
| EMA 17 > EMA 34 | 10 |
| EMA 34 > EMA 144 | 20 |
| EMA 144 > EMA 305 | 30 |
| EMA 305 > EMA 610 | 40 |
| **Total Máximo** | **100** |

**Timeframe**: 70% Semanal + 30% Diário

# Score Expansão EMAs - Sistema 3 Níveis

## SEMANAL (Peso: 70%)

### 1. Expansão Total (40%)
**Fórmula:** `(EMA17 / EMA610 - 1) × 100`

| Expansão | Penalidade |
|----------|------------|
| < 100% | 0 |
| 100-200% | -15 |
| 200-300% | -30 |
| 300-400% | -45 |
| > 400% | -60 |

### 2. Expansão Crítica (40%)
**Fórmula:** `(EMA17 / EMA144 - 1) × 100`

| Expansão | Penalidade |
|----------|------------|
| < 25% | 0 |
| 25-50% | -15 |
| 50-75% | -30 |
| > 75% | -40 |

### 3. Expansão Adjacente (20%)
| Par | Verde (0) | Amarelo (-10) | Vermelho (-25) |
|-----|-----------|---------------|-----------------|
| 17→34 | ≤5% | 5.1-10% | >10% |
| 34→144 | ≤15% | 15.1-25% | >25% |
| 144→305 | ≤25% | 25.1-40% | >40% |
| 305→610 | ≤50% | 50.1-75% | >75% |

## DIÁRIO (Peso: 30%)

### 1. Expansão Total (40%)
**Fórmula:** `(EMA17 / EMA610 - 1) × 100`

| Expansão | Penalidade |
|----------|------------|
| < 50% | 0 |
| 50-100% | -15 |
| 100-150% | -30 |
| 150-200% | -45 |
| > 200% | -60 |

### 2. Expansão Crítica (40%)
**Fórmula:** `(EMA17 / EMA144 - 1) × 100`

| Expansão | Penalidade |
|----------|------------|
| < 15% | 0 |
| 15-30% | -15 |
| 30-45% | -30 |
| > 45% | -40 |

### 3. Expansão Adjacente (20%)
| Par | Verde (0) | Amarelo (-10) | Vermelho (-25) |
|-----|-----------|---------------|-----------------|
| 17→34 | ≤3% | 3.1-5% | >5% |
| 34→144 | ≤8% | 8.1-15% | >15% |
| 144→305 | ≤18% | 18.1-30% | >30% |
| 305→610 | ≤35% | 35.1-55% | >55% |

## Cálculo Final
```
Score TF = 100 - (Total×0.4 + Crítica×0.4 + Adjacente×0.2)
Score Final = (Score_Semanal × 0.7) + (Score_Diário × 0.3)
```