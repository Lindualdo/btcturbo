# BTC Turbo v1.9

Sistema de análise de indicadores Bitcoin para trading alavancado, construído com FastAPI + PostgreSQL.

## Alterações s serem implementadas nesta versão
    Fazer
    - será criado uma nova camada chamada tática com indicadores para tomada de decisão (comprar, vender..)
    - o score dessa camada já indicará se está no momento de agir, apenas nos extremos, correspondendo com a estratégia de Hold..
    - Score de 0 a 100:  0 venda 100 compra meio neutro Hold
    - Novos indicadores da camada tática:  RSI diário, suporte/resistencia, Delta OI, Funding Rates, Volume Spot

## 1.9.6 - Alavancagem - feito
- Bloco Alavancagem independente (retirar do bloco dash-main, será descontinuado)

## 1.9.7 - Riscos


# 1.9.8 - Stop

# Importantes

# 1.9.9 - Alertas criticos
- GATILHOS DE AÇÃO
- REGRAS DE DECISÃO PRIORITÁRIAS
- SISTEMA DE PROTEÇÃO SIMPLIFICADO

# 1.9.10 - Decisão Tática

# 1.9.11 - Camada operacional (controle de operações)


# Não prioritárias

## Após Concluir as novas camadas + sistema de STOP

- INDICADOR ADICIONAL: DISTÂNCIA EMA 200
- INDICADORES COMPLEMENTARES (Confirmação)
- USAR IFR Mensal / EMA 200, para definir a fase do mercado Bull Inicial, Bull Final...


# Após concluir essas implementações - Iniciar a Camada Tática

## 🏗️ Arquitetura

```
app/
├── main.py                    # Entry point FastAPI
├── config/                    # Settings e configurações
├── routers/                   # Endpoints API REST
├── services/                  # Lógica de negócio
│   ├── coleta/               # Coleta dados externos (Notion, TradingView)
│   ├── indicadores/          # Obtenção dados brutos do banco
│   ├── scores/               # Algoritmos de pontuação (0-10)
│   ├── dashboards/           # Dashboards principais
│   └── utils/helpers/        # Funções auxiliares reutilizáveis
└── doc/                      # Documentação técnica
```

## 🎯 Stack Tecnológica

- **Backend**: FastAPI + SQLAlchemy + Psycopg2
- **Database**: PostgreSQL (Railway)
- **Deploy**: Docker + Railway
- **APIs Externas**: TradingView, Notion, BigQuery, Web3

## 📋 Endpoints Principais

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/v1/coletar-indicadores/{bloco}` | Coleta dados externos |
| GET | `/api/v1/obter-indicadores/{bloco}` | Obter dados brutos |
| GET | `/api/v1/calcular-score/{bloco}` | Calcular scores (0-10) |
| POST/GET | `/api/v1/dash-mercado` | Dashboard mercado | aplicar_gatilho: bool = False (gatilhos para ajuste de score)
| POST/GET | `/api/v1/dash-main` | Dashboard principal (4 camadas) |
|GET | `/api/v1/dash-finance` | /health-factor, /alavancagem, /patrimonio , /capital-investido (fazer) |
| GET | `/api/v1/calcular-score-tendecia` | Calcular score, grava na base e retorna o score tendencia|
| POST | `/api/v1/decisao-estrategica` | processa e grava a ultima decisão estratégica - Score tendencia + score ciclo + decisões|
| GET | `/api/v1/decisao-estrategica` | Obter ultima decisão estratégica - Score tendencia + score ciclo + decisões|
| GET | `/api/v1/decisao-estrategica-detalhe` | Obter detalhes da ultima decisão estratégica - score consolidado + indicadores detalhado|

decisao-estrategica-detalhe

**Blocos disponíveis**: `ciclos`, `riscos`, `momentum`, `tecnico`

## ⚡ Automação

Sistema executado a cada hora via N8N:
1. Coleta indicadores por bloco
2. Processa dashboards
3. Atualiza scores consolidados

## 🔧 Padrões de Desenvolvimento

### **Estrutura Obrigatória**

```python
# Sempre separar por camadas (routers > services > utils > helpers)
routers/endpoint.py → services/logic.py → utils/helpers/database.py

# Arquivos máximo 200 linhas
# Uma responsabilidade por arquivo
# Imports organizados: stdlib > third-party > app
```

### **Nomenclatura**

```python
# Funções: verbo_substantivo
def coletar_indicadores(), obter_dados_ciclo()

# Variáveis: snake_case descritivo
dados_mercado, score_consolidado, timestamp_atual

# Classes: PascalCase
class TradingViewHelper, DatabaseConnection
```

### **Tratamento de Erros**

```python
# OBRIGATÓRIO: try/catch em todas as funções críticas
def funcao_critica():
    try:
        logger.info("🔄 Iniciando operação...")
        # lógica
        logger.info("✅ Sucesso")
        return resultado
    except Exception as e:
        logger.error(f"❌ Erro: {str(e)}")
        return {"status": "erro", "detalhes": str(e)}
```

### **Logs Estruturados**

```python
import logging
logger = logging.getLogger(__name__)

# Usar emojis para identificação visual
logger.info("🔄 Iniciando...")    # Processo
logger.info("✅ Sucesso")         # Sucesso  
logger.warning("⚠️ Alerta")       # Warning
logger.error("❌ Erro")           # Erro
logger.info("🔍 Debug")           # Debug
```

### **Database Helpers**

```python
# Sempre usar helpers existentes
from app.services.utils.helpers.postgres.base import execute_query

# NUNCA escrever SQL direto nos services
# Centralizar queries nos helpers correspondentes
```

### **APIs Externas**

```python
# Sempre com fallbacks e timeouts
def buscar_tradingview():
    try:
        response = requests.get(url, timeout=10)
        return response.json()
    except Exception as e:
        logger.error(f"❌ TradingView falhou: {e}")
        return None  # NUNCA retornar dados simulados
```

## 🚫 Regras Rígidas

### **PROIBIDO**

- ❌ Valores fixos ou simulados no código
- ❌ Over-engineering sem solicitação
- ❌ Refatoração sem aprovação
- ❌ Supor informações não confirmadas
- ❌ Misturar responsabilidades no mesmo arquivo
- ❌ Commits sem testes das funcionalidades

### **OBRIGATÓRIO**

- ✅ Confirmar com o usuário se não tiver certeza
- ✅ Fallbacks retornam erro + log (nunca dados falsos)
- ✅ Separar implementações nas camadas definidas
- ✅ Documentar regras de negócio no código
- ✅ Logs nas etapas críticas para rastreio
- ✅ Reutilizar funções existentes antes de criar novas

**Ambiente Atual**: Mac + VS Code + GitHub + Railway

1. **Desenvolvimento**: VS Code local
2. **Commit**: Direto no main via GitHub
3. **Deploy**: Automático na Railway a cada commit
4. **Validação**: Frontend funcionando + endpoints manuais

## 🚀 Status Atual

- ✅ **Backend**: 80% completo
- ✅ **Frontend**: Funcionando (dash-main + dash-mercado + dash-finance)  Vercel + Vite
- ✅ **Deploy**: Automático Railway
- ✅ **APIs**: TradingView + Notion + Web3 integradas
- 🔄 **Próximo**: Gatilhos (peso de score) + Controle de operações + alertas

## 🔗 Integrações Externas

- **Notion**: Database indicadores (ciclos, momentum, riscos)
- **TradingView**: Dados técnicos real-time
- **AAVE**: Health Factor via Web3
- **Railway**: PostgreSQL database
- **N8N**: Automação de coletas

---

**Desenvolvido para: Hold alavancado - gestão ativa do capital satelite - otimização dos resultados com gestão de risco**