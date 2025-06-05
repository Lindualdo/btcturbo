# Arquitetura Backtest - Sistema Hold Alavancado BTC

## 📁 Estrutura do Projeto

```
btc-backtest/
├── main.py
├── routers/
│   ├── backtest_router.py
│   └── analysis_router.py
├── services/
│   ├── backtest_service.py
│   ├── score_service.py
│   ├── position_service.py
│   └── alert_service.py
├── utils/
│   ├── indicators.py
│   ├── risk_management.py
│   └── data_fetcher.py
├── helpers/
│   ├── calculations.py
│   ├── validations.py
│   └── formatters.py
└── models/
    ├── schemas.py
    └── database.py
```

---

## 🗄️ Estrutura de Dados PostgreSQL

### Tabela: `backtest_config`
```sql
CREATE TABLE backtest_config (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    start_date DATE,
    end_date DATE,
    initial_capital DECIMAL(20,2),
    max_leverage DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Tabela: `market_data`
```sql
CREATE TABLE market_data (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP UNIQUE,
    price DECIMAL(20,2),
    volume DECIMAL(20,8),
    
    -- Indicadores Ciclo
    mvrv_z_score DECIMAL(10,4),
    realized_price_ratio DECIMAL(10,4),
    puell_multiple DECIMAL(10,4),
    
    -- Indicadores Momentum
    rsi_weekly DECIMAL(5,2),
    rsi_daily DECIMAL(5,2),
    funding_rate_7d DECIMAL(10,6),
    sth_sopr DECIMAL(10,4),
    long_short_ratio DECIMAL(10,4),
    
    -- Indicadores Técnicos
    ema_17 DECIMAL(20,2),
    ema_34 DECIMAL(20,2),
    ema_144 DECIMAL(20,2),
    ema_305 DECIMAL(20,2),
    ema_610 DECIMAL(20,2),
    bbw_percentage DECIMAL(5,2),
    
    -- Scores Calculados
    score_market DECIMAL(5,2),
    score_risk DECIMAL(5,2),
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_market_data_timestamp ON market_data(timestamp);
```

### Tabela: `backtest_trades`
```sql
CREATE TABLE backtest_trades (
    id SERIAL PRIMARY KEY,
    backtest_id INTEGER REFERENCES backtest_config(id),
    timestamp TIMESTAMP,
    action VARCHAR(20), -- 'ENTER', 'ADD', 'REDUCE', 'EXIT'
    
    -- Contexto da Decisão
    score_market DECIMAL(5,2),
    score_risk DECIMAL(5,2),
    mvrv_value DECIMAL(10,4),
    ema_distance DECIMAL(10,2),
    rsi_daily DECIMAL(5,2),
    
    -- Execução
    price DECIMAL(20,2),
    position_size_percent DECIMAL(5,2),
    leverage_before DECIMAL(5,2),
    leverage_after DECIMAL(5,2),
    
    -- Resultado
    pnl DECIMAL(20,2),
    pnl_percent DECIMAL(10,2),
    portfolio_value DECIMAL(20,2),
    
    reason TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Tabela: `backtest_results`
```sql
CREATE TABLE backtest_results (
    id SERIAL PRIMARY KEY,
    backtest_id INTEGER REFERENCES backtest_config(id),
    
    -- Performance Geral
    total_return DECIMAL(10,2),
    annualized_return DECIMAL(10,2),
    sharpe_ratio DECIMAL(10,4),
    sortino_ratio DECIMAL(10,4),
    max_drawdown DECIMAL(10,2),
    
    -- Estatísticas de Trade
    total_trades INTEGER,
    winning_trades INTEGER,
    losing_trades INTEGER,
    win_rate DECIMAL(5,2),
    avg_win DECIMAL(10,2),
    avg_loss DECIMAL(10,2),
    profit_factor DECIMAL(10,4),
    
    -- Comparação
    btc_hold_return DECIMAL(10,2),
    outperformance DECIMAL(10,2),
    
    -- Risk Metrics
    avg_leverage DECIMAL(5,2),
    max_leverage DECIMAL(5,2),
    time_in_market DECIMAL(5,2),
    
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🔧 Services Implementation

### `backtest_service.py`
```python
class BacktestService:
    """
    Principais métodos:
    - run_backtest(config: BacktestConfig) -> BacktestResult
    - calculate_scores(data: MarketData) -> Scores
    - check_entry_conditions(scores: Scores) -> bool
    - check_exit_conditions(scores: Scores, position: Position) -> bool
    - calculate_position_size(scores: Scores, mvrv: float) -> float
    """
```

### `score_service.py`
```python
class ScoreService:
    """
    Métodos de cálculo:
    - calculate_market_score(data: MarketData) -> float
    - calculate_cycle_score(mvrv, realized_ratio, puell) -> float
    - calculate_momentum_score(rsi_w, funding, sopr, ls_ratio) -> float
    - calculate_technical_score(emas, bbw) -> float
    - calculate_risk_score(health_factor, liq_distance) -> float
    """
```

### `position_service.py`
```python
class PositionService:
    """
    Gestão de posição:
    - calculate_leverage_limit(mvrv: float, rsi_monthly: float) -> float
    - should_add_position(ema_distance, rsi_daily) -> tuple[bool, float]
    - should_reduce_position(ema_distance, rsi_daily) -> tuple[bool, float]
    - calculate_stop_loss(mvrv: float) -> float
    """
```

---

## 📊 Lógica de Backtest

### 1. Loop Principal
```python
for each day in period:
    # 1. Calcular Scores
    market_score = calculate_market_score(day_data)
    risk_score = calculate_risk_score(current_position)
    
    # 2. Decisões de Trading
    if not has_position:
        if market_score > 60 and risk_score > 50:
            enter_position()
    else:
        # Check circuit breakers
        if risk_score < 30:
            close_position()
        elif market_score < 40:
            reduce_position(50%)
        else:
            # Tactical execution
            check_tactical_adjustments()
```

### 2. Cálculo de Scores
```python
# Score de Mercado (Camada 1)
cycle_score = (
    mvrv_score * 0.25 +
    realized_ratio_score * 0.20 +
    puell_score * 0.05
) * 0.5  # 50% peso

momentum_score = (
    rsi_weekly_score * 0.08 +
    funding_score * 0.07 +
    sth_sopr_score * 0.03 +
    ls_ratio_score * 0.02
) * 0.2  # 20% peso

technical_score = (
    ema_score * 0.20 +
    bbw_score * 0.10
) * 0.3  # 30% peso

market_score = cycle_score + momentum_score + technical_score
```

### 3. Execução Tática
```python
# Matriz EMA 144 + RSI
def check_tactical_execution(position, ema_distance, rsi_daily):
    if ema_distance > 20 and rsi_daily > 70:
        return "REDUCE", 40
    elif ema_distance > 20 and rsi_daily > 50:
        return "REDUCE", 25
    elif ema_distance < -10 and rsi_daily < 50:
        return "ADD", 35
    elif ema_distance < -10 and rsi_daily < 30:
        return "ADD", 75
    return "HOLD", 0
```

---

## 📈 Métricas de Performance

### Cálculos Essenciais
```python
# Sharpe Ratio
sharpe = (returns.mean() - risk_free_rate) / returns.std() * sqrt(365)

# Sortino Ratio  
downside_returns = returns[returns < 0]
sortino = (returns.mean() - risk_free_rate) / downside_returns.std() * sqrt(365)

# Maximum Drawdown
rolling_max = portfolio_values.expanding().max()
drawdowns = (portfolio_values - rolling_max) / rolling_max
max_drawdown = drawdowns.min()

# Profit Factor
profit_factor = sum(winning_trades) / abs(sum(losing_trades))
```

---

## 🎯 Endpoints da API

### Backtest Endpoints
```python
POST   /backtest/run              # Executar novo backtest
GET    /backtest/{id}/results     # Resultados completos
GET    /backtest/{id}/trades      # Lista de trades
GET    /backtest/{id}/metrics     # Métricas de performance
GET    /backtest/{id}/chart       # Dados para gráfico
```

### Analysis Endpoints
```python
GET    /analysis/optimal-params   # Parâmetros otimizados
GET    /analysis/sensitivity      # Análise de sensibilidade
GET    /analysis/monte-carlo      # Simulação Monte Carlo
POST   /analysis/compare          # Comparar estratégias
```

---

## 🔄 Fluxo de Dados

```
1. TradingView/APIs → market_data (atualização diária)
   ↓
2. score_service → Calcula scores em tempo real
   ↓
3. backtest_service → Simula decisões históricas
   ↓
4. position_service → Gerencia trades virtuais
   ↓
5. backtest_results → Armazena performance
   ↓
6. Frontend/Dashboard → Visualização
```

---

## 📋 Validações Importantes

### Pre-Backtest
```python
def validate_backtest_config(config):
    # Período mínimo: 6 meses
    # Capital inicial > 0
    # Max leverage <= 5x
    # Data início < Data fim
    # Verificar dados disponíveis
```

### Durante Execução
```python
def validate_trade(trade):
    # Leverage não excede limite MVRV
    # Capital disponível suficiente
    # Stop loss definido
    # Position size válido
    # Sem trades duplicados no mesmo timestamp
```

---

## 🚀 Otimizações

### Performance
- Cache de cálculos de EMA
- Batch insert para trades
- Índices em timestamp e backtest_id
- Cálculo incremental de métricas

### Parâmetros para Otimizar
```python
optimization_params = {
    'score_entry_threshold': [55, 60, 65],
    'score_exit_threshold': [35, 40, 45],
    'risk_score_minimum': [45, 50, 55],
    'ema_realize_distance': [15, 20, 25],
    'rsi_oversold': [25, 30, 35],
    'max_position_size': [80, 90, 100]
}
```

---

## 📊 Visualizações Recomendadas

1. **Equity Curve**: Portfolio vs BTC Hold
2. **Drawdown Chart**: Períodos de perda
3. **Trade Distribution**: Scatter de PnL
4. **Leverage Timeline**: Uso ao longo do tempo
5. **Score Evolution**: Scores vs Preço
6. **Win/Loss Streaks**: Sequências

---

## 🔍 Queries Úteis

### Performance por Período
```sql
SELECT 
    DATE_TRUNC('month', timestamp) as month,
    COUNT(*) as trades,
    AVG(pnl_percent) as avg_return,
    SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END)::float / COUNT(*) as win_rate
FROM backtest_trades
WHERE backtest_id = ?
GROUP BY month
ORDER BY month;
```

### Melhores/Piores Trades
```sql
-- Top 10 melhores
SELECT * FROM backtest_trades
WHERE backtest_id = ?
ORDER BY pnl_percent DESC
LIMIT 10;

-- Top 10 piores
SELECT * FROM backtest_trades
WHERE backtest_id = ?
ORDER BY pnl_percent ASC
LIMIT 10;
```

---

*Documentação Técnica - Sistema Backtest v1.0*