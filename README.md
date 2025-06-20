# BTC Turbo - 5.3.16

## 📋 Visão Geral

Sistema de análise de indicadores Bitcoin construído com **FastAPI + PostgreSQL, deployado no Railway

### Stack Tecnológica
- **Backend**: FastAPI + SQLAlchemy + Psycopg2
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
```

### 2. Fluxo de Dados

#### Coleta → Processamento → Exibição
1. **Coleta POST** (`/api/v1/coletar-indicadores/{bloco}`)
   - Busca dados externos (Notion, TradingView, Web3)
   - Grava no PostgreSQL por bloco

2. **Obtenção GET** (`/api/v1/obter-indicadores/{bloco}`)
   - Lê dados brutos do banco
   - Retorna sem processamento

3. **Score GET** (`/api/v1/calcular-score/{bloco}`)
   - Aplica algoritmos de pontuação
   - Retorna score consolidado (0-10)

4. **Dashboard POST/GET** (`/api/v3/dash-mercado`)
   - POST carrega os dados e GET obtem 
   - indicadores + score de mercado (ciclo, técnico e momentum)

5. **Dashboard POST/GET** (`/api/v3/dash-main`)
   - POST carrega os dados e GET obtem 
   - dados do dash principal home (4 camadas de analise - Mercado, riscos, alavancagem e Ações estratégica)


### 3. Automação acionada a cada hora via N8N 
- coleta indicadores (/api/v1/coletar-indicadores/{bloco})
- carrega dados do dash mercado (/api/v3/dash-mercado)
- carrega dados do dash main (/api/v3/dash-main)

### 4. Dashboard - Frontend Vercer + Vit 
- https://btcturbo-frontend.vercel.app
