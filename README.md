# BTC Turbo - Documentação Técnica de Arquitetura - 5.1.1
Doc: btc-system-improvements melhorias: 5.1

## 📋 Visão Geral

Sistema de análise de indicadores Bitcoin construído com **FastAPI + PostgreSQL + Jinja2**, deployado no Railway. Versão atual: **1.0.25 - migrando para 5.0.0**

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

#### `/api/v1/analise-risco`  - 5.0.3 - feito - 06/06
```python
# Health Factor + Distância Liquidação
# Input: indicadores_risco existentes + novos se necessário
# Output: Score 0-10, nível segurança, alertas
```

#### `/api/v1/analise-mercado` - 5.0.2 - feito  - 06/06
```python
# Consolida: Ciclos (50%) + Técnico (30%) + Momentum (20%)
# Input: usa /obter-indicadores/{bloco} existentes
# Output: Score 0-10, classificação, ação recomendada
```

#### `/api/v1/analise-alavancagem` -  5.0.4 - feito - 06/06
```python
# Tabela MVRV x RSI Mensal → Max Alavancagem
# Input: MVRV do ciclos + RSI mensal (novo indicador)
# Output: Alavancagem máxima, stop loss, fase mercado
# Output: Simulação do valor permitido em dolares para alavancagem
```

#### `/api/v1/analise-tatico` 5.0.5 / 5.0.6 / 5.0.7 - feito - 06/06
```python
# Matriz EMA144 + RSI Diário → Ações específicas
# Input: dados das 3 camadas anteriores
# Output: Ação (HOLD/ADD/REDUCE), tamanho, timing
```
---
### Alertas prioritário (criticos, urgentes, volatilidade e tático) - 5.0.8 a 5.0.14 - feito 08/06
`/api/v1/alertas/verificar` - Endpoint principal - retorna alertas disparados
`/alertas-debug/criticos` - debug da categoria  - retorna alertas + dados para validação
`/alertas-debug/urgentes` - debug da categoria  - retorna alertas + dados para validação
`/alertas-debug/bolatilidade` - debug da categoria  - retorna alertas + dados para validação
`/alertas-debug/taticos` - debug da categoria  - retorna alertas + dados para validação

## Melhorias - Versão sistema - 5.1 

### Alteração: Aumentar peso da Análise Técnica - 5.1.1 - feito - 08/06

**De:**
```
├── CICLO: 50%
├── MOMENTUM: 20%
└── TÉCNICO: 30%
```

**Para:**
```
├── CICLO: 40%      ← Reduzido
├── MOMENTUM: 20%   ← Mantém
└── TÉCNICO: 40%    ← Aumentado
```

**Justificativa:**
- AT antecipa movimentos on-chain
- Setup atual (4 ATHs semanais) não capturado com peso 30%
- Price action é leading indicator
- Sistema atual muito conservador para momentum claro

---

### Alteração: Substituir MVRV Z-Score por combinação MVRV + NUPL - 5.1.2 - feito - 08/06

**De:**
```
CICLO
├── MVRV Z-Score (50%)
├── Realized Price Ratio (40%)
└── Puell Multiple (10%)
```

**Para:**
```
CICLO 
├── MVRV Z-Score (30%)    ← Reduzido
├── NUPL (20%)            ← Novo
├── Realized Price Ratio (40%)
└── Puell Multiple (10%)
```

**Justificativa:**
- MVRV tem lag significativo em topos (10-20% após pico)
- NUPL mais responsivo: >0.75 = euforia clara
- Diversificação reduz dependência de indicador único
- Histórico: MVRV errou topos 2021 e 2024

```python
# NUPL > 0.75 = euforia/topo (score 1-2)
# NUPL 0.5-0.75 = sobrecomprado (score 3-4)  
# NUPL 0.25-0.5 = neutro (score 5-6)
# NUPL 0-0.25 = acumulação (score 7-8)
# NUPL < 0 = oversold extremo (score 9-10)
```
---


### Alteração de Exchange Net Flow por SOPR (Spent Output Profit Ratio) - 5.1.3 - feito - 08/06

---

### - Padronização de base 100 nos escores consolidados - 5.1.4 - feito - 09/10

### - resolver problrma com importação de NUPN e SOPR - não conseguimos resolver - 5.1.5 - feito 10/10
- muito codigo desnecessário para esses dois campos, causando vários probemas
- foi feito refactore, simoplificando os arquivos e causou muitos erros no sistema
- por fim, a importação de ciclos e momentum está sendo feita no n8n

## API Dashboard - Usada pelo Dash externo Vercel

### - home - cabeçalho - 5.1.6 - feito

### - home - mercado - 5.1.7 - feito

## Fase 1 (Imediato):
1. ✅ Sistema de alertas críticos (já implementado)
2. ⏳ Adicionar alertas de oportunidade técnica
3. ⏳ Incluir indicadores_timing no JSON

## 🔔 4. Novos Alertas Prioritários



### 4.1 Alertas de Oportunidade Técnica - 5.1.5
```python
# Setup Técnico Forte
if consecutive_weekly_ath >= 3:
    alert("📈 Setup técnico forte - 3+ ATHs semanais")
    
if golden_cross_4h and score < 60:
    alert("⚡ Golden cross 4H com score neutro - divergência")
    
if price_test_psychological and held:
    alert("💪 Suporte psicológico defendido - força compradora")
```

### 4.2 Alertas de Divergência . 5.1.6
```python
# Técnica vs On-chain
if technical_score > 80 and cycle_score < 50:
    alert("🔄 Divergência: Técnica forte, on-chain fraco")
    
if ema_alignment_perfect and mvrv > 3:
    alert("⚠️ EMAs perfeitas mas MVRV alto - cautela")
```

### 4.3 Alertas de Execução - 5.1.7
```python
# Zona neutra com oportunidade
if ema_distance < 10 and rsi > 70:
    alert("📊 RSI alto em zona neutra - realizar parcial")
    
if ema_distance < 10 and rsi < 40:
    alert("🛒 RSI baixo em zona neutra - oportunidade compra")
```

---

## Novo: Bônus por Momentum Semanal

```python
def calcular_bonus_momentum():
    bonus = 0
    
    # Velas verdes consecutivas
    if consecutive_green_weekly >= 3:
        bonus += 5
        
    # ATH semanal
    if weekly_close == all_time_high:
        bonus += 3
        
    # Defesa de suporte psicológico
    if tested_and_held_round_number:
        bonus += 2
        
    return min(bonus, 10)  # Máximo 10 pontos
```