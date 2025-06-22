#  BTC TURBO - Hold Alavancado - Visão Geral Executiva 1.5.0

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
- o cilco responde se devo estar posicionado, tamanho da posição e alavancagem
2 - Analise de risco
- analisa os indicadores financeiros (plataforma AAVE)
- o score final define a saúde da minha posição
- responde se minha posição está segura
3 - Analise de alavancagem
- Analise o score de mercado, indicadores de ciclo e IFR mensal
- retorna o limite da margem de alavancagem (max 3X)
4 - Execução tática
- aplica regras e validações de proteção (gate system)
- se liberado para operar, define o setup e estrategia
```

## Arquitetura: 4 Camadas de Análise

### 1- Análise de Mercado (Score 0-100)
**Pergunta Central:** "O mercado está favorável para estar posicionado?"
- Define o ciclo de mercado
- usar matriz de ciclos

- Ciclo 40%
- Tecnico 40%
- Momentum 20%

### 📊 Tabela de Indicadores - Análise de Mercado

| Indicador                     | Peso         | Descrição breve |
|------------------------------|--------------|------------------|
| **MVRV Z-Score**             | 30% Ciclo    | Mede se o BTC está sobre ou subvalorizado - valor de mercado vs valor realizado |
| **NUPL**                     | 20% Ciclo    | Lucros/prejuízos não realizados; mostra otimismo ou medo dos investidores |
| **Realized Price Ratio**     | 40% Ciclo    | Compara o preço atual com o preço médio pago; indica fases do ciclo |
| **Puell Multiple**           | 10% Ciclo    | Receita diária dos mineradores em relação à média histórica; detecta topos  fundos |
| **RSI Semanal**              | 40% Momentum | Força relativa dos preços; identifica condições de sobrecompra ou sobrevenda |
| **Funding Rates 7D**         | 30% Momentum | Taxas de financiamento médias; revela o sentimento de alavancagem dos derivativos |
| **SOPR**                     | 20% Momentum | Mede o lucro/prejuízo nas transações realizadas on-chain |
| **Long/Short Ratio**         | 10% Momentum | Relação entre posições compradas e vendidas no mercado futuro |
| **Sistema de EMAs**          | 70% Técnico  | Alinhamento e distância das médias móveis em múltiplos timeframes (diário e semanal) |
| **Bollinger Band Width**     | 30% Técnico  | Mede compressão/expansão da volatilidade; detecta momentos de explosão de preço |


### 2- Gestão de Risco (Score 0-100)
**Pergunta Central:** "Minha posição atual está segura?"

- **Health Factor AAVE** (50%): Margem de segurança na plataforma
- **Distância até Liquidação** (50%): Percentual de queda até liquidação forçada

### 3 - Dimensionamento de Alavancagem

**Pergunta Central:** "Qual alavancagem máxima posso usar?"

- usar matriz de ciclos / alavancagem

### 4 - Execução Tática:

**Pergunta Central:** "O que devo fazer agora?"
- validações de proteção (gate sistem) + matriz de setup