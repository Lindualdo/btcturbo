# BTC Turbo v1.7.0

Sistema de análise de indicadores Bitcoin para trading alavancado, construído com FastAPI + PostgreSQL.

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
| POST/GET | `/api/v1/dash-mercado` | Dashboard mercado |
| POST/GET | `/api/v1/dash-main` | Dashboard principal (4 camadas) |
|GET | `/api/v1/dash-finance` | /health-factor, /alavancagem, /patrimonio , /capital-investido (fazer) |

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

## 📝 Próximas Fases

- **1.7.0**: gatilhos score + score emas sem expansão + controle de operações (stop, RP, compras)
- **1.8.0**: alertas
- **1.9.0**: Backtest + métricas de performance

---

**Desenvolvido para: Hold alavancado - gestão ativa do capital satelite - otimização dos resultados com gestão de risco**