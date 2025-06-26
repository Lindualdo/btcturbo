#  BTC TURBO - Hold Alavancado - Visão Geral Executiva 1.6.0
- revisões nos pesos do ciclos (ciclos de 40% > 50%, tecnico de 40% > 30%)
- camada 4 agora focada exclusivamente nas ações definidas pela matriz de ciclo do mercado ( camada 1)
- analise técnica: trocado posição do preço por expnasão das EMAs (distancia entre as EMAs)
- retirado indicador de Pull Multiple (muito volátio) do bloco ciclo
- incluido indicador Reserve Risk no bloco ciclo (mais eficiente que pull Multiple para identificar fndos)
- alterado pesos dos indicadores de ciclo (mvrv 30 > 40, nupl 20 > 30, realized price ratio 40 > 20)
- camada 1 principal, define ciclo, alavancagem, tamanho da posição, ações a serem executadas
- as demais camadas  operacionaliza (valida alavancagem, confere o risco e financeiro, destaca e alerta as ações)

## Objetivo Principal
Sistema quantitativo para gestão de posição alavancada em Bitcoin, focado em preservação de capital e captura de tendências de médio/longo prazo.

## RESUMO DO SISTEMA

Patrimonio total dividido em duas partes:
- 50% CORE sempre em hold BTC
- 50% satelite será alocado e alavancado de acordo com o ciclo de mercado
- A alaocação é feita exclusivamente na plataforma AAVE

```
1 - Analise de mercado 
- faz analise em 3 blocos (ciclos, momentum e tecncio) e gera um score final
- com base no score define o ciclo de mercado 
- o cilco responde se devo estar posicionado, tamanho da posição, alavancagem e ação
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
- usar matriz de ciclos (matriz_ciclo-v3.1.md)

### 📊 Tabela de Indicadores - Análise de Mercado
**Pergunta:** "O mercado está favorável para estar posicionado?"

| Indicador                     | Peso         | Descrição breve |
|------------------------------|--------------|------------------|
| **MVRV Z-Score**             | 40% Ciclo    | Mede se o BTC está sobre ou subvalorizado - valor de mercado vs valor realizado |
| **NUPL**                     | 30% Ciclo    | Lucros/prejuízos não realizados; mostra otimismo ou medo dos investidores |
| **Realized Price Ratio**     | 20% Ciclo    | Compara o preço atual com o preço médio pago (todas as moedas em circulação)
| **Reserve Risk**             | 10% Ciclo    | Relação entre a confiança dos holders de longo prazo (HODLers) e o preço atual|
| **RSI Semanal**              | 40% Momentum | Força relativa dos preços; identifica condições de sobrecompra ou sobrevenda |
| **Funding Rates 7D**         | 30% Momentum | Taxas de financiamento médias; revela o sentimento de alavancagem dos derivativos |
| **SOPR**                     | 20% Momentum | Mede o lucro/prejuízo nas transações realizadas on-chain |
| **Long/Short Ratio**         | 10% Momentum | Relação entre posições compradas e vendidas no mercado futuro |
| **Sistema de EMAs**          | 50% Técnico  | Alinhamento entre as médias - 70% semanal 30% diário - score-emas-v3.md|
| **Sistema de EMAs**          | 50% Técnico  | Expansão das EMAs - distancias entre si - 70% semanal 30% diário - score-emas-v3.md|

### Análise de Mercado (Score 0-100)
- Calcular o Score de cada indicdor aplicando o peso conforme tabela acima (dentro de cada bloco)
- depois aplicar os pesos de cada blocos para calcular o score de mercado
- Score mercado = 50% do score de ciclo, 20% do score de momentum e 30% do score técnico

```

Receita diária dos mineradores em relação à média histórica; detecta topos  fundos 

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

TÉCNICO (30%) - (score usar: score-emas-v3.md)
├── Sistema EMAs
│   ├── Alinhamento: EMA17>34>144>305>610
│   └── Expasão: distancia entre as medias

```
Para o score das EMAs usar matriz de score
score-emas-v3.md

### 2- Gestão de Risco (Score 0-100)
**Pergunta Central:** "Minha posição atual está segura?"

- **Health Factor AAVE** (50%): Margem de segurança na plataforma
- **Distância até Liquidação** (50%): Percentual de queda até liquidação forçada

### 3 - Dimensionamento de Alavancagem

**Pergunta Central:** "Qual alavancagem máxima posso usar?"

- usar matriz de ciclos / alavancagem

### 4 - Execução Tática:

**Pergunta Central:** "O que devo fazer agora?"
- validações de proteção (gate sistem) 
- usar matriz de ciclo v3 para identificar ação (matriz-ciclos-v3.md)
