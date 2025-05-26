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

### Padrão de Indicador (REAL - Baseado no MVRV existente)
```python
# app/services/ciclo/mvrv_z_score.py

from app.services.utils.indicadores_helper import is_indicator_outdated, force_update_indicator

INDICADOR = "MVRV_Z"

def get_dado_mvrv():
    """
    Retorna dados do indicador com verificação de atualização.
    Se desatualizado (>8h), força update automático.
    """
    if is_indicator_outdated(INDICADOR):
        return force_update_indicator(INDICADOR)
    
    # Retorno do banco/cache atual
    return {
        "nome": INDICADOR,
        "valor": 2.1,
        "score": 6.0,
        "last_update": "2025-05-26T12:00:00Z"
    }

def calcular_score_mvrv():
    """
    Wrapper para uso nos blocos.
    Retorna formato padronizado {"valor": x, "score": y}
    """
    dado = get_dado_mvrv()
    return {
        "valor": dado["valor"],
        "score": dado["score"]
    }
```

## 📋 PADRÕES DE SAÍDA JSON (REAL)

### 1. API `/analise-ciclo` - Formato Bloco
```json
{
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

### 2. API `/analise-btc` - Formato Principal
```json
{
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

### 3. Schemas Pydantic (Para Implementar)
```python
# app/schemas/response_model.py

class IndicadorResponse(BaseModel):
    valor: Union[float, str]
    score: float

class BlocoResponse(BaseModel):
    score: float
    indicadores: Dict[str, IndicadorResponse]

class AnaliseBTCResponse(BaseModel):
    timestamp: datetime
    score_final: float
    score_ajustado: float
    modificador_volatilidade: float
    classificacao_geral: str
    kelly_allocation: str
    acao_recomendada: str
    alertas_ativos: List[str]
    pesos_dinamicos: Dict[str, float]
    blocos: Dict[str, BlocoResponse]
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

### Banco de Dados
```sql
-- Tabela base para indicadores
CREATE TABLE indicadores (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(50) NOT NULL,
    valor_bruto DECIMAL,
    score DECIMAL(3,1),
    classificacao VARCHAR(20),
    timestamp TIMESTAMP DEFAULT NOW(),
    fonte VARCHAR(50),
    metadados JSONB
);

-- Tabela para scores consolidados
CREATE TABLE analises (
    id SERIAL PRIMARY KEY,
    score_final DECIMAL(3,1),
    classificacao VARCHAR(20),
    kelly_allocation VARCHAR(10),
    alertas JSONB,
    timestamp TIMESTAMP DEFAULT NOW()
);
```

## 📋 CHECKLIST DE VALIDAÇÃO

### Por Etapa
- [ ] **Etapa 1:** Notion estruturado com dados de teste
- [ ] **Etapa 2:** Leitura automatizada do Notion funcionando
- [ ] **Etapa 3:** Pelo menos 1 API externa integrada
- [ ] **Etapa 4:** Dados sendo persistidos corretamente
- [ ] **Etapa 5:** Cálculo de 1 indicador completo
- [ ] **Etapa 6:** Endpoint de dados brutos funcionando
- [ ] **Etapa 7:** Endpoint de atualização operacional
- [ ] **Etapa 8:** API final retornando score válido

### Critérios de Qualidade
- [ ] Código seguindo padrões do projeto
- [ ] Tratamento de erros implementado
- [ ] Logs estruturados para debugging
- [ ] Testes unitários básicos
- [ ] Documentação inline atualizada

## 🚀 CRONOGRAMA SUGERIDO

| Etapa | Duração | Dependência | Entregável |
|-------|---------|-------------|------------|
| 1 | 1 dia | - | Notion estruturado |
| 2 | 2 dias | Etapa 1 | Integração Notion |
| 3 | 3 dias | Etapa 2 | APIs externas |
| 4 | 1 dia | Etapa 3 | Persistência BD |
| 5 | 4 dias | Etapa 4 | Cálculos core |
| 6 | 2 dias | Etapa 5 | APIs dados brutos |
| 7 | 1 dia | Etapa 6 | API atualização |
| 8 | 2 dias | Etapa 7 | APIs finais |

**Total:** ~16 dias de desenvolvimento

## 🎯 PRÓXIMOS PASSOS

1. **Validar** esta documentação padrão
2. **Definir** quais indicadores começar na Etapa 1
3. **Gerar** documentação específica da primeira etapa
4. **Implementar** seguindo os padrões estabelecidos

---
*Versão: 1.0 | Data: 26/05/2025 | Projeto: BTC Turbo*