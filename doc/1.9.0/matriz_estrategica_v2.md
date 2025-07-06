# BTC TURBO - MATRIZ DE DECISÃO v2.0

## INDICADORES ON-CHAIN (Pesos Ajustados)

| Indicador | Peso | Justificativa |
|-----------|------|---------------|
| **MVRV Z-Score** | 30% | Melhor preditor de topos |
| **NUPL** | 25% | Confirma sentimento |
| **Reserve Risk** | 35% | Mais confiável para fundos/topos |
| **Puell Multiple** | 10% | Complementar |

### Scores Calibrados (0-10)

**MVRV Z-Score**
- < 0: Score 10 | 0-1: Score 8 | 1-2: Score 6 | 2-3: Score 4 | 3-4: Score 2 | > 4: Score 0

**NUPL** 
- < 0: Score 10 | 0-0.25: Score 8 | 0.25-0.5: Score 6 | 0.5-0.65: Score 4 | 0.65-0.75: Score 2 | > 0.75: Score 0

**Reserve Risk**
- < 0.001: Score 10 | 0.001-0.0025: Score 8 | 0.0025-0.005: Score 6 | 0.005-0.01: Score 4 | 0.01-0.02: Score 2 | > 0.02: Score 0

**Puell Multiple**
- < 0.5: Score 10 | 0.5-1: Score 8 | 1-1.5: Score 6 | 1.5-2.5: Score 4 | 2.5-4: Score 2 | > 4: Score 0

## INDICADOR ADICIONAL: DISTÂNCIA EMA 200

**% acima da EMA 200 semanal**
- < 50%: Neutro/Acumulação
- 50-100%: Bull Inicial 
- 100-200%: Bull Maduro
- 200-300%: Bull Avançado
- > 300%: Zona de Perigo

## MATRIZ DE DECISÃO ATUALIZADA

### Bull Forte (88-100)

| Score On-chain | Alavancagem | Satélite | Ação | Proteção |
|----------------|-------------|----------|------|----------|
| 80-100 | 3x | 100% | Hold Agressivo | Stop 3x ATR |
| 60-79 | 2x | 100% | Hold Normal | Stop 2.5x ATR |
| 45-59 | 1.5x | 100% | Hold Cauteloso | **Stop 2x ATR** |
| 30-44 | 1x | 80% | Reduzir Risco | Stop 1.5x ATR |
| 0-29 | 0x | 50% | Proteção Total | Trailing Stop |

### Bull Consolidação (66-87)

| Score On-chain | Alavancagem | Satélite | Ação | Proteção |
|----------------|-------------|----------|------|----------|
| 80-100 | 2x | 100% | Acumular | Stop 3x ATR |
| 60-79 | 1.5x | 90% | Hold | Stop 2.5x ATR |
| 45-59 | 1x | 70% | Cautela | Stop 2x ATR |
| 30-44 | 0.5x | 50% | Reduzir | Stop 1.5x ATR |
| 0-29 | 0x | 30% | Mínimo | Cash |

### Neutro (35-65)

| Score On-chain | Alavancagem | Satélite | Ação | Proteção |
|----------------|-------------|----------|------|----------|
| 80-100 | 1x | 70% | Testar Alta | Stop 2x ATR |
| 60-79 | 0.5x | 50% | Neutro | Stop Fixo |
| 45-59 | 0x | 30% | Defensivo | Cash |
| 30-44 | 0x | 20% | Wait | Cash |
| 0-29 | 0x | 10% | Mínimo | Cash |

### Bear (13-34)

| Score On-chain | Alavancagem | Satélite | Ação | Proteção |
|----------------|-------------|----------|------|----------|
| 80-100 | 1x long | 50% | Contra-tendência | Stop 1.5x ATR |
| 60-79 | 0x | 30% | Cash | - |
| 45-59 | 0.5x short | 20% | Hedge Leve | Stop 2x ATR |
| 30-44 | 1x short | 10% | Hedge Normal | Stop 1.5x ATR |
| 0-29 | 1.5x short | 5% | Hedge Forte | Stop 1x ATR |

### Bear Extremo (0-12)

| Score On-chain | Alavancagem | Satélite | Ação | Proteção |
|----------------|-------------|----------|------|----------|
| 80-100 | 2x long | 100% | Compra Agressiva | Stop 3x ATR |
| 60-79 | 1.5x long | 80% | Compra Normal | Stop 2.5x ATR |
| 45-59 | 1x long | 60% | Compra Cautelosa | Stop 2x ATR |
| 30-44 | 0.5x long | 40% | DCA Leve | Stop Fixo |
| 0-29 | 0x | 20% | Wait | Cash |

## SISTEMA DE PROTEÇÃO SIMPLIFICADO

### Zona Crítica (Score On-chain 45-59)
- **Ativação**: Quando score entra na zona 45-59
- **Stop Loss**: -10% da posição alavancada
- **Exemplo**: Com 1.5x alavancagem, stop em -15% do capital
- **Exit**: Stop atingido OU score > 60 OU score < 45

### Percentuais por Alavancagem
| Alavancagem | Stop Loss |
|-------------|-----------|
| 3x | -15% do capital |
| 2x | -12% do capital |
| 1.5x | -10% do capital |
| 1x | -8% do capital |
| 0.5x | -5% do capital |

## INDICADORES COMPLEMENTARES (Confirmação)

### RSI Mensal
- < 30: Oversold extremo (confirma compra)
- 30-50: Bear/Neutro
- 50-70: Bull Normal
- 70-80: Bull Forte (cautela se on-chain < 60)
- > 80: Overbought (reduzir se on-chain < 45)

### MACD Semanal
- Cruzamento alta + on-chain > 60 = Aumentar exposição
- Divergência baixista + on-chain < 60 = Reduzir alavancagem

### Volume On-Balance (OBV)
- Divergência com preço = Alerta adicional
- Confirma movimentos quando alinhado

## REGRAS DE DECISÃO PRIORITÁRIAS

1. **Distância EMA 200 > 250%**: Reduzir alavancagem em 1 nível
2. **Score on-chain 45-59**: Ativar proteção ATR imediatamente
3. **RSI mensal > 80 + Score < 60**: Máximo 1x alavancagem
4. **Reserve Risk < 0.001**: Pode aumentar 0.5x na alavancagem
5. **Divergência MACD + Score < 50**: Zerar alavancagem

## GATILHOS DE AÇÃO

- **Mudança de Zona On-chain**: Revisar em 24h
- **Entrada zona 45-59**: Ativar ATR stop em 1h
- **Divergência 2+ indicadores**: Reduzir 50% posição
- **Tendência muda faixa**: Rebalancear em 48h