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

---

## 🎯 FASE 1 - Backend Refactoring

### 5.0.0 - criação do projeto - feito 05/06
- excluido documentos e arquivos descontinuados
- retirado toda interface visual - frontend (será contruida react)

### 5.0.1 - Ajustes de score - feito 05/06
- novos pesos por bloco
- incluido BBW no bloco de analise tecnica

### 1.2 Novos Routers

#### `/api/v1/camada-risco`  - feito junto da v 5.0.1 05/06
```python
# Health Factor + Distância Liquidação
# Input: indicadores_risco existentes + novos se necessário
# Output: Score 0-10, nível segurança, alertas
```

#### `/api/v1/camada-mercado`
```python
# Consolida: Ciclos (50%) + Técnico (30%) + Momentum (20%)
# Input: usa /obter-indicadores/{bloco} existentes
# Output: Score 0-10, classificação, ação recomendada
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


## 🎯 Estrutura de 4 Camadas

### Camada 1: Análise de Mercado (Score 0-100)
**Pergunta:** "O mercado está favorável para estar posicionado?"

```
CICLO (50%) - peso do bloco
├──Score_Bloco - soma do score ponderado de cada indicador
├── MVRV Z-Score (50%)
│   └── < 0: Score 9-10 | 0-2: Score 7-8 | 2-4: Score 5-6 | 4-6: Score 3-4 | > 6: Score 0-2
├── Realized Price Ratio (40%)
│   └── < 0.7: Score 9-10 | 0.7-1: Score 7-8 | 1-1.5: Score 5-6 | 1.5-2.5: Score 3-4 | > 2.5: Score 0-2
└── Puell Multiple (10%)
    └── < 0.5: Score 9-10 | 0.5-1: Score 7-8 | 1-2: Score 5-6 | 2-4: Score 3-4 | > 4: Score 0-2

MOMENTUM (20%) - peso do bloco
├── Score_Bloco - soma do score ponderado de cada indicador
├── RSI Semanal (40%)
│   └── < 30: Score 9-10 | 30-45: Score 7-8 | 45-55: Score 5-6 | 55-70: Score 3-4 | > 70: Score 0-2
├── Funding Rates 7D (35%)
│   └── < -0.05%: Score 9-10 | -0.05-0%: Score 7-8 | 0-0.02%: Score 5-6 | 0.02-0.1%: Score 3-4 | > 0.1%: Score 0-2
├── Exchange_Netflow (15%) - será substituido por STH-SOPR
│   └── < 0.9: Score 9-10 | 0.9-0.97: Score 7-8 | 0.97-1.03: Score 5-6 | 1.03-1.1: Score 3-4 | > 1.1: Score 0-2
└── Long/Short Ratio (10%)
    └── < 0.8: Score 9-10 | 0.8-0.95: Score 7-8 | 0.95-1.05: Score 5-6 | 1.05-1.3: Score 3-4 | > 1.3: Score 0-2

TÉCNICO (30%) - peso do bloco
├── Score_Bloco - soma do score ponderado de cada indicador
├── Sistema EMAs (70%)
│   ├── Alinhamento: EMA17>34>144>305>610 = Score 10 (50%)
│   └── Posição: Preço vs cada EMA (50%)
└── Bollinger Band Width (30%)
    └── < 5%: Score 9-10 | 5-10%: Score 7-8 | 10-20%: Score 5-6 | 20-30%: Score 3-4 | > 30%: Score 0-2
```
    **Decisão:** Score > 60 = Mercado favorável ✅

---

### Camada 2: Gestão de Risco (Score 0-100)
**Pergunta:** "Minha posição atual está segura?"

```
├── Health Factor AAVE (50%)
│   └── > 2.0: Score 90-100 | 1.5-2.0: Score 70-80 | 1.3-1.5: Score 50-60 | 1.1-1.3: Score 30-40 | < 1.1: Score 0-20
└── Distância Liquidação (50%)
    └── > 50%: Score 90-100 | 30-50%: Score 70-80 | 20-30%: Score 50-60 | 10-20%: Score 30-40 | < 10%: Score 0-20
```

**Decisão:** Score > 50 = Posição segura ✅

---

### Camada 3: Dimensionamento (Tabela MVRV)
**Pergunta:** "Qual alavancagem máxima posso usar?"

| MVRV | RSI Mensal | Fase | Max Alavancagem | Stop Loss |
|------|------------|------|-----------------|-----------|
| < 1.0 | < 30 | Bottom/Capitulação | 3.0x | -15% |
| 1.0-2.0 | 30-50 | Acumulação | 2.5x | -12% |
| 2.0-3.0 | 50-70 | Bull Médio | 2.0x | -10% |
| > 3.0 | > 70 | Euforia/Topo | 1.5x | -8% |

---

### Camada 4: Execução Tática
**Pergunta:** "Quando e quanto adicionar/realizar?"

#### Matriz de Decisão EMA 144 + RSI Diário

| Distância EMA 144 | RSI Diário | Ação | Tamanho | Justificativa |
|-------------------|------------|------|---------|---------------|
| > +20% | > 70 | **REALIZAR** | 40% | Extremo sobrecomprado |
| > +20% | 50-70 | **REALIZAR** | 25% | Muito esticado |
| > +20% | < 50 | **HOLD** | 0% | Divergência, aguardar |
| +10% a +20% | > 70 | **REALIZAR** | 25% | Sobrecomprado |
| +10% a +20% | 50-70 | **HOLD** | 0% | Tendência saudável |
| +10% a +20% | < 50 | **HOLD** | 0% | Momentum fraco |
| -5% a +10% | Qualquer | **HOLD** | 0% | Zona neutra |
| -10% a -5% | > 50 | **HOLD** | 0% | Sem confirmação |
| -10% a -5% | < 50 | **ADICIONAR** | 35% | Desconto + oversold |
| < -10% | > 30 | **ADICIONAR** | 50% | Grande desconto |
| < -10% | < 30 | **ADICIONAR** | 75% | Capitulação |

---
