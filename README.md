# BTC Turbo - Documentação Técnica Padrão
**Sistema BTC Hold Alavancado v3.0**

## 🎯 VISÃO GERAL DO SISTEMA

### Objetivo
Sistema modular de análise de indicadores BTC com score automatizado (0-10) e alocação Kelly para hold alavancado.

### Arquitetura Geral
```
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│   Notion API    │───▶│  PostgreSQL  │───▶│   APIs Finais   │
│ (Dados Manuais) │    │   (Cache)    │    │ (Score + Alertas)│
└─────────────────┘    └──────────────┘    └─────────────────┘
         │                       ▲                     ▲
         ▼                       │                     │
┌─────────────────┐              │              ┌─────────────┐
│ APIs Externas   │──────────────┘              │   N8N       │
│(TradingView,etc)│                             │(Scheduler)  │
└─────────────────┘                             └─────────────┘
```

## 📋 ESTRUTURA REAL VALIDADA

**Projeto atual:** Sistema funcional com dados mockados
**Arquitetura:** FastAPI + TradingView + Notion + PostgreSQL (futuro)
**Status:** Bloco Ciclo implementado, outros blocos pendentes
**Deploy:** Railway com Docker

### Blocos Principais
| Bloco | Peso | Componentes |
|-------|------|-------------|
| **Ciclo** | 40% | MVRV Z-Score (20%), Realized Price (15%), Puell (5%) |
| **Momentum** | 25% | RSI Semanal (10%), Funding (8%), OI Change (4%), L/S Ratio (3%) |
| **Risco** | 15% | Dist. Liquidação (6%), Health Factor (4%), Netflow (3%), Stablecoin (2%) |
| **Técnico** | 20% | Sistema EMAs (15%), Padrões Gráficos (5%) |

### Classificação Final
| Score | Classe | Kelly % | Ação |
|-------|--------|---------|------|
| 0-2 | Crítico | 0% | Zerar alavancagem |
| 2-4 | Ruim | 10% | Posição mínima |
| 4-6 | Neutro | 25% | Conservador |
| 6-8 | Bom | 50% | Moderado |
| 8-10 | Ótimo | 75% | Agressivo |

## 🔄 FLUXO DE IMPLEMENTAÇÃO

### Etapa 1: Dados Manuais no Notion
**Objetivo:** Base de dados históricos e indicadores estáticos
- Criação de tabelas estruturadas no Notion
- Inserção manual de dados históricos críticos
- Padronização de campos e formatos

### Etapa 2: Integração Notion → Sistema
**Objetivo:** Coleta automatizada dos dados do Notion
- Função genérica para leitura do Notion
- Mapeamento de campos para modelos internos
- Cache local para otimização

### Etapa 3: Integração APIs Externas
**Objetivo:** Coleta de dados em tempo real
- Clientes para cada API (TradingView, Glassnode, etc.)
- Tratamento de erros e fallbacks
- Rate limiting e retry automático

### Etapa 4: Persistência no Banco
**Objetivo:** Armazenamento estruturado no PostgreSQL
- Modelos SQLAlchemy para cada indicador
- Histórico temporal dos dados
- Índices para performance

### Etapa 5: Cálculo dos Indicadores
**Objetivo:** Processamento dos dados brutos
- Funções de cálculo por indicador
- Aplicação dos pesos e normalizações
- Score parcial por bloco

### Etapa 6: APIs de Dados Brutos
**Objetivo:** Acesso aos indicadores individuais
- Endpoints para cada indicador
- Formato padronizado de resposta
- Filtros temporais

### Etapa 7: APIs de Atualização
**Objetivo:** Trigger manual via N8N
- Endpoint `/atualizar` para refresh completo
- Jobs assíncronos para cada bloco
- Status de processamento

### Etapa 8: APIs Finais
**Objetivo:** Score consolidado e alertas
- Endpoint principal `/analise-btc`
- Score por bloco individual
- Sistema de alertas em tempo real

## 🏗️ PADRÕES DE DESENVOLVIMENTO

### Estrutura de Arquivos (REAL)
```
app/
├── main.py                  # Entrada FastAPI
├── config.py                # Configurações via BaseSettings
├── dependencies.py          # Clientes de APIs externas
├── db/                      # Conexão PostgreSQL
│   └── database.py
├── models/                  # ORM SQLAlchemy
│   └── indicators.py
├── schemas/                 # Pydantic response models
│   └── response_model.py
├── routers/                 # Endpoints da API
│   ├── analise_btc.py       # API principal consolidada
│   ├── analise_ciclo.py     # API bloco ciclo
│   └── atualizar.py         # API atualização
└── services/                # Lógica de negócio
    ├── blocos/              # Consolidação por bloco
    │   └── ciclo.py         # Agrega indicadores do ciclo
    ├── ciclo/               # Indicadores do bloco CICLO
    │   ├── mvrv_z_score.py
    │   ├── puell_multiple.py
    │   └── realized_ratio.py
    ├── momentum/            # Indicadores do bloco MOMENTUM
    │   ├── rsi_semanal.py
    │   ├── funding_rates.py
    │   ├── oi_change.py
    │   └── long_short_ratio.py
    ├── risco/               # Indicadores do bloco RISCO
    │   ├── dist_liquidacao.py
    │   ├── health_factor.py
    │   ├── exchange_netflow.py
    │   └── stablecoin_ratio.py
    ├── tecnico/             # Indicadores do bloco TÉCNICO
    │   ├── sistema_emas.py
    │   └── padroes_graficos.py
    └── utils/               # Helpers internos
        └── indicadores_helper.py
```

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

## 📋 PADRÕES DE SAÍDA JSON (REAL)
1. API /analise-ciclo - Formato Bloco
json{
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

--- 

2. API /analise-btc - Formato Principal
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