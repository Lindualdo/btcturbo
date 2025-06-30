#  BTC TURBO - Hold Alavancado - Visão Geral Executiva 1.7.0
- Criação de camada adicional após camada 1
- nesta camada adicional

## Objetivo Principal
Sistema quantitativo para gestão de posição alavancada em Bitcoin, focado em preservação de capital e captura de tendências de médio/longo prazo.

## 1. ESTRUTURA DE CAPITAL
- **Core**: 50% (Buy & Hold permanente)
- **Satélite**: 50% (Gestão ativa)
- **Alavancagem**: Até 3x sobre satélite


## RESUMO DO SISTEMA - DECISÃO EM 4 CAMADAS

```
1 - Analise de mercado 
- faz analise em 3 blocos (ciclos, momentum e tecncio) e gera um score final
- com base no score define o ciclo de mercado 
- o cilco responde se devo estar posicionado, tamanho da posição, alavancagem e ação
- gatilhos objetivos ajustam o score para melhor responsividade ao mercado (novo)
2 - Analise de risco
- analisa os indicadores financeiros (plataforma AAVE)
- o score final define a saúde da minha posição
- responde se minha posição está segura
3 - Analise de alavancagem
- Analise o ciclo de mercado (definido na camada 1), calcula os limites permitidos X utilizados
- retorna o limite liberado para operar (max 3X)
4 - Execução tática
- aplica regras e validações de proteção (gate system)
- se liberado para operar, executa e estrategia definida na matriz de ciclos
```

## Arquitetura: 4 Camadas de Análise

### 1- Análise de Mercado (Score 0-100)
- Define o ciclo de mercado
- Define o tamanho da posição
- Define o limire de alavancagem
- realiza as ações táticas (manual operacional)

### 📊 Tabela de Indicadores - Análise de Mercado
**Pergunta:** "O mercado está favorável para estar posicionado?"

| Indicador                     | Peso         | Descrição breve |
|------------------------------|--------------|------------------|
| **MVRV Z-Score**             | 40% Ciclo    | Mede se o BTC está sobre ou subvalorizado - valor de mercado vs valor realizado |
| **NUPL**                     | 30% Ciclo    | Lucros/prejuízos não realizados; mostra otimismo ou medo dos investidores |
| **Realized Price Ratio**     | 15% Ciclo    | Compara o preço atual com o preço médio pago (todas as moedas em circulação)
| **Reserve Risk**             | 15% Ciclo    | Relação entre a confiança dos holders de longo prazo (HODLers) e o preço atual|
| **RSI Semanal**              | 40% Momentum | Força relativa dos preços; identifica condições de sobrecompra ou sobrevenda |
| **Funding Rates 7D**         | 30% Momentum | Taxas de financiamento médias; revela o sentimento de alavancagem dos derivativos |
| **SOPR**                     | 20% Momentum | Mede o lucro/prejuízo nas transações realizadas on-chain |
| **Long/Short Ratio**         | 10% Momentum | Relação entre posições compradas e vendidas no mercado futuro |
| **Sistema de EMAs**          | 100% Técnico  | Alinhamento entre as médias - 70% semanal 30% diário |

### Análise de Mercado (Score 0-100)
- Calcular o Score de cada indicdor aplicando o peso conforme tabela acima (dentro de cada bloco)
- depois aplicar os pesos de cada blocos para calcular o score de mercado
- Score mercado = 50% do score de ciclo, 20% do score de momentum e 30% do score técnico
- Aplicar gatilhos de ajuste de score (manual operacional)

### Calculo dos scores
CICLO (50%)
├── MVRV Z-Score
│   └── < 0: Score 9-10 | 0-1: Score 7-8 | 1-2.5: Score 5-6 | 2.5-3.7: Score 3-4 | > 3.7: Score 0-2
├── NUPL
│   └── < 0: Score 9-10 | 0-0.25: Score 7-8 | 0.25-0.5: Score 5-6 | 0.5-0.7: Score 3-4 | > 0.7: Score 0-2
├── Realized Price Ratio
│   └── < 0.8: Score 9-10 | 0.8-1.2: Score 7-8 | 1.2-2: Score 5-6 | 2-3: Score 3-4 | > 3: Score 0-2
├── Reserve Risk
│   └── < 0.002: Score 9-10 | 0.002-0.005: Score 7-8 | 0.005-0.01: Score 5-6 | 0.01-0.02: Score 3-4 | > 0.02: Score 0-2

MOMENTUM (20%)
├── RSI Semanal
│   └── < 30: Score 9-10 | 30-45: Score 7-8 | 45-55: Score 5-6 | 55-70: Score 3-4 | > 70: Score 0-2
├── Funding Rates 7D (35%)
│   └── < -0.05%: Score 9-10 | -0.05-0%: Score 7-8 | 0-0.02%: Score 5-6 | 0.02-0.1%: Score 3-4 | > 0.1%: Score 0-2
├── SOPR
│   └── < 0.9: Score 9-10 | 0.9-0.97: Score 7-8 | 0.97-1.03: Score 5-6 | 1.03-1.1: Score 3-4 | > 1.1: Score 0-2
└── Long/Short Ratio (10%)
    └── < 0.8: Score 9-10 | 0.8-0.95: Score 7-8 | 0.95-1.05: Score 5-6 | 1.05-1.3: Score 3-4 | > 1.3: Score 0-2

TÉCNICO (30%)
├── Sistema EMAs
│   ├── Alinhamento: EMA17>34>144>305>610


| Condição | Pontos |
|----------|--------|
| EMA 17 > EMA 34 | 10 |
| EMA 34 > EMA 144 | 20 |
| EMA 144 > EMA 305 | 30 |
| EMA 305 > EMA 610 | 40 |
| **Total Máximo** | **100** |

**Timeframe**: 70% Semanal + 30% Diário


### 2- Gestão de Risco (Score 0-100)
**Pergunta Central:** "Minha posição atual está segura?"

- **Health Factor AAVE** (50%): Margem de segurança na plataforma
- **Distância até Liquidação** (50%): Percentual de queda até liquidação forçada

### 3 - Dimensionamento de Alavancagem

**Pergunta Central:** "Qual alavancagem máxima posso usar?"

- usar matriz de ciclos no manual operacional

### 4 - Execução Tática:

**Pergunta Central:** "O que devo fazer agora?"
- validações de proteção (gate sistem) 
- usar manual operacional
