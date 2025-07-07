# Sistema de Score Bitcoin: 0 (Caro) a 100 (Barato) - v3

## Confirmações para Extremos
Quando score atingir 0-30 ou 70-100, confirmar com:
1. **Persistência**: Valor extremo mantido por 3+ dias
2. **Divergência**: Pelo menos 3 dos 4 indicadores concordando
3. **Momentum**: RSI semanal >70 (topo) ou <30 (fundo)
4. **Volume**: Spike de volume on-chain confirmando movimento

## Tabela 1: Combinações Binárias (Ajustada para Baixa Volatilidade)

| Score | Condições (AND) |
|-------|----------------|
| **10** | MVRV Z-Score > 4.5 **E** Reserve Risk > 0.012 **E** NUPL > 0.65 |
| **20** | MVRV Z-Score > 3.8 **E** Puell Multiple > 3 **E** Reserve Risk > 0.01 |
| **30** | NUPL > 0.6 **E** Reserve Risk > 0.008 **E** MVRV Z-Score > 3.2 |
| **40** | MVRV Z-Score > 2.5 **E** Puell Multiple > 2 |
| **50** | NUPL entre 0.3-0.45 **E** Reserve Risk entre 0.005-0.007 |
| **60** | MVRV Z-Score entre 1.2-2 **E** Reserve Risk entre 0.004-0.005 |
| **70** | NUPL < 0.2 **E** Reserve Risk < 0.004 |
| **80** | MVRV Z-Score < 1 **E** Puell Multiple < 0.6 **E** Reserve Risk < 0.003 |
| **90** | NUPL < 0.1 **E** Reserve Risk < 0.002 **E** Puell Multiple < 0.5 |
| **100** | MVRV Z-Score < 0 **E** NUPL < -0.15 **E** Reserve Risk < 0.0015 |

## Tabela 2: Matriz Individual com Pesos Ajustados (Fallback)

### Pesos dos Indicadores:
- **MVRV Z-Score**: 40% (+5%)
- **Reserve Risk**: 35% (+5%)
- **NUPL**: 15% (-5%)
- **Puell Multiple**: 10% (-5%)

### Valores por Score (Calibrados para Mercado Atual):

| Indicador | Score 10 | Score 20 | Score 30 | Score 40 | Score 50 | Score 60 | Score 70 | Score 80 | Score 90 | Score 100 |
|-----------|----------|----------|----------|----------|----------|----------|----------|----------|----------|-----------|
| **MVRV Z-Score** | > 5 | 4-5 | 3.2-4 | 2.5-3.2 | 1.8-2.5 | 1.2-1.8 | 0.8-1.2 | 0.4-0.8 | 0-0.4 | < 0 |
| **Reserve Risk** | > 0.015 | 0.012-0.015 | 0.01-0.012 | 0.008-0.01 | 0.006-0.008 | 0.004-0.006 | 0.003-0.004 | 0.002-0.003 | 0.0015-0.002 | < 0.0015 |
| **NUPL** | > 0.7 | 0.65-0.7 | 0.6-0.65 | 0.5-0.6 | 0.35-0.5 | 0.2-0.35 | 0.05-0.2 | -0.05-0.05 | -0.15--0.05 | < -0.15 |
| **Puell Multiple** | > 3.5 | 3-3.5 | 2.5-3 | 2-2.5 | 1.3-2 | 0.9-1.3 | 0.6-0.9 | 0.45-0.6 | 0.35-0.45 | < 0.35 |

### Cálculo do Score Final (Tabela 2):
```
Score Final = (Score_MVRV × 0.40) + (Score_RR × 0.35) + (Score_NUPL × 0.15) + (Score_Puell × 0.10)
```

### Mudanças Principais:
- **MVRV**: Topo em 5 (vs 8 anterior), refletindo que 3.5 já marcou topo recente
- **Reserve Risk**: Compressão de ~40% nos valores
- **NUPL**: Extremos reduzidos (0.7 vs 0.8 para topo)
- **Puell**: Ajustado para nova realidade de mineração

### Interpretação:
- 0-20: Mercado muito caro (zona de distribuição)
- 20-40: Mercado caro (cautela)
- 40-60: Mercado neutro
- 60-80: Mercado barato (acumulação)
- 80-100: Mercado muito barato (forte acumulação)