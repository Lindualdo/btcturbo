# BTC Turbo - Documentação Técnica de Arquitetura

## 📋 Visão Geral

Sistema de análise de indicadores Bitcoin construído com **FastAPI + PostgreSQL + Jinja2**, deployado no Railway. Versão atual: **1.0.25**.

### Stack Tecnológica
- **Backend**: FastAPI + SQLAlchemy + Psycopg2
- **Frontend**: Jinja2 Templates + Chart.js + CSS/JS vanilla
- **Database**: PostgreSQL (Railway)
- **Deploy**: Docker + Railway
- **APIs Externas**: TradingView, Notion, BigQuery, Web3

---

## 🏗️ Arquitetura Atual

### 1. Estrutura de Pastas
```
app/
├── config/                    # Configurações e settings
├── routers/                   # Endpoints FastAPI
├── services/                  # Lógica de negócio
│   ├── coleta/               # Coleta de dados externos
│   ├── scores/               # Cálculo de scores
│   ├── indicadores/          # Obtenção de dados brutos
│   └── utils/helpers/        # Funções auxiliares
├── templates/                 # Templates Jinja2 + assets
└── schemas/                   # Modelos Pydantic
```

### 2. Fluxo de Dados

#### Coleta → Processamento → Exibição
1. **Coleta** (`/api/v1/coletar-indicadores/{bloco}`)
   - Busca dados externos (Notion, TradingView, Web3)
   - Grava no PostgreSQL por bloco

2. **Obtenção** (`/api/v1/obter-indicadores/{bloco}`)
   - Lê dados brutos do banco
   - Retorna sem processamento

3. **Score** (`/api/v1/calcular-score/{bloco}`)
   - Aplica algoritmos de pontuação
   - Retorna score consolidado (0-10)

4. **Análise** (`/api/v1/analise-btc`)
   - Consolida todos os blocos
   - Aplica pesos e gera score final
   - Cache diário implementado

### 3. Blocos de Indicadores

| Bloco | Peso | Indicadores Principais | Fonte |
|-------|------|----------------------|-------|
| **Técnico** | 50% | EMAs (17,34,144,305,610) + Alinhamento | TradingView |
| **Ciclos** | 30% | MVRV Z-Score, Realized Ratio, Puell Multiple | Notion/BigQuery |
| **Momentum** | 20% | RSI, Funding Rates, Netflow, L/S Ratio | Notion |
| **Riscos** | 0%* | Health Factor, Dist. Liquidação | Web3/AAVE |

*Risco usado como redutor, não no cálculo principal*

---

## 🗄️ Estrutura de Dados

### PostgreSQL - Tabelas Principais

#### indicadores_tecnico (Mais Complexa)
```sql
-- EMAs por timeframe
ema_17_1w, ema_34_1w, ema_144_1w, ema_305_1w, ema_610_1w  -- Semanal
ema_17_1d, ema_34_1d, ema_144_1d, ema_305_1d, ema_610_1d  -- Diário

-- Scores calculados
score_1w_ema, score_1w_price, score_1d_ema, score_1d_price
score_consolidado_1w, score_consolidado_1d, score_final_ponderado

-- Metadados
btc_price_current, distancias_json, timestamp, fonte
```

#### Outras Tabelas (Padrão Simples)
```sql
indicadores_ciclo: mvrv_z_score, realized_ratio, puell_multiple
indicadores_momentum: rsi_semanal, funding_rates, exchange_netflow, long_short_ratio  
indicadores_risco: dist_liquidacao, health_factor, btc_price, alavancagem
```

#### Cache Consolidado
```sql
scores_consolidados: data, score_final, classificacao_geral, kelly_allocation, 
                    pesos_dinamicos, dados_completos (JSONB)
```

---

## 🔧 Padrões Implementados

### 1. Helpers PostgreSQL
**Localização**: `app/services/utils/helpers/postgres/`

Cada bloco possui 3 funções padrão:
- `get_dados_{bloco}()` - Busca mais recente
- `insert_dados_{bloco}()` - Insere novos dados  
- `get_historico_{bloco}()` - Histórico com limite

### 2. Response Patterns
```python
# Score Individual (por bloco)
{
    "bloco": "ciclos",
    "score_consolidado": 5.5,
    "classificacao_consolidada": "neutro", 
    "indicadores": {
        "MVRV_Z": {"valor": 2.1, "score": 6.0, "peso": "20%"}
    }
}

# Análise Consolidada
{
    "score_final": 6.18,
    "classificacao": "bom",
    "kelly": "50%",
    "acao": "Manter posição",
    "blocos": {...}
}
```

### 3. Template Architecture
- **Base Template**: `templates/base.html`
- **Componentes**: Navigation, Footer, Gauge Charts
- **Styles**: CSS unificado em `static/css/dashboard-unified.css`
- **JavaScript**: Core dashboard em `static/js/dashboard-core.js`

---

## ⚙️ Configurações e Deploy

### Environment Variables (.env)
```bash
# Database (Railway)
DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, DB_PORT
DATABASE_URL  # Fallback connection string

# APIs Externas
TV_USERNAME, TV_PASSWORD                    # TradingView
NOTION_TOKEN, NOTION_DATABASE_ID           # Notion
GOOGLE_APPLICATION_CREDENTIALS_JSON        # BigQuery
WALLET_ADDRESS, AAVE_RPC_URL               # Web3
```

### Docker + Railway Deploy
- **Dockerfile**: Python 3.11-slim + git para tvdatafeed
- **Auto-deploy**: Push para main branch
- **Health checks**: `/ping`, `/health`, `/api/v1/diagnostico/health-check`

---

## 🚨 Limitações e Problemas Atuais

### 1. Arquitetura
- **Monolito**: Tudo em um único serviço
- **Acoplamento**: Services conhecem detalhes de PostgreSQL
- **Cache Manual**: Sistema de cache próprio sem Redis
- **Logs**: Logging básico sem structured logging

### 2. Frontend
- **Sem Framework**: JavaScript vanilla + Chart.js
- **Template Pesado**: HTML inline nos routers
- **Responsividade**: CSS responsivo básico
- **Estado**: Sem gerenciamento de estado

### 3. Dados
- **APIs Externas**: Dependência crítica sem fallbacks robustos
- **Coleta Manual**: Alguns indicadores via Notion (processo manual)
- **Rate Limits**: Sem throttling para APIs externas
- **Validação**: Validação básica de dados coletados

### 4. Performance
- **N+1 Queries**: Múltiplas consultas sequenciais
- **Sem Connection Pool**: Conexões PostgreSQL por request
- **Cálculos Síncronos**: Score calculations bloqueiam requests
- **Cache Hit Rate**: Baixo devido à invalidação agressiva

### 5. Observabilidade
- **Métricas**: Sem APM ou métricas de performance
- **Alerting**: Sistema de alertas manual
- **Error Tracking**: Logs simples sem agregação
- **Monitoring**: Só health checks básicos

---

## 🚀 Oportunidades de Melhoria

### 1. Arquitetura (Prioridade Alta)

#### Separação de Responsabilidades
- **Repository Pattern**: Abstrair acesso ao PostgreSQL
- **Service Layer**: Isolar lógica de negócio dos routers
- **DTO Pattern**: Separar modelos de domínio dos schemas API

#### Async/Background Jobs
- **Celery + Redis**: Coleta de dados como jobs assíncronos
- **APScheduler**: Agendamento de coletas automáticas
- **WebSockets**: Updates em tempo real no dashboard

### 2. Performance (Prioridade Alta)

#### Database Optimization
```python
# Connection Pooling
from sqlalchemy.pool import QueuePool
engine = create_engine(url, poolclass=QueuePool, pool_size=20)

# Query Optimization  
def get_all_latest_indicators():
    return session.execute(text("""
        SELECT * FROM (
            SELECT *, ROW_NUMBER() OVER (PARTITION BY bloco ORDER BY timestamp DESC) as rn
            FROM all_indicators 
        ) WHERE rn = 1
    """))
```

#### Caching Strategy
```python
# Redis Cache
@cache(expire=300)
async def get_score_consolidado(incluir_risco: bool):
    # Expensive calculation
    pass

# Application-level cache
from functools import lru_cache
@lru_cache(maxsize=128)
def calculate_ema_scores(prices: tuple):
    pass
```

### 3. Frontend Modernization (Prioridade Média)

#### Framework Migration
- **FastAPI + React/Vue**: SPA para melhor UX
- **Server-Sent Events**: Real-time updates
- **Progressive Web App**: Offline capability

#### Component Architecture
```typescript
// React Component Example
interface GaugeProps {
  score: number;
  title: string;
  classification: string;
  clickable?: boolean;
}

const GaugeComponent: React.FC<GaugeProps> = ({ score, title, classification, clickable }) => {
  // Implementation
}
```

### 4. DevOps e Observabilidade (Prioridade Média)

#### Monitoring Stack
- **Prometheus + Grafana**: Métricas customizadas
- **Sentry**: Error tracking
- **DataDog/New Relic**: APM completo

#### CI/CD Pipeline
```yaml
# GitHub Actions
name: Deploy
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: pytest
      - name: Deploy to Railway
        run: railway deploy
```

### 5. Data Pipeline (Prioridade Baixa)

#### ETL Modernization
- **Apache Airflow**: Orchestração de coleta
- **DBT**: Transformações SQL
- **Great Expectations**: Data quality validation

#### Real-time Processing
```python
# Kafka/Redis Streams para real-time data
async def process_btc_price_update(price_data):
    # Update indicators
    # Broadcast to connected clients
    # Trigger recalculations if needed
```

---

## 📈 Roadmap Sugerido

### Fase 1 - Estabilização (1-2 sprints)
1. **Repository Pattern**: Abstrair PostgreSQL
2. **Connection Pooling**: Otimizar DB connections  
3. **Error Handling**: Melhorar tratamento de erros
4. **Structured Logging**: Implementar logs JSON

### Fase 2 - Performance (2-3 sprints)
1. **Redis Cache**: Cache distribuído
2. **Background Jobs**: Coleta assíncrona
3. **Query Optimization**: Otimizar consultas
4. **API Rate Limiting**: Throttling requests

### Fase 3 - Modernização (3-4 sprints)  
1. **Frontend Framework**: Migrar para React/Vue
2. **Real-time Updates**: WebSockets/SSE
3. **Monitoring**: APM e métricas
4. **CI/CD**: Pipeline automatizado

### Fase 4 - Escalabilidade (4-5 sprints)
1. **Microservices**: Quebrar monolito
2. **Event Sourcing**: Audit trail completo
3. **Data Lake**: Histórico de longo prazo
4. **Machine Learning**: Predições automatizadas

---

## 🎯 Conclusão

O BTC Turbo possui uma **arquitetura sólida** para um MVP, com separação clara de responsabilidades e padrões consistentes. A estrutura atual suporta bem o uso previsto, mas possui oportunidades claras de **modernização e otimização**.

**Próximos passos recomendados**:
1. Implementar **Repository Pattern** para melhor testabilidade
2. Adicionar **Redis cache** para performance
3. Migrar coleta para **background jobs**
4. Implementar **monitoring** básico

O projeto demonstra boas práticas de desenvolvimento e está bem posicionado para crescimento futuro com as melhorias sugeridas.