# 🗺️ Mapeamento Sistema BTC Turbo v1.5.0

## 1. VISÃO GERAL - ESTRUTURA DE PASTAS

```
app/
├── main.py                    # 🎯 Entry point FastAPI
├── config/                    # ⚙️ Settings e configurações
├── routers/                   # 🛤️ Endpoints FastAPI
│   ├── coleta.py              # POST coleta indicadores
│   ├── indicadores.py         # GET obter indicadores  
│   ├── score.py               # GET calcular scores
│   └── dashboards.py          # POST/GET dashboards v3
├── services/                  # 🏭 Lógica de negócio
│   ├── coleta/               # Coleta dados externos
│   │   ├── ciclos.py
│   │   ├── riscos.py
│   │   ├── momentum.py
│   │   └── tecnico.py
│   ├── indicadores/          # Obtenção dados brutos
│   │   ├── ciclos.py
│   │   ├── riscos.py
│   │   ├── momentum.py
│   │   └── tecnico.py
│   ├── scores/               # Cálculo de scores
│   │   ├── ciclos.py
│   │   ├── riscos.py
│   │   ├── momentum.py
│   │   └── tecnico.py
│   ├── dashboards/           # Dashboards v3
│   │   ├── dash_main_service.py
│   │   ├── dash_mercado_service.py
│   │   └── dash_mercado/     # Módulos mercado
│   └── utils/helpers/        # Funções auxiliares
│       ├── notion_helper.py
│       ├── tradingview_helper.py
│       └── postgres/         # Database helpers
└── doc/                      # 📚 Documentação técnica
```

## 2. MAPEAMENTO DETALHADO DOS ENDPOINTS

### 2.1 **COLETA** - `/api/v1/coletar-indicadores/{bloco}`

**Fluxo:** `POST /api/v1/coletar-indicadores/riscos`
```
routers/coleta.py
└── services/coleta/riscos.py
    └── utils/helpers/notion_helper.py → get_risco_data_from_notion()
    └── utils/helpers/postgres/indicadores/risco_helper.py → insert_dados_risco_completo()
```

**Fluxo:** `POST /api/v1/coletar-indicadores/tecnico`
```
routers/coleta.py
└── services/coleta/tecnico.py
    └── utils/helpers/tradingview_helper.py → buscar dados TradingView
    └── utils/helpers/postgres/indicadores/tecnico_helper.py → insert_dados_tecnico()
```

**Status dos Blocos:**
- ✅ **riscos** - Ativo (Notion)
- ✅ **tecnico** - Ativo (TradingView)
- ❌ **ciclos** - Importado via N8N
- ❌ **momentum** - Importado via N8N

### 2.2 **INDICADORES** - `/api/v1/obter-indicadores/{bloco}`

**Fluxo Comum:**
```
routers/indicadores.py
└── services/indicadores/{bloco}.py
    └── utils/helpers/postgres/indicadores/{bloco}_helper.py → get_dados_{bloco}()
```

### 2.3 **SCORES** - `/api/v1/calcular-score/{bloco}`

**Fluxo Comum:**
```
routers/score.py
└── services/scores/{bloco}.py
    ├── utils/helpers/postgres/indicadores/{bloco}_helper.py → get_dados_{bloco}()
    └── algoritmos de score específicos por bloco
```

### 2.4 **DASHBOARDS** - `/api/v3/dash-*`

**Fluxo:** `POST/GET /api/v3/dash-mercado`
```
routers/dashboards.py
└── services/dashboards/dash_mercado_service.py
    ├── services/dashboards/dash_mercado/data_collector.py
    ├── services/dashboards/dash_mercado/score_calculator.py
    ├── services/dashboards/dash_mercado/database_helper.py
    └── services/dashboards/dash_mercado/main_functions.py
```

**Fluxo:** `POST/GET /api/v3/dash-main`
```
routers/dashboards.py
└── services/dashboards/dash_main_service.py
    ├── 4 camadas de análise (mercado, risco, alavancagem, execução tática)
    ├── utils/gate_system_utils.py
    ├── utils/setup_detector_utils.py
    └── helpers/comprar_helper.py
```

### 2.5 **AUTOMAÇÃO N8N** (Externa)
- Executa a cada hora:
  - `POST /api/v1/coletar-indicadores/{bloco}`
  - `POST /api/v3/dash-mercado`
  - `POST /api/v3/dash-main`

## 3. ARQUIVOS ÓRFÃOS IDENTIFICADOS

### 3.1 **Status Limpeza**
✅ **Sistema Limpo** - Documentos V2 removidos
✅ **Funções Legacy** - `*_legacy()` excluídas  
✅ **Estrutura Organizada** - Sem código órfão

### 3.2 **Arquivos de Desenvolvimento** (⚠️ REVIEW)
```
todo.md                                      # 📝 Tarefas pendentes
doc/btcturbo-regras/backtest.md             # 📋 Não implementado
```

## 4. INCONSISTÊNCIAS DE VERSIONAMENTO
- não identificado
### 4.2 **URLs Inconsistentes**
- não identificado

## 5. ANÁLISE DE DEPENDÊNCIAS

### 5.1 **APIs Externas Ativas**
- ✅ **Notion API** - Coleta ciclos/momentum/riscos
- ✅ **TradingView** - Dados técnicos  
- ✅ **PostgreSQL** - Railway Database
- ✅ **BigQuery/Web3** - Mencionadas na doc

### 5.2 **Helpers Críticos**
```
utils/helpers/notion_helper.py               # 🔥 Core coleta
utils/helpers/tradingview_helper.py          # 🔥 Core técnico  
utils/helpers/postgres/base.py               # 🔥 Core database
utils/helpers/postgres/indicadores/*         # 🔥 Core CRUD
```

### 5.3 **Modularidade por Bloco**
- **CICLO** ✅ - Completo (coleta, indicadores, scores)
- **MOMENTUM** ✅ - Completo  
- **RISCOS** ✅ - Completo
- **TECNICO** ✅ - Completo

## 6. RECOMENDAÇÕES PRIORITÁRIAS

### 6.1 **Finalização v1.5.0** 
1. **main.py** - Atualizar version="1.5.0"
2. **README** - Atualizar descrição do projeto

### 6.2 **Próximas Funcionalidades**
1. Separar `tradingview_helper.py` em módulos
2. Implementar controle de operações
3. Sistema de logs estruturado
4. Gestão de stops

### 6.3 **Roadmap**
1. Alertas e notificações
2. Análise técnica aprofundada  
3. Sistema de backtest
4. Métricas de performance

---

**Sistema Status:** 🔄 **REORGANIZAÇÃO** - Partindo para v1.5.0 como base limpa