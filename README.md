# BTC TURBO - v1.0.25

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

## 1.0.12 - redistribuir pesos - bloco momentum  - feito
- alterar api obter-indicadores, calcular-score - analise-btc
- helpers momentum
- alterar dash momentum
- revisar dash consolidados para avaliar impacto

´´´
├── MOMENTUM (30%)
├── RSI Semanal (12%) ← +2%
├── Funding Rates (10%) ← +2%
├── Exchange Netflow 7D (5%) ← NOVO
└── Long/Short Ratio (3%) ← Mantém

´´´
---

## 1.0.13 -  Com ou sem risco no score final - Feito
- incluido flag para considerar ou não o risco no score final
- alterado o dash incluido paramentro para setar ou não o score com risco

---

## 1.0.14 -  Gravar score consolidado na base - Um registro por dia -feito
- gravar score na base se ainda não foi gravado para o dia
- buscar dados no cache do banco primeiro, se não existir busca nas APIs
- opção de forçar atualização (neste caso busca das APIs)

---

## 1.0.15 -  coleta de dados - bloco risco - feito

- alterar tabela indicsores_risco incluir novos campos campos
- calcular HF e Dist. pra liquidação

## 1.0.16 / 17 -  coleta de dados - ciclos - MVRV - feito (precisa de ajustes)

- coleta e MVRV

## 1.0.18 -  Fix - problema no forçar update do dash principal - feito - 01/06

- Botão atualizar não estava funcionando, estava sempre usando o cach

## 1.0.19 -  Coletar dados EMAs e calcular alinhamento e posição do preço - feito - 01/06

- Estavamos usando API externa para calcular o score e classificação
- rotina diferente dos demais blocos porque precisa calcular internamente o indicador, não existe no mercado

- coleta-indicadores{tecnico}
- obter-indicadores{tecnico}
- calcular-score{tecnico}
- helpers - postgres

## Ajustar o dash

### 1.0.20 - Bloco analise tecnica - feito - 02/06
- usar api interna desenvolvida na versão 1.0.19 - obter-indicadore{tenico}
- incluir link nos gráficos para mostrar o detalhe (posição das emas,alertas, e dados relevantes)
- mostrar a versão atual do sistema de forma dinamica (discreto)

### 1.0.21 - Bloco geral (home) - feito -02/06
- usar novos pesos (tecnico 50% - ciclo 30% - momentum - 20%)
- não iremos mais considerar o risco no score final (vamos aplicar um redutor do score geral conforme o risco)
- teremos um botão para ver o score com a redução do risco ou sem a redução
- Ainda iremos definir o percentual a ser reduzido do score com base no risco 
- continuar mostrando o bloco risco para referêicia
- mostrar a versão atual do sistema de forma dinamica (discreto)

### 1.0.22  - Importar indicadores do Notion (ciclos e momentum) - Feito - 03/06
- Os indicadores são coletados manualmente e gravados no Notion
- o sistema importa esses dados /coletar-indicadores/{bloco}

### 1.0.23 - Refatorar dash (html) principal e analise.py - arquivo está muito grande - feito - 03/06
- decompor em arquivos menores - um para cada tarefa específica
- está complicado para dar manutenção
- refatorar o arquivo analise.py simplificar o json de saida
- entender como está o funcionamento completo do dashboard e organizar

### 1.0.24 - Otimizar o refactore do dashboar - feito 04/06
/docs/dashboard-espec.md
- simplificação, otimização, modularização, estrutura mais fácil de dar manutenção

### 1.0.25 -  Página de detalhes da analise ténica - FEITO 04/06
- criar a págida de detalhes da analise tecnica 
- incluir os alertas exclusivos deste bloco (alertas na página detalhe)

### 1.0.26 - Ajuste dinamico de pesos no score
- ajustes de riscos
- ajustes de volatilidade
- ajuste regime de mercado

### 1.0.26 - sistema de alertas na home dash

- alertas de oportunidades
- incluir a versão de forma dinamica pegando do main ou variável de config em todos as página do dash (hoje está estática)
- corrigir valor no indicador Exchange Netflow do bloco momentum -  4 casas decimais ou K ao final do numero inteiro (milhares de BTCs)
- unificar com alertas da analise tecnica que está na página de detalhes
- validar/revisar alertas da analise tecnica da distancia do preço em relação as médias
- criar um router/service unificado de todosos alertas
- consumir esse endpoint na automação do sistema de alertas e na página prinicpal do dassh e blocos 

### 1.0.27 - Criar outro indicador de risco (Alavancagem atual X alavancagem permitida Kelly)
- escala para aderencia, quanto mais aderente ao Kelly, maior pontuação
- definir peso em relação aos outros existentes

### 1.0.28 - Criar sistema de penalidade do score com base no score de risco
- o risco, sempre pode retirar pontos do score geral, nunca acrescentar
- definir critérios objetivos - consultar especialista analise BTC

## 1.0.29 - criar histórico ( scores blocos, consolidado e indicadores bruto)
- consutar especialista Analise BTC, se agrega ou não na tomada de decisão

### 1.0.29 - Criar dash com graficos de linhas para monitorar disciplina no Risco e evolução financeira
- Health factore
- Distancia para liuquidação (percentual)
- Alavancagem
- Crescimento de BTC na carteira (saldo liq. em dolares X preço atual do BTC)
- o objetivo primcipal do Hold alavancado é aumentar a qtd de BTC em carteira

## Incluir outros indicadoes de anlise tecnica alem das EMAs
- definir indcadores e price action

##  coleta indicadores dinamico (ciclos e momentum)
- buscar dados publicos, necessários para as formulas e calcular no sistema
- não usar APIs pagas

## - histórico dos indicadores dados bruto

## - histórico dos scores geral e score dos blocos

- Docs: 
https://github.com/Lindualdo/btcturbo/blob/main/doc/validation-limites-indicadores.md


- validação dos valores coletados
- coleta dos indicadores e gravação no Postgres
- registrar a fonte de cada indicador (hoje está uma fonte para todo o bloco) 
* notion
* Trandview
* web3
* APIs

##  coleta de indicadores  - momentum

---



## alertas
- implementar sistemas de alertas
https://github.com/Lindualdo/btcturbo/blob/main/doc/btcturbo-alertas.espc.md

---

## excluir indicadores descontinuados da tabela de riscos 
- exchange_netflow
- stablecoin_ratio
- ajustar no Helper e demais funções


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
{
    "timestamp": "2025-06-02T21:08:16.929740",
    "versao": "1.0.20",
    "configuracao": {
        "incluir_risco": true,
        "risco_disponivel": true,
        "blocos_no_calculo": 3,
        "fonte": "fresh_calculation",
        "force_update": true,
        "novos_pesos": "Técnico 50% | Ciclo 30% | Momentum 20% | Risco como redutor",
        "nota_risco": "Redução por risco PREPARADA mas temporariamente desabilitada (redutor = 1.0)"
    },
    "score_base": 6.18,
    "score_final": 6.18,
    "score_ajustado": 6.18,
    "redutor_risco": 1.0,
    "modificador_volatilidade": 1.0,
    "classificacao_geral": "bom",
    "kelly_allocation": "50%",
    "acao_recomendada": "Manter posição - condições favoráveis",
    "alertas_ativos": [
        "PERIGO: Liquidação próxima (Health Factor < 1.15)",
        "EUFORIA: Funding Rate acima de 0.1%, considerar redução",
        "Mudança de tendência principal detectada (preço cruzou EMA200)",
        "Volatilidade extremamente elevada"
    ],
    "pesos_dinamicos": {
        "tecnico": 0.5,
        "ciclo": 0.3,
        "momentum": 0.2,
        "risco": 0.0
    },
    "blocos": {
        "tecnico": {
            "bloco": "tecnico",
            "peso_bloco": "20%",
            "score_consolidado": 7.54,
            "classificacao_consolidada": "Correção Saudável",
            "timestamp": "2025-06-02T15:38:03.921570",
            "metodo": "emas_multitimeframe",
            "timeframes": {
                "semanal": {
                    "peso": "70%",
                    "score_total": 7.5,
                    "alinhamento": 10.0,
                    "posicao": 5.0,
                    "emas": {
                        "17": 96228.19,
                        "34": 89902.48,
                        "144": 61668.52,
                        "305": 44519.41,
                        "610": 30072.6
                    }
                },
                "diario": {
                    "peso": "30%",
                    "score_total": 7.65,
                    "alinhamento": 10.0,
                    "posicao": 5.3,
                    "emas": {
                        "17": 105603.4,
                        "34": 102856.01,
                        "144": 93818.41,
                        "305": 85570.88,
                        "610": 72556.64
                    }
                }
            },
            "indicadores": {
                "Sistema_EMAs_Multitimeframe": {
                    "valor": "Correção Saudável",
                    "score": 7.5,
                    "classificacao": "Correção Saudável",
                    "peso": "20%",
                    "fonte": "tvdatafeed_emas",
                    "ponderacao": "70% semanal + 30% diário"
                },
                "Padroes_Graficos": {
                    "valor": "Descontinuado",
                    "score": 0.0,
                    "classificacao": "N/A",
                    "peso": "0%",
                    "fonte": "tvdatafeed_emas",
                    "observacao": "Peso zerado - foco em EMAs"
                }
            },
            "distancias": {
                "daily": {
                    "ema_17": "-1.28%",
                    "ema_34": "+1.35%",
                    "ema_144": "+11.12%",
                    "ema_305": "+21.83%",
                    "ema_610": "+43.68%"
                },
                "weekly": {
                    "ema_17": "+8.34%",
                    "ema_34": "+15.96%",
                    "ema_144": "+69.05%",
                    "ema_305": "+134.17%",
                    "ema_610": "+246.66%"
                },
                "weights": {
                    "daily": 0.3,
                    "weekly": 0.7
                }
            },
            "alertas": [],
            "status": "success"
        },
        "ciclos": {
            "bloco": "ciclo",
            "peso_bloco": "40%",
            "score_consolidado": 4.75,
            "classificacao_consolidada": "neutro",
            "timestamp": "2025-06-02T11:00:34.834000",
            "indicadores": {
                "MVRV_Z": {
                    "valor": 2.5572,
                    "score": 5.5,
                    "classificacao": "neutro",
                    "peso": "20%",
                    "fonte": "Glassnode"
                },
                "Realized_Ratio": {
                    "valor": 2.2639,
                    "score": 3.5,
                    "classificacao": "ruim",
                    "peso": "15%",
                    "fonte": "Glassnode"
                },
                "Puell_Multiple": {
                    "valor": 1.1778,
                    "score": 5.5,
                    "classificacao": "neutro",
                    "peso": "5%",
                    "fonte": "Glassnode"
                }
            },
            "status": "success"
        },
        "momentum": {
            "bloco": "momentum",
            "peso_bloco": "30%",
            "score_consolidado": 4.9,
            "classificacao_consolidada": "neutro",
            "timestamp": "2025-06-02T16:00:07.739000",
            "indicadores": {
                "RSI_Semanal": {
                    "valor": 61.61,
                    "score": 3.5,
                    "classificacao": "ruim",
                    "peso": "12%",
                    "fonte": "Glassnode"
                },
                "Funding_Rates": {
                    "valor": "0.050%",
                    "score": 5.5,
                    "classificacao": "neutro",
                    "peso": "10%",
                    "fonte": "Glassnode"
                },
                "Exchange_Netflow": {
                    "valor": -2922.0,
                    "score": 5.5,
                    "classificacao": "neutro",
                    "peso": "5%",
                    "fonte": "Glassnode"
                },
                "Long_Short_Ratio": {
                    "valor": 0.9478,
                    "score": 7.5,
                    "classificacao": "bom",
                    "peso": "3%",
                    "fonte": "Glassnode"
                }
            },
            "status": "success"
        },
        "riscos": {
            "bloco": "riscos",
            "peso_bloco": "10%",
            "score_consolidado": 9.5,
            "classificacao_consolidada": "ótimo",
            "timestamp": "2025-06-02T20:00:51.248851",
            "indicadores": {
                "Dist_Liquidacao": {
                    "valor": "58.6%",
                    "score": 9.5,
                    "classificacao": "ótimo",
                    "peso": "5%",
                    "fonte": "aave/web3"
                },
                "Health_Factor": {
                    "valor": 2.413361,
                    "score": 9.5,
                    "classificacao": "ótimo",
                    "peso": "5%",
                    "fonte": "aave/web3"
                }
            },
            "status": "success"
        }
    },
    "resumo_blocos": {
        "tecnico": {
            "score_consolidado": 7.54,
            "classificacao": "Correção Saudável",
            "peso": "50.0%",
            "status": "success",
            "incluido_no_calculo": true
        },
        "ciclos": {
            "score_consolidado": 4.75,
            "classificacao": "neutro",
            "peso": "30.0%",
            "status": "success",
            "incluido_no_calculo": true
        },
        "momentum": {
            "score_consolidado": 4.9,
            "classificacao": "neutro",
            "peso": "20.0%",
            "status": "success",
            "incluido_no_calculo": true
        },
        "riscos": {
            "score_consolidado": 9.5,
            "classificacao": "ótimo",
            "peso": "0% (redutor)",
            "status": "success",
            "incluido_no_calculo": false,
            "funcao": "Redutor do score base (temporariamente desabilitado)"
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

´´´
json

{
    "bloco": "Financeiro Direto",
    "score_consolidado": 6.6,
    "peso": 0.35,
    "principais_alertas": [
        "HF crítico: 1.25"
    ],
    "financial_overview": {
        "collateral": 397163.25743252,
        "debt": 247299.03437482,
        "nav": 149864.2230577
    },
    "detalhes": {
        "health_factor": {
            "valor": 1.25,
            "classificacao": "Elevado",
            "score": 7.0,
            "peso": 0.8
        },
        "alavancagem": {
            "valor": 2.65,
            "classificacao": "Moderada",
            "score": 5.0,
            "peso": 0.2
        }
    }
}