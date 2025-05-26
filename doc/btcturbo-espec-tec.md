# BTC Turbo - Documentação Técnica Padrão
**Sistema BTC Hold Alavancado v3.0**

## 🎯 VISÃO GERAL DO SISTEMA

### Objetivo
Sistema modular de análise de indicadores BTC com score automatizado (0-10) e alocação Kelly para hold alavancado.

### Arquitetura Geral Atualizada
```
┌──────────────────┐    ┌──────────────────┐    ┌─────────────────────────┐
│     NOTION       │    │   APIs EXTERNAS  │    │      PostgreSQL         │
│ (dados brutos    │───▶│  (dados brutos   │───▶│   (dados brutos +       │
│  atualizados)    │    │   tempo real)    │    │    histórico completo)  │
│                  │    │                  │    │                         │
│ • tbl_ciclos     │    │ • Glassnode      │    │ • indicadores_ciclo     │
│ • tbl_momentum   │    │ • TradingView    │    │ • indicadores_momentum  │
│ • tbl_risco      │    │ • Coinglass      │    │ • indicadores_risco     │
│ • tbl_tecnico    │    │ • AAVE           │    │ • indicadores_tecnico   │
└──────────────────┘    └──────────────────┘    └─────────────────────────┘
                                                            │
                                                            ▼
                                                 ┌─────────────────────────┐
                                                 │    CAMADA CÁLCULO       │
                                                 │  (funções de score)     │
                                                 │                         │
                                                 │ • calcular_score_mvrv() │
                                                 │ • calcular_score_rsi()  │
                                                 │ • calcular_score_X()    │
                                                 └─────────────────────────┘
                                                            │
                                                            ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                           APIs FINAIS                                      │
│                     (retorna dados + scores)                              │
│                                                                            │
│ • /analise-btc      • /analise-ciclo     • /analise-momentum              │
│ • /analise-risco    • /analise-tecnico   • /alertas                       │
└────────────────────────────────────────────────────────────────────────────┘

                                    ▼ FUTURO ▼
                               ┌─────────────────┐
                               │   PostgreSQL    │
                               │ (scores +       │
                               │  histórico)     │
                               │                 │
                               │ • scores_ciclo  │
                               │ • scores_final  │
                               └─────────────────┘
```

### Fluxo de Dados Detalhado
1. **COLETA**: Notion (manual) + APIs (automático) → PostgreSQL
2. **VERIFICAÇÃO**: Função verifica se dados estão atualizados (< 8h)
3. **ATUALIZAÇÃO**: Se necessário, executa coleta específica por indicador
4. **CÁLCULO**: Funções leem PostgreSQL e calculam scores em tempo real
5. **RESPOSTA**: APIs retornam dados brutos + scores calculados
6. **FUTURO**: Scores também serão persistidos para análise histórica

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

## 🔄 FLUXO DE DADOS COMPLETO

### Arquitetura de Camadas
```
┌─────────────────────────────────────────┐
│           APIs FINAIS                   │
│    (/analise-btc, /analise-ciclo)      │
└─────────────────────────────────────────┘
                    ▲
┌─────────────────────────────────────────┐
│      FUNÇÕES DE CÁLCULO SCORE          │
│  (sempre consultam PostgreSQL)         │
└─────────────────────────────────────────┘
                    ▲
┌─────────────────────────────────────────┐
│           PostgreSQL                    │
│  (única fonte de dados + histórico)    │
└─────────────────────────────────────────┘
                    ▲
┌─────────────────────────────────────────┐
│     CAMADA DE COLETA VARIÁVEL           │
│  Notion + Glassnode + TradingView...    │
└─────────────────────────────────────────┘
```

### Princípios de Design
- **APIs estáveis**: Sempre consultam PostgreSQL
- **Flexibilidade**: Trocar fontes sem quebrar APIs
- **Histórico**: Dados temporais completos
- **Performance**: Cache natural no banco
- **Transparência**: APIs não sabem origem dos dados

## 🔄 FLUXO DE IMPLEMENTAÇÃO DETALHADO

### Etapa 1: Dados Manuais no Notion ✅
**Objetivo:** Criar base de dados históricos
- Tabela `tbl_ciclos` criada com campos: `Indicador`, `data_coleta`, `valor_coleta`, `fonte`
- Dados inseridos manualmente para indicadores do bloco Ciclo
- Notion como fonte de verdade para dados históricos

### Etapa 2: Integração Notion → PostgreSQL
**Objetivo:** Leitura automatizada e persistência
```python
# app/services/integracao/notion_collector.py

def collect_ciclo_data():
    """Coleta dados do Notion e salva no PostgreSQL"""
    notion = get_notion_client()
    database_id = settings.NOTION_DATABASE_ID
    
    # Busca todos os indicadores ativos
    results = notion.databases.query(database_id=database_id)
    
    for page in results["results"]:
        indicador = page["properties"]["Indicador"]["title"][0]["text"]["content"]
        valor = page["properties"]["valor_coleta"]["number"]
        data_coleta = page["properties"]["data_coleta"]["date"]["start"]
        fonte = page["properties"]["fonte"]["select"]["name"]
        
        # Salva no PostgreSQL
        save_to_postgres(indicador, {
            "valor": valor,
            "fonte": fonte,
            "timestamp": data_coleta
        })
```

### Etapa 3: Integração APIs Externas
**Objetivo:** Coleta automatizada de dados dinâmicos
```python
# app/services/integracao/glassnode_collector.py

def collect_glassnode_data():
    """Coleta dados do Glassnode para indicadores específicos"""
    api_key = get_glassnode_key()
    
    # MVRV Z-Score
    mvrv_data = requests.get(f"https://api.glassnode.com/v1/metrics/market/mvrv_z_score?a=BTC&api_key={api_key}")
    save_to_postgres("MVRV_Z", {
        "valor": mvrv_data.json()[-1]["v"],
        "fonte": "Glassnode"
    })
    
    # Realized Price
    realized_data = requests.get(f"https://api.glassnode.com/v1/metrics/market/price_realized_usd?a=BTC&api_key={api_key}")
    save_to_postgres("REALIZED_PRICE", {
        "valor": realized_data.json()[-1]["v"],
        "fonte": "Glassnode"
    })
```

### Etapa 4: Funções de Cálculo Reais
**Objetivo:** Substituir mocks por lógica real
```python
# Cada indicador implementa seu padrão específico
def calcular_score_mvrv():
    # 1. Verificar atualização
    if is_indicator_outdated("MVRV_Z"):
        update_mvrv_data()  # Função específica
    
    # 2. Buscar dados do PostgreSQL
    dados = get_dados_postgres("MVRV_Z")
    
    # 3. Calcular score
    score = aplicar_formula_mvrv(dados["valor"])
    
    return {"valor": dados["valor"], "score": score}
```

### Etapa 5: APIs de Dados Brutos
**Objetivo:** Endpoints para consulta individual
```python
# app/routers/dados_brutos.py

@router.get("/indicador/{nome}")
def get_indicador_bruto(nome: str):
    """Retorna dados brutos de um indicador específico"""
    dados = get_dados_postgres(nome)
    return {
        "nome": nome,
        "valor": dados["valor"],
        "fonte": dados["fonte"],
        "timestamp": dados["timestamp"]
    }
```

### Etapa 6: API de Atualização Forçada
**Objetivo:** Trigger manual via N8N
```python
# app/routers/atualizar.py

@router.post("/forcar-update/{indicador}")
def forcar_update_indicador(indicador: str):
    """Força atualização de um indicador específico"""
    if indicador == "MVRV_Z":
        update_mvrv_data()
    elif indicador == "REALIZED_RATIO":
        update_realized_data()
    # ... outros indicadores
    
    return {"status": "atualizado", "indicador": indicador}

@router.post("/forcar-update-todos")
def forcar_update_todos():
    """Força atualização de todos os indicadores"""
    # Executa update de todos os indicadores
    # Usado pelo N8N em schedule
    pass
```

### Etapa 7: APIs Finais Consolidadas
**Objetivo:** Score final + alertas + recomendações
- API `/analise-btc` - Já implementada, usar dados reais
- API `/analise-ciclo` - Já implementada, usar dados reais
- APIs dos outros blocos - Implementar seguindo padrão

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

### Padrão de Indicador Atualizado (ARQUITETURA FINAL)
```python
# app/services/ciclo/mvrv_z_score.py

from app.services.utils.postgres_helper import get_dados_postgres, save_dados_postgres
from app.services.integracao.glassnode_client import get_mvrv_from_glassnode
from datetime import datetime, timedelta
import logging

# CONFIGURAÇÃO ESPECÍFICA DO INDICADOR
INDICADOR = "MVRV_Z_SCORE"
UPDATE_THRESHOLD_HOURS = 24  # MVRV atualiza 1x por dia
ORIGEM = "Glassnode"         # Fonte de dados deste indicador

def data_update():
    """
    Função principal de atualização do indicador.
    FLUXO:
    1. Busca dados no PostgreSQL
    2. Verifica se estão atualizados (< threshold_hours)
    3. Se não, busca na origem configurada
    4. Salva no PostgreSQL e retorna dados
    """
    try:
        # 1. Busca dados existentes no PostgreSQL
        dados_existentes = get_dados_postgres(INDICADOR)
        
        # 2. Verifica se dados existem e estão atualizados
        if dados_existentes:
            last_update = dados_existentes["timestamp"]
            time_diff = datetime.utcnow() - last_update
            
            if time_diff.total_seconds() <= UPDATE_THRESHOLD_HOURS * 3600:
                logging.info(f"{INDICADOR}: Dados atualizados, usando cache PostgreSQL")
                return {
                    "valor": dados_existentes["valor"],
                    "timestamp": dados_existentes["timestamp"],
                    "fonte": dados_existentes["fonte"],
                    "cache": True
                }
        
        # 3. Dados não existem OU estão desatualizados - buscar na origem
        logging.info(f"{INDICADOR}: Buscando dados atualizados de {ORIGEM}")
        
        if ORIGEM == "Glassnode":
            dados_origem = get_mvrv_from_glassnode()
        elif ORIGEM == "Notion":
            dados_origem = get_mvrv_from_notion()
        else:
            raise ValueError(f"Origem {ORIGEM} não configurada para {INDICADOR}")
        
        # 4. Salva no PostgreSQL
        dados_para_salvar = {
            "indicador": INDICADOR,
            "valor": dados_origem["valor"],
            "fonte": ORIGEM,
            "timestamp": datetime.utcnow()
        }
        
        save_dados_postgres(dados_para_salvar)
        
        logging.info(f"{INDICADOR}: Dados atualizados de {ORIGEM} e salvos no PostgreSQL")
        
        return {
            "valor": dados_origem["valor"],
            "timestamp": dados_para_salvar["timestamp"],
            "fonte": ORIGEM,
            "cache": False
        }
        
    except Exception as e:
        logging.error(f"Erro ao atualizar {INDICADOR}: {str(e)}")
        # IMPORTANTE: NÃO retorna dados mock - propaga erro real
        raise e

def calcular_score_mvrv():
    """
    Função de cálculo que usa data_update() para dados sempre atualizados
    """
    try:
        dados = data_update()
        valor = dados["valor"]
        
        # Lógica de score específica do MVRV
        if valor < 0:
            score = 9.5
        elif valor < 2:
            score = 7.5
        elif valor < 4:
            score = 5.5
        elif valor < 6:
            score = 3.5
        else:
            score = 1.0
            
        return {
            "valor": valor,
            "score": score,
            "timestamp": dados["timestamp"],
            "fonte": dados["fonte"]
        }
        
    except Exception as e:
        logging.error(f"Erro ao calcular score {INDICADOR}: {str(e)}")
        # Propaga erro - não retorna dados fictícios
        raise e
```

### Padrão Realized Ratio (origem Notion)
```python
# app/services/ciclo/realized_ratio.py

INDICADOR = "REALIZED_RATIO"
UPDATE_THRESHOLD_HOURS = 8   # Realized atualiza 3x por dia
ORIGEM = "Notion"

def data_update():
    # Mesmo padrão, mas busca do Notion
    if ORIGEM == "Notion":
        dados_origem = get_realized_from_notion()
    # Resto igual ao padrão MVRV
```

### Padrão RSI Semanal (origem TradingView)
```python
# app/services/momentum/rsi_semanal.py

INDICADOR = "RSI_SEMANAL"
UPDATE_THRESHOLD_HOURS = 1   # RSI atualiza a cada hora
ORIGEM = "TradingView"

def data_update():
    # Mesmo padrão, mas busca do TradingView
    if ORIGEM == "TradingView":
        dados_origem = get_rsi_from_tradingview()
    # Resto igual ao padrão MVRV
```

### Configurações por Indicador
```python
# Períodos de atualização sugeridos por tipo:

# INDICADORES ON-CHAIN (lentos)
MVRV_UPDATE_HOURS = 24       # 1x por dia
REALIZED_UPDATE_HOURS = 24   # 1x por dia  
PUELL_UPDATE_HOURS = 12      # 2x por dia

# INDICADORES TÉCNICOS (médios)
RSI_UPDATE_HOURS = 2         # 12x por dia
EMA_UPDATE_HOURS = 1         # 24x por dia

# INDICADORES RÁPIDOS (tempo real)
FUNDING_UPDATE_HOURS = 0.5   # 48x por dia
HEALTH_FACTOR_UPDATE_HOURS = 0.25  # 96x por dia (crítico)
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

## 🗄️ ESTRUTURA DO BANCO DE DADOS (TABELA ÚNICA PARA TODOS INDICADORES)

### Tabela Principal: `indicadores`
```sql
CREATE TABLE indicadores (
    id SERIAL PRIMARY KEY,
    indicador VARCHAR(50) NOT NULL,          -- "MVRV_Z_SCORE", "RSI_SEMANAL", etc.
    valor DECIMAL(15,6) NOT NULL,            -- Valor bruto coletado
    fonte VARCHAR(50) NOT NULL,              -- "Notion", "Glassnode", "TradingView"
    timestamp TIMESTAMP DEFAULT NOW(),       -- Quando foi coletado
    metadados JSONB DEFAULT '{}',            -- Dados extras (configuração, contexto)
    
    -- Índices para performance
    INDEX idx_indicador_timestamp (indicador, timestamp DESC),
    INDEX idx_timestamp (timestamp DESC),
    INDEX idx_fonte (fonte)
);

-- Exemplos de dados
INSERT INTO indicadores (indicador, valor, fonte, timestamp) VALUES
('MVRV_Z_SCORE', 2.75, 'Glassnode', NOW()),
('REALIZED_RATIO', 46204, 'Notion', NOW()),
('PUELL_MULTIPLE', 1.44, 'Notion', NOW()),
('RSI_SEMANAL', 52.3, 'TradingView', NOW()),
('FUNDING_RATES', 0.015, 'Coinglass', NOW());
```

### Variáveis de Ambiente Necessárias
```bash
# PostgreSQL Connection
DB_HOST=localhost
DB_NAME=btc_turbo
DB_USER=postgres
DB_PASSWORD=sua_senha
DB_PORT=5432

# Ou usar DATABASE_URL única
DATABASE_URL=postgresql://user:password@host:port/database
```

### Configuração no config.py
```python
# app/config.py - ADICIONAR:

class Settings(BaseSettings):
    # ... outras configurações ...
    
    # PostgreSQL
    DB_HOST: str = Field(..., env="DB_HOST")
    DB_NAME: str = Field(..., env="DB_NAME") 
    DB_USER: str = Field(..., env="DB_USER")
    DB_PASSWORD: str = Field(..., env="DB_PASSWORD")
    DB_PORT: int = Field(5432, env="DB_PORT")
    
    # Ou conexão única
    DATABASE_URL: Optional[str] = Field(None, env="DATABASE_URL")
```

### ⚠️ OBRIGATÓRIO: Funções PostgreSQL Helper Atualizadas
**Arquivo:** `app/services/utils/postgres_helper.py`

```python
# NOVA ESTRUTURA - UMA TABELA GERAL POR INDICADOR

import logging
from datetime import datetime
from typing import Dict, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from app.config import get_settings

def get_db_connection():
    """Conecta com PostgreSQL usando configurações do .env"""
    settings = get_settings()
    return psycopg2.connect(
        host=settings.DB_HOST,
        database=settings.DB_NAME,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        cursor_factory=RealDictCursor
    )

def get_dados_postgres(indicador: str) -> Optional[Dict]:
    """
    Busca dados mais recentes de um indicador específico no PostgreSQL.
    
    Args:
        indicador: Nome do indicador (ex: "MVRV_Z_SCORE")
        
    Returns:
        Dict com dados do indicador ou None se não encontrado
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                query = """
                    SELECT indicador, valor, fonte, timestamp, metadados
                    FROM indicadores 
                    WHERE indicador = %s 
                    ORDER BY timestamp DESC 
                    LIMIT 1
                """
                cursor.execute(query, (indicador,))
                result = cursor.fetchone()
                
                if result:
                    return dict(result)
                return None
                
    except Exception as e:
        logging.error(f"Erro ao buscar {indicador} no PostgreSQL: {str(e)}")
        return None

def save_dados_postgres(dados: Dict) -> bool:
    """
    Salva dados de um indicador no PostgreSQL.
    
    Args:
        dados: Dict com chaves: indicador, valor, fonte, timestamp, metadados (opcional)
        
    Returns:
        True se sucesso, False se erro
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                query = """
                    INSERT INTO indicadores (indicador, valor, fonte, timestamp, metadados)
                    VALUES (%(indicador)s, %(valor)s, %(fonte)s, %(timestamp)s, %(metadados)s)
                """
                
                dados_para_insert = {
                    "indicador": dados["indicador"],
                    "valor": dados["valor"],
                    "fonte": dados["fonte"],
                    "timestamp": dados.get("timestamp", datetime.utcnow()),
                    "metadados": dados.get("metadados", {})
                }
                
                cursor.execute(query, dados_para_insert)
                conn.commit()
                
                logging.info(f"Dados salvos no PostgreSQL: {dados['indicador']}")
                return True
                
    except Exception as e:
        logging.error(f"Erro ao salvar dados no PostgreSQL: {str(e)}")
        return False

def is_indicator_outdated(indicador: str, threshold_hours: int = 8) -> bool:
    """
    Verifica se um indicador precisa ser atualizado.
    
    Args:
        indicador: Nome do indicador
        threshold_hours: Horas limite para considerar desatualizado
        
    Returns:
        True se precisa atualizar, False se ainda válido
    """
    try:
        dados = get_dados_postgres(indicador)
        
        if not dados:
            logging.info(f"{indicador}: Não encontrado no PostgreSQL, precisa atualizar")
            return True
        
        last_update = dados["timestamp"]
        time_diff = datetime.utcnow() - last_update
        is_outdated = time_diff.total_seconds() > threshold_hours * 3600
        
        if is_outdated:
            logging.info(f"{indicador}: Desatualizado há {time_diff.total_seconds()/3600:.1f}h")
        else:
            logging.info(f"{indicador}: Atualizado, ainda válido por {threshold_hours - time_diff.total_seconds()/3600:.1f}h")
            
        return is_outdated
        
    except Exception as e:
        logging.error(f"Erro ao verificar {indicador}: {str(e)}")
        return True  # Em caso de erro, força atualização

def get_all_indicators_status() -> Dict:
    """
    Retorna status de todos os indicadores do sistema.
    Útil para monitoramento e debugging.
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                query = """
                    SELECT 
                        indicador,
                        valor,
                        fonte,
                        timestamp,
                        EXTRACT(EPOCH FROM (NOW() - timestamp))/3600 as horas_desde_update
                    FROM indicadores 
                    WHERE timestamp = (
                        SELECT MAX(timestamp) 
                        FROM indicadores i2 
                        WHERE i2.indicador = indicadores.indicador
                    )
                    ORDER BY indicador
                """
                cursor.execute(query)
                results = cursor.fetchall()
                
                return {
                    "total_indicadores": len(results),
                    "indicadores": [dict(row) for row in results],
                    "timestamp_consulta": datetime.utcnow().isoformat()
                }
                
    except Exception as e:
        logging.error(f"Erro ao buscar status dos indicadores: {str(e)}")
        return {"erro": str(e)}
``` get_dados_momentum() -> Optional[Dict]: pass  
def is_momentum_outdated(hours: int = 8) -> bool: pass

def save_dados_risco(dados: Dict): pass
def get_dados_risco() -> Optional[Dict]: pass
def is_risco_outdated(hours: int = 8) -> bool: pass

def save_dados_tecnico(dados: Dict): pass
def get_dados_tecnico() -> Optional[Dict]: pass
def is_tecnico_outdated(hours: int = 8) -> bool: pass
```

### Tabelas Futuras para Scores (DESENVOLVIMENTO FUTURO)
```sql
-- Para armazenar histórico de scores calculados
CREATE TABLE scores_ciclo (
    id SERIAL PRIMARY KEY,
    mvrv_z_score_value DECIMAL(15,6),
    mvrv_z_score_score DECIMAL(3,1),
    realized_ratio_value DECIMAL(15,6),
    realized_ratio_score DECIMAL(3,1),
    puell_multiple_value DECIMAL(15,6),
    puell_multiple_score DECIMAL(3,1),
    score_bloco_final DECIMAL(3,1),
    timestamp TIMESTAMP DEFAULT NOW()
);

CREATE TABLE scores_consolidado (
    id SERIAL PRIMARY KEY,
    score_ciclo DECIMAL(3,1),
    score_momentum DECIMAL(3,1),
    score_risco DECIMAL(3,1),
    score_tecnico DECIMAL(3,1),
    score_final DECIMAL(3,1),
    score_ajustado DECIMAL(3,1),
    kelly_allocation VARCHAR(10),
    classificacao VARCHAR(20),
    timestamp TIMESTAMP DEFAULT NOW()
);

-- NOTA: Implementar em versão futura para análise histórica de performance
```

## 📋 CHECKLIST OBRIGATÓRIO PARA DESENVOLVEDOR

### ✅ Antes de Implementar Qualquer Nova Funcionalidade

**1. Estrutura de Arquivos Obrigatória:**
```
app/services/utils/postgres_helper.py  ← SEMPRE CRIAR PRIMEIRO
app/services/integracao/               ← Pasta para clients externos
app/schemas/response_model.py         ← Atualizar se novos campos
```

**2. Dependências Obrigatórias no main.py:**
```python
# PADRÃO OBRIGATÓRIO - Sempre verificar imports
from app.routers import analise_btc, analise_ciclo, nome_do_arquivo

# PADRÃO OBRIGATÓRIO - Router deve coincidir com import
app.include_router(nome_do_arquivo.router, prefix="/prefixo")
```

**3. Testes de Integração:**
- [ ] Endpoint `/debug/test-config` funcionando
- [ ] Endpoint específico de teste criado
- [ ] Swagger `/docs` mostrando todas as rotas
- [ ] Logs aparecendo no console

### ⚠️ ERROS COMUNS E SOLUÇÕES

| Erro | Causa | Solução |
|------|-------|---------|
| `No module named 'app.services.utils.postgres_helper'` | Arquivo não criado | Criar arquivo com funções mock |
| `ImportError: cannot import name 'router'` | Erro no import do main.py | Verificar nome correto do arquivo |
| `"detail": "Not Found"` | Rota não registrada | Verificar router no main.py |
| `AttributeError: module has no attribute` | Função não existe | Implementar função no arquivo |

### 🛠️ TEMPLATE PARA NOVOS INDICADORES (ARQUITETURA FINAL)

**Passo 1: Criar arquivo do indicador**
```python
# app/services/ciclo/mvrv_z_score.py

from app.services.utils.postgres_helper import get_dados_postgres, save_dados_postgres, is_indicator_outdated
from app.services.integracao.glassnode_client import get_mvrv_data
from datetime import datetime
import logging

# CONFIGURAÇÃO DO INDICADOR
INDICADOR = "MVRV_Z_SCORE"
UPDATE_THRESHOLD_HOURS = 24  # Atualiza 1x por dia
ORIGEM = "Glassnode"

def data_update():
    """Função obrigatória para todos os indicadores"""
    try:
        # 1. Verifica se dados estão atualizados
        if not is_indicator_outdated(INDICADOR, UPDATE_THRESHOLD_HOURS):
            dados_existentes = get_dados_postgres(INDICADOR)
            logging.info(f"{INDICADOR}: Usando dados do cache PostgreSQL")
            return dados_existentes
        
        # 2. Busca dados da origem
        logging.info(f"{INDICADOR}: Buscando dados atualizados de {ORIGEM}")
        
        if ORIGEM == "Glassnode":
            dados_origem = get_mvrv_data()
        elif ORIGEM == "Notion":
            dados_origem = get_mvrv_from_notion()
        else:
            raise ValueError(f"Origem {ORIGEM} não configurada")
        
        # 3. Salva no PostgreSQL
        dados_para_salvar = {
            "indicador": INDICADOR,
            "valor": dados_origem["valor"],
            "fonte": ORIGEM,
            "timestamp": datetime.utcnow(),
            "metadados": {"raw_data": dados_origem}
        }
        
        if save_dados_postgres(dados_para_salvar):
            logging.info(f"{INDICADOR}: Dados atualizados e salvos")
            return dados_para_salvar
        else:
            raise Exception("Falha ao salvar no PostgreSQL")
            
    except Exception as e:
        logging.error(f"Erro ao atualizar {INDICADOR}: {str(e)}")
        raise e  # NÃO retorna mock - propaga erro real

def calcular_score_mvrv():
    """Função de cálculo que usa data_update()"""
    try:
        dados = data_update()
        valor = dados["valor"]
        
        # Lógica específica de score para MVRV
        if valor < 0:
            score = 9.5
        elif valor < 2:
            score = 7.5
        elif valor < 4:
            score = 5.5
        elif valor < 6:
            score = 3.5
        else:
            score = 1.0
            
        return {
            "valor": valor,
            "score": score,
            "timestamp": dados["timestamp"],
            "fonte": dados["fonte"]
        }
        
    except Exception as e:
        logging.error(f"Erro ao calcular score {INDICADOR}: {str(e)}")
        raise e
```

**Passo 2: Registrar no endpoint de update**
```python
# app/routers/atualizar.py - ADICIONAR:

indicadores = [
    ("app.services.ciclo.mvrv_z_score", "data_update"),
    ("app.services.ciclo.realized_ratio", "data_update"),
    ("app.services.ciclo.puell_multiple", "data_update"),
    
    # ADICIONAR NOVOS INDICADORES AQUI:
    # ("app.services.momentum.rsi_semanal", "data_update"),
    # ("app.services.momentum.funding_rates", "data_update"),
]
```

**Passo 3: Criar cliente de integração (se necessário)**
```python
# app/services/integracao/glassnode_client.py

import requests
from app.config import get_settings

def get_mvrv_data():
    """Busca MVRV Z-Score do Glassnode"""
    settings = get_settings()
    api_key = settings.GLASSNODE_API_KEY
    
    url = f"https://api.glassnode.com/v1/metrics/market/mvrv_z_score"
    params = {"a": "BTC", "api_key": api_key}
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    
    data = response.json()
    latest = data[-1]  # Último valor
    
    return {
        "valor": latest["v"],
        "timestamp": latest["t"],
        "raw_response": data
    }
```

**Passo 4: Criar teste específico**
```python
# app/routers/test_indicadores.py

@router.get("/test-mvrv", tags=["Debug"])
def test_mvrv():
    try:
        from app.services.ciclo.mvrv_z_score import data_update
        resultado = data_update()
        return {"status": "sucesso", "dados": resultado}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## 🚀 CRONOGRAMA ATUALIZADO COM CHECKLIST

| Etapa | Duração | Arquivos Obrigatórios | Checklist de Validação |
|-------|---------|----------------------|------------------------|
| **1** | 1 dia | Notion estruturado | ✅ Tabela criada ✅ Dados inseridos |
| **2** | 2 dias | `postgres_helper.py`<br>`notion_reader.py`<br>`test_endpoint.py` | ✅ `/debug/test-config` OK<br>✅ `/debug/test-notion` OK<br>✅ Dados lidos sem erro |
| **3** | 3 dias | Clientes APIs externas<br>Funções de coleta | ✅ 1 API externa funcionando<br>✅ Rate limiting implementado |
| **4** | 1 dia | Conexão PostgreSQL real<br>Modelos SQLAlchemy | ✅ Insert funcionando<br>✅ Select funcionando |
| **5** | 4 dias | Funções de cálculo<br>Lógicas de score | ✅ 1 indicador calculando real<br>✅ Score entre 0-10 |
| **6** | 2 dias | Endpoints dados brutos | ✅ JSON padrão retornando<br>✅ Swagger atualizado |
| **7** | 1 dia | API atualização<br>Integração N8N | ✅ Force update funcionando<br>✅ Logs estruturados |
| **8** | 2 dias | APIs finais consolidadas | ✅ Score final calculado<br>✅ Alertas funcionando |

### 🔥 REGRA OBRIGATÓRIA: "NÃO PASSE PARA PRÓXIMA ETAPA SEM VALIDAR A ANTERIOR"

**Cada etapa deve ter:**
1. ✅ **Código funcionando** - sem erros de import/execução
2. ✅ **Teste automatizado** - endpoint `/debug/test-X` OK
3. ✅ **Documentação atualizada** - arquivos e padrões claros
4. ✅ **Commit realizado** - código versionado e seguro

### 📞 COMUNICAÇÃO COM ANALISTA

**Ao finalizar cada etapa, reportar:**
```
✅ ETAPA X CONCLUÍDA
- Arquivos criados: [lista]
- Testes passando: [URLs]
- Problemas encontrados: [descrição]
- Próxima etapa: [confirmação]
```

**Se encontrar problema:**
```
❌ PROBLEMA NA ETAPA X
- Erro específico: [descrição]
- Tentativas feitas: [lista]
- Preciso de: [ajuda específica]
```

## 🎯 PRÓXIMOS PASSOS

1. **Validar** esta documentação padrão
2. **Definir** quais indicadores começar na Etapa 1
3. **Gerar** documentação específica da primeira etapa
4. **Implementar** seguindo os padrões estabelecidos

---
*Versão: 1.0 | Data: 26/05/2025 | Projeto: BTC Turbo*