# Sistema BTC TURBO - Hold Alavancado - Visão Geral Executiva

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
- **Sistema EMAs Multi-timeframe** (70%): Alinhamento de médias móveis exponenciais (17, 34, 144, 305, 610) em 4 timeframes (1H, 4H, 1D, 1W)
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

### 4️⃣ Execução Tática
**Pergunta Central:** "Quando e quanto adicionar ou realizar?"

Matriz de decisão baseada em:
- **Distância da EMA 144 diária**: Mede esticamento do preço
- **RSI diário**: Identifica condições de sobrecompra/sobrevenda
- **Estrutura multi-timeframe**: Valida setups em timeframes menores (4H)

## Sistema de Decisão Hierárquico

### Prioridade 1: Proteção de Capital
- Score Risco < 50 → Redução imediata
- Health Factor < 1.3 → Ação emergencial
- Alavancagem acima do permitido → Ajuste obrigatório

### Prioridade 2: Condições de Mercado
- Score Mercado < 40 → Modo defensivo
- Score Mercado > 60 → Considerar posicionamento

### Prioridade 3: Execução Tática
Apenas quando Prioridades 1 e 2 estão satisfeitas:
- Compras em correções com RSI baixo
- Realizações em esticamentos com RSI alto
- Tamanhos de 10% a 75% conforme setup

## Indicadores Complementares

### Timing e Volatilidade
- **BBW (Bollinger Band Width)**: Detecta compressão pré-movimento
- **ATR (Average True Range)**: Mede volatilidade para stops
- **Volume Profile**: Identifica zonas de suporte/resistência

### Smart Money
- **Exchange Flows**: Movimento de BTC para/de exchanges
- **Whale Transactions**: Atividade de grandes holders
- **Miner Flows**: Comportamento dos mineradores

## Estratégia Core-Satellite

- **50% Core**: Bitcoin spot, nunca alavancado (buy & hold)
- **50% Satellite**: Capital para estratégia alavancada (0-3x conforme sistema)

## Diferenciais do Sistema

1. **Multi-camada**: Proteção através de verificações independentes
2. **Adaptativo**: Ajusta exposição conforme fase do ciclo
3. **Quantitativo**: Decisões baseadas em dados, não emoção
4. **Hierárquico**: Proteção sempre prevalece sobre oportunidade

## Gestão de Cenários Especiais

- **Acumulação macro**: Reduz para 1x em lateralizações prolongadas
- **Volatilidade extrema**: Circuit breakers automáticos
- **Divergências**: Peso maior para indicador mais conservador

## Resultados Esperados

- **Objetivo primário**: Preservação de capital
- **Objetivo secundário**: Superar buy & hold em 50%+ ao ano
- **Drawdown máximo aceitável**: 35%
- **Sharpe Ratio alvo**: > 1.5

---

*Sistema desenvolvido para investidores qualificados com horizonte de médio/longo prazo e tolerância a volatilidade*