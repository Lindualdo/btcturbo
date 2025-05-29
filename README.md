# BTC TURBO - v1.0.11

## 🎯 Objetivo da Documentação

Esta documentação técnica define claramente o padrão arquitetural, responsabilidades das APIs, estrutura de pastas e fluxo de trabalho, facilitando o desenvolvimento organizado e evitando quebras na implementação.

---

## Notas da versão - 1.0.10 - feito

- Conlcuido dashboads de analises (riscos, ciclos, momentum e técnica)
- organização melhor do main
- status de funcionamento na home e links para diagnosticos e Health check
- dash de anlise tecnica ainda usando api externa - precisamos implementar (mais complexa)
- https://btcturbo-production.up.railway.app/dashboard/

---

## 1.0.11  - Dashboard consolidao  - Home - feito
- Concluir a api de analise consolidada - api/v1/analise-btc
- atualizar a home do dash para incluir a analise consolidada de cada bloco com o score geral

---

## 1.0.12 - redistribuir pesos - bloco momentum  
- alterar api obter-indicadore, calcular-score - analise-btc
- alterar dash momentum
- revisar dash consolidados para avaliar impacto

´´´

├── RSI Semanal (12%) ← +2%
├── Funding Rates (10%) ← +2%
├── Exchange Netflow 7D (5%) ← NOVO
└── Long/Short Ratio (3%) ← Mantém

´´´
---

## 1.0.13 -  coleta de dados

- Docs: 
https://github.com/Lindualdo/btcturbo/blob/main/doc/validation-limites-indicadores.md


- validação dos valores coletados
- coleta dos indicadores e gravação no Postgres
- registrar a fonte de cada indicador (hoje está uma fonte para todo o bloco) 
* notion
* Trandview
* web3
* APIs

- Inclusão de dois novos indicadores no bloco momentum
* Stablecoin Supply Ratio - SSR (2%)
* Exchange Netflow 7D (3%)


## 1.0.14 - alertas
- implementar sistemas de alertas
https://github.com/Lindualdo/btcturbo/blob/main/doc/btcturbo-alertas.espc.md

---

## 1.0.15 - excluir indicadores descontinuados da tabela de riscos (exchange_netflow, stablecoin_ratio)

## 🗂 Estrutura do Projeto

```
app/
├── routers/
│   ├── coleta.py               # APIs de coleta de indicadores externos
│   ├── indicadores.py          # APIs para obter dados brutos do banco
│   ├── score.py                # APIs para cálculo do score individual
│   └── analise.py              # API consolidada final
└── services/
    ├── coleta/                 # Coleta dos dados externos - fallback - gravar valor zero
    │   ├── ciclo.py
    │   ├── momentum.py
    │   ├── risco.py
    │   └── tecnico.py
    ├── scores/                 # Cálculos de scores blocos - valor zero no indicador - desconsiderar percentual
    │   ├── ciclo.py
    │   ├── momentum.py
    │   ├── risco.py
    │   └── tecnico.py
    └── utils/                      # Funções auxiliares e comuns   
        ├── ciclo.py
        ├── momentum.py
        ├── cache.py
        ├── tecnico-emas.py
        ├── tecnico-padroes.py
        ├── helpers         # Coleta dos dados externos
            postgrees.py
            notion.py
            api-clasnode.py
            trandview.py     
```

---
## 🗂 Estrutura dos Helpers - atualizado na versão 1.0.5

app/services/utils/helpers/postgres/
├── __init__.py              # Facilita importações
├── base.py                  # Conexão + execute_query genérica
├── ciclo_helper.py         # 3 funções específicas do ciclo
├── momentum_helper.py      # 3 funções específicas do momentum  
├── risco_helper.py         # 3 funções específicas do risco
├── tecnico_helper.py       # 3 funções específicas do técnico
└── utils.py                # Health check + diagnósticos


## 🔄 Fluxo Completo e Responsabilidades

| Etapa           | API                                    | Responsabilidade                         |
| --------------- | -------------------------------------- | ---------------------------------------- |
| 1. Coleta       | `POST /api/v1/coletar-indicadores`     | Buscar dados externos e gravar no banco  |
| 2. Recuperação  | `GET /api/v1/obter-indicadores/{bloco}`| Ler indicadores brutos do banco          |
| 3. Score        | `GET /api/v1/calcular-score/{bloco}`   | Calcular score a partir dos dados brutos |
| 4. Consolidação | `GET /api/v1/analise-btc`              | Consolidar e gerar score final e alertas |

---

### POST /api/v1/diagnostico/setup-database


## Fluxo padrão de cada Processos - APIs

### 1. 📥 Processo de Coleta
router (coleta.py)
   └─▶ services/coleta/{bloco}.py
         └─▶ utils/cache.py
               └─▶ utils/helpers_{indicador}.py
                     └─▶ [Grava Dados Brutos no PostgreSQL]


### 2. 📤 Processo Obter Dados Brutos
router (indicadores.py)
   └─▶ [Consulta Dados Brutos no PostgreSQL]

### 3. 📊 Processo de Cálculo de Score
router (score.py)                               
   └─▶ services/scores/{bloco}.py
         └─▶ [Consulta Dados Brutos no PostgreSQL]
               └─▶ utils/helpers_{indicador}.py
                     └─▶ [Retorna Score calculado]


### 4. router (alertas.py)
   └─▶ services/alertas.py
         └─▶ utils/helpers_alertas.py
               └─▶ [Retorna lista de alertas ativos]


### 5. 📌 Processo Consolidado Final

router (analise.py)
   ├─▶ services/scores/{bloco}.py (todos blocos)
   │     └─▶ utils/helpers_{indicador}.py
   └─▶ services/alertas.py
         └─▶ utils/helpers_alertas.py
               └─▶ [Gera resposta consolidada final com scores e alertas relacionado a todos os blocos]

---


## 🚩 Padrões das APIs

### 🔹 API Calcular Score Individual

**Endpoint**:

```bash
GET /api/v1/calcular-score/{bloco}
```

**Exemplo real da resposta (Bloco Ciclos)**:

```json
{
    "bloco": "ciclos",
    "score": 5.5,
    "indicadores": {
        "MVRV_Z": {
            "valor": 2.1,
            "score": 6.0
        },
        "Realized_Ratio": {
            "valor": 1.3,
            "score": 5.5
        },
        "Puell_Multiple": {
            "valor": 1.2,
            "score": 5.0
        }
    }
}

```

**A Saida da APi analise-btc**:

2. API /api/v1/analise-btc - Formato Principal

```json
json{
    "timestamp": "2025-05-26T13:23:55.242171Z",
    "score_final": 5.85,
    "score_ajustado": 5.27,
    "modificador_volatilidade": 0.9,
    "classificacao_geral": "Neutro",
    "kelly_allocation": "25%",
    "acao_recomendada": "Manter posição conservadora",
    "alertas_ativos": [
        "Volatilidade elevada",
        "EMA200 como resistência"
    ],
    "pesos_dinamicos": {
        "ciclo": 0.40,
        "momentum": 0.25,
        "risco": 0.15,
        "tecnico": 0.20
    },
    "blocos": {
        "ciclo": {
            "score": 5.5,
            "indicadores": {
                "MVRV_Z": {
                    "valor": 2.1,
                    "score": 6.0
                },
                "Realized_Ratio": {
                    "valor": 1.3,
                    "score": 5.5
                },
                "Puell_Multiple": {
                    "valor": 1.2,
                    "score": 5.0
                }
            }
        }
    }
}
```

---

## 📚 Orientações Gerais


* Cada arquivo `.py` deve ser pequeno e focado em UMA única responsabilidade.
* Não misture lógica de coleta com cálculos ou lógica de exposição.
* Utilize e mantenha padrões de respostas JSON claramente definidos e consistentes.
* Sempre documente alterações na estrutura padrão, justificando a mudança claramente no README.

---

## 🛠️ Padrões Técnicos

* **Framework**: FastAPI
* **Banco de Dados**: PostgreSQL
* **ORM**: SQLAlchemy
* **Deploy**: Railway (Docker)
* **Formato de Dados**: JSON padrão estabelecido

---

## 🔧 CONFIGURAÇÕES TÉCNICAS

### Configurações Técnicas (REAL)
```bash
# .env - Baseado no config.py existente
TV_USERNAME=seu_usuario_tradingview
TV_PASSWORD=sua_senha_tradingview
NOTION_TOKEN=secret_token_notion
NOTION_DATABASE_ID=database_id_padrao
GOOGLE_APPLICATION_CREDENTIALS_JSON="{...}"
GOOGLE_CLOUD_PROJECT=projeto_gcp

# Novas APIs (serão adicionadas conforme necessário)
GLASSNODE_API_KEY=sua_chave_glassnode
COINGLASS_API_KEY=sua_chave_coinglass
AAVE_RPC_URL=https://ethereum-rpc.com
```

---

### Padrão de Response
```python
class IndicadorResponse(BaseModel):
    nome: str
    valor_bruto: Union[float, str]
    score: float
    classificacao: str
    timestamp: datetime
    fonte: str
    
class BlocoResponse(BaseModel):
    nome: str
    peso_percentual: float
    score_consolidado: float
    indicadores: List[IndicadorResponse]
    
class AnaliseResponse(BaseModel):
    timestamp: datetime
    score_final: float
    classificacao_geral: str
    kelly_allocation: str
    acao_recomendada: str
    alertas_ativos: List[str]
    blocos: List[BlocoResponse]
```


## 🚨 Alertas Importantes para Desenvolvedores

* **Não modifique** o padrão de resposta das APIs sem autorização.
* **Logs** são obrigatórios em erros críticos para facilitar depuração.


## 📁 **Nova Estrutura PostgreSQL**

```
app/services/utils/helpers/postgres/
├── __init__.py              # Facilita importações e exports
├── base.py                  # Conexão + execute_query genérica  
├── ciclo_helper.py         # 3 funções específicas do bloco ciclo
├── momentum_helper.py      # 3 funções específicas do bloco momentum
├── risco_helper.py         # 3 funções específicas do bloco risco
├── tecnico_helper.py       # 3 funções específicas do bloco técnico
├── utils.py                # Health check + diagnósticos gerais
└── dados_exemplo.py        # Dados realistas para desenvolvimento
```

### 🔧 **Funções Disponíveis por Bloco:**
- `get_dados_{bloco}()` - Busca dados mais recentes
- `insert_dados_{bloco}()` - Insere novos dados  
- `get_historico_{bloco}()` - Busca histórico com limite

---

## 📊 **Estrutura de Dados PostgreSQL**

### **Tabelas Criadas:**
```sql
-- Bloco Ciclo (MVRV Z-Score, Realized Price Ratio, Puell Multiple)
indicadores_ciclo (id, mvrv_z_score, realized_ratio, puell_multiple, timestamp, fonte, metadados)

-- Bloco Momentum (RSI, Funding Rates, OI Change, Long/Short Ratio)  
indicadores_momentum (id, rsi_semanal, funding_rates, oi_change, long_short_ratio, timestamp, fonte, metadados)

-- Bloco Risco (Liquidation Distance, Health Factor, Exchange Netflow, Stablecoin Ratio)
indicadores_risco (id, dist_liquidacao, health_factor, exchange_netflow, stablecoin_ratio, timestamp, fonte, metadados)

-- Bloco Técnico (Sistema EMAs, Padrões Gráficos)
indicadores_tecnico (id, sistema_emas, padroes_graficos, timestamp, fonte, metadados)
```

---

## 🔍 **Como Usar o Sistema de Diagnóstico**

### **1. Verificar Status Geral:**
```bash
GET /api/v1/diagnostico/health-check
```

**Resposta Esperada:**
```json
{
  "system_status": "✅ HEALTHY",
  "postgresql_connection": "✅ CONNECTED",
  "health_details": {
    "blocos": {
      "ciclo": {"total_records": 5, "status": "✅ OK"},
      "momentum": {"total_records": 5, "status": "✅ OK"}
    }
  }
}
```

### **2. Setup Inicial (Desenvolvimento):**
```bash
POST /api/v1/diagnostico/setup-database
```

### **3. Validar APIs:**
```bash
GET /api/v1/diagnostico/test-indicadores
```

---

## 🚨 **Padrões Estabelecidos**

### **Regra Arquitetural Memorizada:**
- 🔄 **SEMPRE** separar arquivos grandes por responsabilidade/bloco
- 💡 **SEMPRE** sugerir alternativas antes de implementar
- 📝 Arquivos pequenos = + entendimento, - erros, + reutilização

### **Tratamento de Erros:**
- Logs detalhados com contexto
- Fallbacks estruturados
- Never fail silently
- 3 cenários: Sucesso, Sem dados, Erro