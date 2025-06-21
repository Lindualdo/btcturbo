#  BTC TURBO - Hold Alavancado - Visão Geral Executiva 1.5.0

## Objetivo Principal
Sistema quantitativo para gestão de posição alavancada em Bitcoin, focado em preservação de capital e captura de tendências de médio/longo prazo.

## Arquitetura: 4 Camadas de Análise

### 1️⃣ Análise de Mercado (Score 0-100)
**Pergunta Central:** "O mercado está favorável para estar posicionado?"
- Define o ciclo de mercado
- usar matriz de ciclos

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
- **Sistema EMAs Multi-timeframe** (70% dos 40% do bloco técncio): 
  - Timeframe Semanal (70% dos 70% do sistema de EMAs)
    - Alinhamento de médias (50% do timeframe semanal)  - ponderada por período
    - Distância do preço às médias (50% do timeframe semanal) - ponderada por período
  - Timeframe Diário (30% dos 70% do sistema de EMAs)
    - Alinhamento de médias (50% do timeframe diário)  - ponderada por período
    - Distância do preço às médias (50% do timeframe diário) - ponderada por período
- **Bollinger Band Width** (30% dos 40%): Medida de volatilidade/compressão

### 2️⃣ Gestão de Risco (Score 0-100)
**Pergunta Central:** "Minha posição atual está segura?"

- **Health Factor AAVE** (50%): Margem de segurança na plataforma
- **Distância até Liquidação** (50%): Percentual de queda até liquidação forçada

### 3️⃣ Dimensionamento de Alavancagem

**Pergunta Central:** "Qual alavancagem máxima posso usar?"

- usar matriz de alavancagem


### 4️⃣ Execução Tática

- usar matriz de setup