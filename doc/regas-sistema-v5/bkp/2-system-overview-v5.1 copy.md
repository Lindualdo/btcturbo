#  BTC TURBO - Hold Alavancado - Visão Geral Executiva

## Objetivo Principal
Sistema quantitativo para gestão de posição alavancada em Bitcoin, focado em preservação de capital e captura de tendências de médio/longo prazo.

## Arquitetura: 4 Camadas de Análise

### 1️⃣ Análise de Mercado (Score 0-100)
**Pergunta Central:** "O mercado está favorável para estar posicionado?"

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
- **Sistema EMAs Multi-timeframe** (70%): Alinhamento de médias móveis exponenciais(17, 34, 144, 305, 610) semanal e diário +  posição do preço em relação as médias (50% para alinhamento e 50% para posição)
- **Bollinger Band Width** (30%): Medida de volatilidade/compressão

### 2️⃣ Gestão de Risco (Score 0-100)
**Pergunta Central:** "Minha posição atual está segura?"

- **Health Factor AAVE** (50%): Margem de segurança na plataforma
- **Distância até Liquidação** (50%): Percentual de queda até liquidação forçada

### 3️⃣ Dimensionamento de Alavancagem
**Pergunta Central:** "Qual alavancagem máxima posso usar?"

Baseado exclusivamente no MVRV:
- MVRV < 1.0: Máximo 3.0x (fase de acumulação)
- MVRV 1.0-2.0: Máximo 2.5x (bull inicial)
- MVRV 2.0-3.0: Máximo 2.0x (bull médio)
- MVRV > 3.0: Máximo 1.5x (zona de topo)

### 4 Ações táticas
- usar documento fluxo de decisão simplif