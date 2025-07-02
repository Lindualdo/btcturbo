# BTC TURBO - Indicador de Estrutura de Mercado HH/HL

## CONCEITO FUNDAMENTAL

Estrutura de mercado identifica a direção da tendência através dos pontos de pivô (topos e fundos).

### Definições:
- **HH (Higher High)**: Topo mais alto que o anterior
- **HL (Higher Low)**: Fundo mais alto que o anterior
- **LH (Lower High)**: Topo mais baixo que o anterior
- **LL (Lower Low)**: Fundo mais baixo que o anterior

## IDENTIFICAÇÃO DE PIVÔS

### Pivô de Alta (Topo):
- Ponto mais alto com 2 candles menores à esquerda E direita
- Exemplo: [95k, 98k, **100k**, 99k, 97k] = Topo em 100k

### Pivô de Baixa (Fundo):
- Ponto mais baixo com 2 candles maiores à esquerda E direita
- Exemplo: [95k, 93k, **90k**, 91k, 94k] = Fundo em 90k

## ANÁLISE DA ESTRUTURA

### Tendência de Alta (Bullish):
```
Fundo 1: $90,000
Topo 1: $95,000
Fundo 2: $92,000 (HL - mais alto que $90,000)
Topo 2: $98,000 (HH - mais alto que $95,000)
```

### Tendência de Baixa (Bearish):
```
Topo 1: $100,000
Fundo 1: $95,000
Topo 2: $98,000 (LH - mais baixo que $100,000)
Fundo 2: $93,000 (LL - mais baixo que $95,000)
```

## CÁLCULO DO SCORE (0-100)

### Período de Análise: Últimos 10 pivôs (5 topos + 5 fundos)

| Estrutura | Condição | Score |
|-----------|----------|-------|
| **Tendência Forte Alta** | 4+ HH e 4+ HL | 90-100 |
| **Tendência Alta** | 3 HH e 3 HL | 70-90 |
| **Início de Alta** | 2 HH e 2 HL | 60-70 |
| **Range/Indefinido** | Mistura sem padrão | 40-60 |
| **Início de Baixa** | 2 LH e 2 LL | 30-40 |
| **Tendência Baixa** | 3 LH e 3 LL | 10-30 |
| **Tendência Forte Baixa** | 4+ LH e 4+ LL | 0-10 |

## AJUSTES ESPECIAIS

### Quebra de Estrutura:
- Se último movimento quebra padrão: -20 pontos
- Exemplo: 3 HH/HL seguidos de 1 LL = sinal de alerta

### Força do Movimento:
- Se último HH >5% acima do anterior: +10 pontos
- Se último HL <2% acima do anterior: -10 pontos

## EXEMPLO PRÁTICO

```
Últimos 5 fundos: $88k, $90k, $92k, $94k, $96k (todos HL)
Últimos 5 topos: $92k, $95k, $98k, $101k, $104k (todos HH)

Cálculo:
- 5 HH + 5 HL = Tendência Forte Alta
- Score base: 95
- Último HH foi 3% acima (normal): 0 ajuste
- Score final: 95
```

## INTEGRAÇÃO COM SISTEMA

### No Bloco Técnico (peso 20%):
```
Score Técnico = (EMAs × 0.5) + (RSI × 0.3) + (Estrutura × 0.2)
```

### Interpretação:
- Score >80: Estrutura confirma tendência forte
- Score 60-80: Estrutura saudável
- Score 40-60: Cautela, possível mudança
- Score <40: Estrutura bearish, reduzir exposição

## TIMEFRAME RECOMENDADO

**Diário** para consistência com EMAs e RSI do bloco técnico.

### Configuração:
- Análise: 20-30 dias de histórico
- Pivôs: Mínimo 2 candles de confirmação
- Atualização: 1x ao dia após fechamento

---
*Indicador de estrutura para confirmar tendências e identificar reversões*