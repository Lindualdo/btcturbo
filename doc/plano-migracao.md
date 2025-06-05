# Plano de Migração BTC Turbo v0.25 → v5.0
*Cenário 2: Evolução Incremental - Mantendo Compatibilidade*

---

## 📊 Visão Macro

### Estratégia Geral
- **Manter**: Arquitetura FastAPI + PostgreSQL + estrutura atual
- **Adicionar**: 4 novos routers para camadas v5.0
- **Preservar**: Endpoints existentes funcionando normalmente
- **Evoluir**: Sistema atual → Sistema v5.0 incrementalmente

### Estrutura Final
```
app/
├── routers/
│   ├── [EXISTENTES] analise_btc.py, coleta.py, etc...
│   └── [NOVOS] camada_mercado.py, camada_risco.py, 
│                camada_dimensionamento.py, camada_tatico.py
├── services/
│   ├── [EXISTENTES] scores/, indicadores/, etc...
│   └── [NOVOS] camadas/, alertas/
└── [RESTO INALTERADO]
```

---

## 🎯 FASE 1 - Backend Refactoring (4 semanas)

### 1.1 Novos Routers (Semana 1)

#### `/api/v1/camada-mercado`
```python
# Consolida: Ciclos (50%) + Técnico (30%) + Momentum (20%)
# Input: usa /obter-indicadores/{bloco} existentes
# Output: Score 0-10, classificação, ação recomendada
```

#### `/api/v1/camada-risco` 
```python
# Health Factor + Distância Liquidação
# Input: indicadores_risco existentes + novos se necessário
# Output: Score 0-10, nível segurança, alertas
```

#### `/api/v1/camada-dimensionamento`
```python
# Tabela MVRV x RSI Mensal → Max Alavancagem
# Input: MVRV do ciclos + RSI mensal (novo indicador)
# Output: Alavancagem máxima, stop loss, fase mercado
```

#### `/api/v1/camada-tatico`
```python
# Matriz EMA144 + RSI Diário → Ações específicas
# Input: dados das 3 camadas anteriores
# Output: Ação (HOLD/ADD/REDUCE), tamanho, timing
```

### 1.2 Novos Indicadores (Semana 2)

#### Tabela: `indicadores_dimensionamento`
```sql
CREATE TABLE indicadores_dimensionamento (
    id SERIAL PRIMARY KEY,
    rsi_mensal DECIMAL(5,2),
    mvrv_z_score DECIMAL(10,4),
    max_alavancagem DECIMAL(5,2),
    stop_loss_percent DECIMAL(5,2),
    fase_mercado VARCHAR(50),
    timestamp TIMESTAMP DEFAULT NOW()
);
```

#### Tabela: `indicadores_tatico`
```sql
CREATE TABLE indicadores_tatico (
    id SERIAL PRIMARY KEY,
    ema_144_distance DECIMAL(10,2),
    rsi_diario DECIMAL(5,2),
    acao_recomendada VARCHAR(20),
    tamanho_posicao DECIMAL(5,2),
    score_confianca DECIMAL(5,2),
    timestamp TIMESTAMP DEFAULT NOW()
);
```

### 1.3 Sistema de Alertas (Semana 3)

#### Tabela: `alertas_operacionais`
```sql
CREATE TABLE alertas_operacionais (
    id SERIAL PRIMARY KEY,
    prioridade INTEGER CHECK (prioridade IN (1,2,3,4)),
    titulo VARCHAR(200),
    mensagem TEXT,
    acao_recomendada VARCHAR(100),
    origem_camada VARCHAR(50),
    valor_trigger DECIMAL(10,4),
    status VARCHAR(20) DEFAULT 'ATIVO',
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP
);
```

#### Service: `app/services/alertas/alertas_service.py`
```python
class AlertasService:
    def gerar_alertas_mercado(score_mercado, score_risco)
    def gerar_alertas_risco(health_factor, dist_liquidacao)
    def gerar_alertas_dimensionamento(mvrv, alavancagem_atual)
    def gerar_alertas_tatico(ema_distance, rsi_daily)
    def consolidar_alertas_ativos()
```

### 1.4 Integração e Scores (Semana 4)

#### Service: `app/services/camadas/camadas_service.py`
```python
class CamadasService:
    def calcular_score_mercado():
        # Ciclos 50% + Técnico 30% + Momentum 20%
        # Usar scores existentes com novos pesos
        
    def calcular_score_risco():
        # Health Factor + Distância Liquidação
        
    def calcular_dimensionamento(mvrv, rsi_mensal):
        # Tabela MVRV → retorna max_leverage
        
    def calcular_tatico(mercado, risco, dimensionamento):
        # Matriz EMA144 + RSI → ação específica
```

---

## 🎨 FASE 2 - Nova UI (6 semanas)

### 2.1 Escolha do Framework (Semana 1)
- **Opção A**: React + FastAPI como API pura
- **Opção B**: Vue.js + manter templates híbridos
- **Opção C**: Modernizar Jinja2 + HTMX para interatividade

### 2.2 Dashboard Novo (Semanas 2-4)
- **Página Principal**: 4 gauges das camadas + ação recomendada
- **Análise Detalhada**: Drill-down por camada
- **Centro de Alertas**: Sistema de notificações
- **Histórico**: Evolução dos scores

### 2.3 Mobile First (Semanas 5-6)
- **Responsividade**: Breakpoints para mobile/tablet/desktop
- **PWA**: Service workers para offline
- **Quick Actions**: Botões de ação rápida

---

## 🧪 FASE 3 - Sistema Backtest (8 semanas)

### 3.1 Arquitetura Backtest (Semanas 1-2)
```
app/services/backtest/
├── backtest_service.py      # Engine principal
├── score_service.py         # Cálculos históricos  
├── position_service.py      # Gestão de posição
└── performance_service.py   # Métricas
```

### 3.2 Database Schema (Semana 3)
```sql
-- backtest_config, market_data, backtest_trades, backtest_results
-- Conforme especificado na doc v5
```

### 3.3 Lógica de Trading (Semanas 4-6)
- **Loop Principal**: Simulação dia a dia
- **Decisões**: Baseadas nas 4 camadas
- **Execução**: Matriz tática automatizada
- **Risk Management**: Circuit breakers

### 3.4 Interface e Relatórios (Semanas 7-8)
- **Configurador**: Parâmetros de teste
- **Visualizações**: Equity curve, drawdown
- **Comparações**: vs Buy & Hold
- **Otimização**: Grid search parâmetros

---

## ⚡ FASE 4 - Performance (4 semanas)

### 4.1 Database Optimization (Semana 1)
- **Connection Pooling**: SQLAlchemy pool
- **Índices**: Otimizar queries das camadas
- **Query Optimization**: Consolidar consultas N+1

### 4.2 Caching Strategy (Semana 2)
- **Redis**: Cache distribuído para scores
- **Application Cache**: LRU para cálculos pesados
- **Database Cache**: Materialized views

### 4.3 Background Jobs (Semana 3)
- **Celery + Redis**: Coleta assíncrona
- **Scheduled Tasks**: Cálculos periódicos
- **Real-time**: WebSockets para updates

### 4.4 Monitoring (Semana 4)
- **APM**: Sentry ou similar
- **Metrics**: Prometheus + Grafana
- **Health Checks**: Endpoints detalhados

---

## 📋 Entregas por Fase

### FASE 1 - Backend ✅
- 4 novos endpoints camadas
- Sistema de alertas funcional
- Novos indicadores integrados
- Compatibilidade 100% mantida

### FASE 2 - UI ✅
- Dashboard moderno responsivo
- Centro de alertas interativo
- Mobile-first experience
- Real-time updates

### FASE 3 - Backtest ✅
- Engine completo de simulação
- Interface de configuração
- Relatórios de performance
- Otimização de parâmetros

### FASE 4 - Performance ✅
- Sistema otimizado < 200ms
- Cache hit rate > 90%
- Background processing
- Monitoring completo

---

## 🎯 Cronograma Total: 22 semanas (~5.5 meses)

**Marco 1** (4 sem): Backend v5.0 funcional  
**Marco 2** (10 sem): Sistema completo com UI nova  
**Marco 3** (18 sem): Backtest operacional  
**Marco 4** (22 sem): Sistema otimizado para produção

---

## 🔄 Estratégia de Deploy

### Compatibilidade Durante Migração
- **v0.25**: Endpoints existentes inalterados
- **v5.0**: Novos endpoints `/api/v1/camada-*`
- **Híbrido**: Frontend pode consumir ambos
- **Cutover**: Migração gradual por funcionalidade

### Testing Strategy
- **Unit Tests**: Cada service novo
- **Integration Tests**: Camadas integradas
- **E2E Tests**: Fluxos completos
- **Performance Tests**: Load testing

### Rollback Plan
- **Database**: Migrações reversíveis
- **Code**: Feature flags
- **API**: Versionamento
- **Frontend**: Deploy independente

---

*Última atualização: Janeiro 2025*