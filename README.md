# BTC Turbo - Documentação Técnica de Arquitetura

## 📋 Visão Geral

Sistema de análise de indicadores Bitcoin construído com **FastAPI + PostgreSQL + Jinja2**, deployado no Railway. Versão atual: **1.0.25 - migrando para 5.0.0**

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

## 🎯 FASE 1 - Backend Refactoring

### 1.1 Novos Routers

#### `/api/v1/camada-mercado`
```python
# Consolida: Ciclos (50%) + Técnico (30%) + Momentum (20%)
# Input: usa /obter-indicadores/{bloco} existentes
# Output: Score 0-10, classificação, ação recomendada
```

#### `/api/v1/camada-risco`  - feito
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
---
