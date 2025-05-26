# 📋 Documentação Técnica - Arquitetura BTC Turbo API

## 🎯 Visão Macro da Arquitetura

### Fluxo Principal
```
📊 analise-btc (API Principal)
    ↓ consome
├── 🔄 analise-ciclos    (Score Ponderado)
├── ⚠️ analise-riscos    (Score Ponderado) 
├── 📈 analise-tecnica   (Score Ponderado)
└── ⚡ analise-momentum  (Score Ponderado)
    ↓ todas consomem
📥 obter-indicadores (Dados Brutos + Cache)
    ↓ coleta de
🌐 Fontes Externas (APIs, Notion, TradingView, etc.)
```

## 🏗️ Arquitetura em Camadas

### **Camada 1: Consolidação (analise-btc)**
- **Responsabilidade**: Score final ponderado
- **Input**: Scores dos 4 blocos
- **Output**: JSON completo com recomendações
- **Localização**: `/app/routers/analise_btc.py`

### **Camada 2: Cálculo de Blocos**
- **Responsabilidade**: Score ponderado por categoria
- **Routes**: `/api/v1/analise-ciclos`, `/api/v1/analise-riscos`, `/api/v1/analise-tecnica`, `/api/v1/analise-momentum`
- **Input**: Dados brutos de `obter-indicadores`
- **Output**: Score + detalhamento por indicador

### **Camada 3: Coleta e Cache (obter-indicadores)**
- **Responsabilidade**: Dados brutos + gestão de cache
- **Route**: `/api/v1/obter-indicadores/{bloco}`
- **Lógica de Cache**: 8h de validade
- **Fluxo**:
  - ✅ Existe + Atualizado → Retorna do banco
  - ❌ Não existe ou desatualizado → Coleta + Grava + Retorna

### **Camada 4: Fontes Externas**
- TradingView (tvDatafeed)
- Notion (databases)
- APIs financeiras (Glassnode, etc.)
- BigQuery (dados históricos)

## 📊 Padrão de Implementação por API

### **obter-indicadores** (Camada de Dados)
```python
# Localização: /app/routers/obter_indicadores.py
@router.get("/obter-indicadores/{bloco}", summary="Obter Dados", tags=["Dados"])
def obter_indicadores(bloco: str):
    # 1. Verificar cache no banco (8h)
    # 2. Se desatualizado: coletar + gravar
    # 3. Retornar dados brutos
    return {
        "bloco": "ciclo",
        "dados": {
            "MVRV_Z": {"valor": 2.1, "timestamp": "..."},
            "Realized_Ratio": {"valor": 1.3, "timestamp": "..."}
        }
    }
```

### **analise-[bloco]** (Camada de Cálculo)
```python
# Exemplo: /app/routers/analise_ciclos.py
@router.get("/analise-ciclos", summary="Analise Ciclos", tags=["Ciclos"])
def analisar_ciclos():
    # 1. Chamar obter-indicadores("ciclo")
    # 2. Aplicar fórmulas de score por indicador
    # 3. Calcular score ponderado do bloco
    return {
        "score": 5.5,
        "indicadores": {
            "MVRV_Z": {"valor": 2.1, "score": 6.0},
            "Realized_Ratio": {"valor": 1.3, "score": 5.5}
        }
    }
```

### **analise-btc** (Camada de Consolidação)
```python
# Localização: /app/routers/analise_btc.py
@router.get("/analise-btc", response_model=AnaliseBTCResponse, summary="Analise Geral", tags=["Analise BTC"])
def analise_geral():
    # 1. Chamar todas as APIs de bloco
    # 2. Aplicar pesos dinâmicos
    # 3. Calcular score final + recomendações
    return AnaliseBTCResponse  # Schema completo
```

## 🛣️ Estrutura de Rotas Padronizada

### **Configuração no main.py**
```python
from fastapi import FastAPI
from app.routers import (
    analise_btc, 
    analise_ciclos, 
    analise_riscos, 
    analise_tecnica, 
    analise_momentum,
    obter_indicadores
)

app = FastAPI()

# Padrão obrigatório: /api/v1/
app.include_router(analise_btc.router, prefix="/api/v1/analise-btc", tags=["Análise Principal"])
app.include_router(analise_ciclos.router, prefix="/api/v1/analise-ciclos", tags=["Ciclos"])
app.include_router(analise_riscos.router, prefix="/api/v1/analise-riscos", tags=["Riscos"])
app.include_router(analise_tecnica.router, prefix="/api/v1/analise-tecnica", tags=["Técnica"])
app.include_router(analise_momentum.router, prefix="/api/v1/analise-momentum", tags=["Momentum"])
app.include_router(obter_indicadores.router, prefix="/api/v1/obter-indicadores", tags=["Dados"])
```

## 🔧 Padrões Técnicos Obrigatórios

### **Gestão de Cache**
```python
# Em cada indicador
def get_dado_indicador(nome: str):
    if is_indicator_outdated(nome):  # > 8h
        return force_update_indicator(nome)
    return get_from_database(nome)
```

### **Estrutura de Pastas**
```
services/
├── blocos/          # Cálculo por bloco
│   ├── ciclo.py
│   ├── riscos.py
│   ├── tecnica.py
│   └── momentum.py
├── indicadores/     # Coleta individual
│   ├── ciclo/
│   ├── riscos/
│   └── ...
└── utils/           # Helpers (cache, validação)
```

### **Nomenclatura Padrão**
- **Função de coleta**: `get_dado_<indicador>()`
- **Função de score**: `calcular_score_<indicador>()`
- **Função de bloco**: `calcular_bloco_<nome>()`
- **Router pattern**: `@router.get("/analise-<bloco>", summary="...", tags=["..."])`
- **URL final**: `/api/v1/analise-<bloco>` ou `/api/v1/obter-indicadores/{bloco}`

## 🎯 JSON de Retorno Padronizado

### **obter-indicadores**
```json
{
  "bloco": "ciclo",
  "timestamp": "2025-05-26T13:00:00Z",
  "dados": {
    "MVRV_Z": {"valor": 2.1, "timestamp": "..."},
    "Realized_Ratio": {"valor": 1.3, "timestamp": "..."}
  }
}
```

### **analise-[bloco]**
```json
{
  "score": 5.5,
  "indicadores": {
    "MVRV_Z": {"valor": 2.1, "score": 6.0},
    "Realized_Ratio": {"valor": 1.3, "score": 5.5}
  }
}
```

### **analise-btc**
```json
{
  "timestamp": "...",
  "score_final": 5.85,
  "classificacao_geral": "Neutro",
  "blocos": {
    "ciclo": {"score": 5.5, "indicadores": {...}},
    "riscos": {"score": 6.2, "indicadores": {...}}
  }
}
```

## ⚙️ Configurações Centralizadas

### **Cache Settings**
```python
# app/config.py
CACHE_EXPIRATION_SECONDS: int = 28800  # 8h
UPDATE_THRESHOLD_HOURS: int = 8
```

### **Pesos dos Blocos**
```python
WEIGHT_CICLO: float = 0.40
WEIGHT_MOMENTUM: float = 0.25  
WEIGHT_RISCO: float = 0.15
WEIGHT_TECNICO: float = 0.20
```

## 🚨 Pontos Críticos de Implementação

### **1. Dependências entre APIs**
- `analise-btc` **depende** de todas as APIs de bloco
- APIs de bloco **dependem** de `obter-indicadores`
- Implementar timeouts e fallbacks

### **2. Gestão de Erro**
- Se indicador indisponível → peso 0
- Recalcular proporcionalmente outros indicadores
- Log detalhado de falhas

### **3. Performance**
- Cache inteligente (8h)
- Requisições paralelas quando possível
- Evitar cascata de calls desnecessárias

## 📋 Status Atual vs. Target

### ✅ **Implementado**
- Estrutura base da arquitetura
- API `analise-ciclos` (mockada)
- API `analise-btc` (consolidação mockada)
- Sistema de cache básico

### 🔄 **Em Desenvolvimento**
- API `obter-indicadores` (coleta real)
- APIs `analise-riscos`, `analise-tecnica`, `analise-momentum`
- Conexão com fontes externas reais

### ⏭️ **Próximos Passos**
1. Implementar `obter-indicadores` com coleta real
2. Criar APIs dos blocos restantes
3. Integrar fontes de dados externas
4. Testes de integração entre camadas

## 🛠️ Detalhamento Técnico por Bloco

### **Bloco Ciclo (40% peso)**
**Indicadores:**
- MVRV Z-Score (20%)
- Realized Price Ratio (15%)
- Puell Multiple (5%)

**Fontes:**
- Glassnode API
- CryptoQuant API
- LookIntoBitcoin

### **Bloco Momentum (25% peso)**
**Indicadores:**
- RSI Semanal (10%)
- Funding Rates 7D (8%)
- Open Interest Change 30D (4%)
- Long/Short Ratio (3%)

**Fontes:**
- TradingView (tvDatafeed)
- Coinglass API
- Binance API

### **Bloco Risco (15% peso)**
**Indicadores:**
- Distância do Liquidation (6%)
- Health Factor AAVE (4%)
- Exchange Netflow 7D (3%)
- Stablecoin Supply Ratio (2%)

**Fontes:**
- AAVE Protocol (Web3)
- CryptoQuant API
- Glassnode API

### **Bloco Técnico (20% peso)**
**Indicadores:**
- Sistema EMAs Multi-TF (15%)
- Padrões Gráficos (5%)

**Fontes:**
- TradingView (tvDatafeed)
- Análise algorítmica própria

## 🔍 Exemplo de Implementação Completa

### **1. obter-indicadores/ciclo**
```python
@router.get("/obter-indicadores/{bloco}", summary="Obter Dados", tags=["Dados"])
def obter_indicadores_ciclo(bloco: str):
    # Verificar cache
    cached_data = check_cache(bloco)
    if cached_data and not is_outdated(cached_data):
        return cached_data
    
    # Coletar dados específicos do bloco
    if bloco == "ciclo":
        mvrv_data = fetch_mvrv_from_glassnode()
        realized_data = fetch_realized_from_cryptoquant()
        puell_data = fetch_puell_from_lookinto()
        
        data = {
            "bloco": "ciclo",
            "timestamp": datetime.utcnow(),
            "dados": {
                "MVRV_Z": mvrv_data,
                "Realized_Ratio": realized_data,
                "Puell_Multiple": puell_data
            }
        }
    
    # Gravar no banco
    save_to_database(data)
    return data
```

### **2. analise-ciclos**
```python
@router.get("/analise-ciclos", summary="Analise Ciclos", tags=["Ciclos"])
def analisar_ciclos():
    # Obter dados brutos
    raw_data = requests.get("/api/v1/obter-indicadores/ciclo").json()
    
    # Calcular scores
    scores = {}
    for indicador, dados in raw_data["dados"].items():
        score = calculate_score(indicador, dados["valor"])
        scores[indicador] = {
            "valor": dados["valor"],
            "score": score
        }
    
    # Score ponderado do bloco
    bloco_score = calculate_weighted_score(scores, WEIGHTS_CICLO)
    
    return {
        "score": bloco_score,
        "indicadores": scores
    }
```

## 📝 Convenções de Desenvolvimento

### **Nomenclatura de Arquivos**
```
routers/
├── obter_indicadores.py
├── analise_ciclos.py
├── analise_riscos.py
├── analise_tecnica.py
├── analise_momentum.py
└── analise_btc.py

services/
├── blocos/
│   ├── ciclo.py
│   ├── riscos.py
│   ├── tecnica.py
│   └── momentum.py
├── indicadores/
│   ├── ciclo/
│   │   ├── mvrv_z_score.py
│   │   ├── realized_ratio.py
│   │   └── puell_multiple.py
│   └── ...
└── utils/
    ├── cache_helper.py
    ├── score_calculator.py
    └── data_fetcher.py
```

### **Padrão de Response Model**
```python
# Sempre usar Pydantic schemas com summary e tags específicas
@router.get("/analise-btc", response_model=AnaliseBTCResponse, summary="Analise Geral", tags=["Analise BTC"])
@router.get("/analise-ciclos", response_model=BlocoCicloResponse, summary="Analise Ciclos", tags=["Ciclos"])
@router.get("/obter-indicadores/{bloco}", response_model=IndicadoresResponse, summary="Obter Dados", tags=["Dados"])
```

### **Tratamento de Erros**
```python
try:
    data = fetch_external_api()
except APIException as e:
    logger.error(f"Erro na API externa: {e}")
    # Usar dados do cache ou valor padrão
    data = get_fallback_data()
except Exception as e:
    logger.error(f"Erro inesperado: {e}")
    raise HTTPException(status_code=500, detail="Erro interno")
```

## 🔗 Dependências Externas

### **APIs Requeridas**
- **Glassnode**: MVRV, Exchange Flow, Stablecoin metrics
- **CryptoQuant**: Realized Price, Mining data
- **Coinglass**: Funding Rates, Open Interest
- **TradingView**: Price data, Technical indicators
- **AAVE**: Health Factor via Web3

### **Configuração de API Keys**
```python
# app/config.py
GLASSNODE_API_KEY: str = Field(..., env="GLASSNODE_API_KEY")
CRYPTOQUANT_API_KEY: str = Field(..., env="CRYPTOQUANT_API_KEY")
COINGLASS_API_KEY: str = Field(..., env="COINGLASS_API_KEY")
AAVE_RPC_URL: str = Field(..., env="AAVE_RPC_URL")
```

## 🎯 Roadmap de Implementação

### **Fase 1: Infraestrutura Base**
- [ ] API `obter-indicadores` funcional
- [ ] Sistema de cache no PostgreSQL
- [ ] Conexões com APIs externas
- [ ] Tratamento de erros robusto

### **Fase 2: Blocos Individuais**
- [ ] `analise-ciclos` completo
- [ ] `analise-riscos` completo  
- [ ] `analise-tecnica` completo
- [ ] `analise-momentum` completo

### **Fase 3: Consolidação**
- [ ] `analise-btc` integrado
- [ ] Pesos dinâmicos funcionais
- [ ] Sistema de alertas ativo
- [ ] Documentação de APIs (Swagger)

### **Fase 4: Otimização**
- [ ] Cache distribuído (Redis)
- [ ] Requisições paralelas
- [ ] Monitoramento e logs
- [ ] Testes automatizados

---

**Arquitetura modular, escalável e com separação clara de responsabilidades.**

**Projeto:** BTC Turbo API  
**Versão:** 1.0  
**Data:** Maio 2025  
**Autor:** Equipe de Desenvolvimento