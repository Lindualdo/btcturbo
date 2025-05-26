# 📊 API OBTER INDICADORES - Documentação Completa

## 📋 OBJETIVO
Criar endpoint `/obter-indicadores` que centraliza acesso a todos os dados de indicadores com controle inteligente de cache e força atualização opcional.

## 🏗️ ARQUITETURA FINAL

### Fluxo de Uso Universal
```
APIs de Score → /obter-indicadores → PostgreSQL (dados sempre atuais)
N8N Scheduler → /obter-indicadores?forcar=true → Força atualização
Dashboard → /obter-indicadores → Dados disponíveis
```

### Controle de Cache Inteligente
- **`forcar=false`** (padrão): Retorna dados + atualiza se necessário
- **`forcar=true`**: Força atualização + retorna dados atualizados

## 📁 ESTRUTURA DE ARQUIVOS

```
app/
├── routers/
│   └── obter_indicadores.py     # API centralizadora (NOVO NOME)
├── services/
│   └── blocos/
│       ├── update_ciclo.py      # Bloco ciclo (implementar)
│       ├── update_momentum.py   # Bloco momentum (futuro)
│       ├── update_risco.py      # Bloco risco (futuro)
│       └── update_tecnico.py    # Bloco técnico (futuro)
└── utils/
    └── postgres_helper.py       # Já existe
```

## 🔧 IMPLEMENTAÇÃO OBRIGATÓRIA

### 1. Arquivo: `app/routers/obter_indicadores.py`

```python
from fastapi import APIRouter, Query, HTTPException
from datetime import datetime
from typing import Dict, List
import logging

router = APIRouter()

@router.get("/obter-indicadores", 
            summary="Obter Todos Indicadores", 
            tags=["Indicadores"])
def obter_todos_indicadores(forcar: bool = Query(False, description="Forçar atualização dos dados ignorando cache")):
    """
    Obtém dados de todos os blocos de indicadores do PostgreSQL.
    Atualiza automaticamente se dados estiverem desatualizados ou se forçado.
    
    Esta é a API CENTRALIZADORA usada por:
    - APIs de score (/analise-btc, /analise-ciclo)
    - Scheduler N8N (com forcar=true)
    - Dashboard e outras consultas
    
    Args:
        forcar: Se True, ignora cache e força atualização de todos os blocos
        
    Returns:
        Dados brutos atuais de todos os blocos + status de processamento
    """
    resultado = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "parametro_forcar": forcar,
        "blocos_processados": {},
        "dados_brutos": {},  # ← DADOS SEMPRE RETORNADOS
        "resumo": {
            "total_blocos": 0,
            "blocos_atualizados": 0,
            "blocos_cache": 0,
            "blocos_erro": 0
        }
    }
    
    # Lista de blocos disponíveis no sistema
    blocos = [
        ("ciclo", "app.services.blocos.update_ciclo", "update_ciclo"),
        # ("momentum", "app.services.blocos.update_momentum", "update_momentum"),  # Futuro
        # ("risco", "app.services.blocos.update_risco", "update_risco"),          # Futuro
        # ("tecnico", "app.services.blocos.update_tecnico", "update_tecnico")     # Futuro
    ]
    
    for nome_bloco, modulo_path, funcao_nome in blocos:
        try:
            # Import dinâmico do módulo do bloco
            modulo = __import__(modulo_path, fromlist=[funcao_nome])
            funcao_update = getattr(modulo, funcao_nome)
            
            # Executa obtenção/atualização do bloco
            resultado_bloco = funcao_update(forcar=forcar)
            
            # Registra status do processamento
            resultado["blocos_processados"][nome_bloco] = {
                "atualizado": resultado_bloco["atualizado"],
                "motivo": resultado_bloco["motivo"],
                "fonte": resultado_bloco.get("fonte"),
                "timestamp_dados": resultado_bloco.get("timestamp_dados"),
                "timestamp_processamento": resultado_bloco.get("timestamp_atualizacao", resultado_bloco.get("timestamp_verificacao"))
            }
            
            # SEMPRE inclui dados brutos atuais do PostgreSQL
            resultado["dados_brutos"][nome_bloco] = resultado_bloco["dados"]
            
            # Atualiza contadores
            resultado["resumo"]["total_blocos"] += 1
            
            if resultado_bloco["atualizado"]:
                resultado["resumo"]["blocos_atualizados"] += 1
            else:
                resultado["resumo"]["blocos_cache"] += 1
                
            logging.info(f"Bloco {nome_bloco} obtido com sucesso")
            
        except Exception as e:
            erro_detalhes = {
                "atualizado": False,
                "motivo": "erro",
                "erro": str(e),
                "tipo_erro": type(e).__name__,
                "timestamp_erro": datetime.utcnow().isoformat() + "Z"
            }
            
            resultado["blocos_processados"][nome_bloco] = erro_detalhes
            resultado["dados_brutos"][nome_bloco] = None  # Indica erro
            resultado["resumo"]["blocos_erro"] += 1
            
            logging.error(f"Erro ao obter bloco {nome_bloco}: {str(e)}")
    
    # Se todos os blocos falharam, retorna erro HTTP
    if resultado["resumo"]["blocos_erro"] == resultado["resumo"]["total_blocos"]:
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Falha ao obter dados de todos os blocos",
                "detalhes": resultado
            }
        )
    
    return resultado
```

### 2. Arquivo: `app/services/blocos/update_ciclo.py`

```python
from datetime import datetime
from typing import Dict
import logging

def update_ciclo(forcar: bool = False) -> Dict:
    """
    Atualiza indicadores do bloco ciclo.
    
    Args:
        forcar: Se True, ignora cache e força atualização
        
    Returns:
        Dict com status da atualização
    """
    try:
        from app.services.utils.postgres_helper import is_ciclo_outdated, get_dados_ciclo
        from app.services.integracao.notion_ciclo_reader import get_ciclo_data_from_notion, update_ciclo_from_notion
        
        # Verifica se precisa atualizar (ou se está sendo forçado)
        precisa_atualizar = forcar or is_ciclo_outdated(hours=8)
        
        if not precisa_atualizar:
            # Dados ainda válidos, retorna do cache
            dados_cache = get_dados_ciclo()
            
            logging.info("Bloco ciclo: Usando dados do cache PostgreSQL")
            
            return {
                "bloco": "ciclo",
                "atualizado": False,
                "motivo": "cache_valido",
                "dados": {
                    "mvrv_z_score": dados_cache.get("mvrv_z_score"),
                    "realized_ratio": dados_cache.get("realized_ratio"),
                    "puell_multiple": dados_cache.get("puell_multiple")
                },
                "fonte": dados_cache.get("fonte"),
                "timestamp_dados": dados_cache.get("timestamp").isoformat() if dados_cache.get("timestamp") else None,
                "timestamp_verificacao": datetime.utcnow().isoformat() + "Z"
            }
        
        # Precisa atualizar - busca do Notion
        logging.info("Bloco ciclo: Buscando dados atualizados do Notion")
        
        # Chama função que busca Notion e salva PostgreSQL
        sucesso = update_ciclo_from_notion()
        
        if not sucesso:
            raise Exception("Falha ao atualizar dados do Notion")
        
        # Busca dados recém-salvos para confirmar
        dados_atualizados = get_dados_ciclo()
        
        return {
            "bloco": "ciclo",
            "atualizado": True,
            "motivo": "forcado" if forcar else "cache_expirado",
            "dados": {
                "mvrv_z_score": dados_atualizados.get("mvrv_z_score"),
                "realized_ratio": dados_atualizados.get("realized_ratio"),
                "puell_multiple": dados_atualizados.get("puell_multiple")
            },
            "fonte": "Notion",
            "timestamp_dados": dados_atualizados.get("timestamp").isoformat() if dados_atualizados.get("timestamp") else None,
            "timestamp_atualizacao": datetime.utcnow().isoformat() + "Z"
        }
        
    except Exception as e:
        logging.error(f"Erro ao atualizar bloco ciclo: {str(e)}")
        
        return {
            "bloco": "ciclo",
            "atualizado": False,
            "motivo": "erro",
            "erro": str(e),
            "timestamp_erro": datetime.utcnow().isoformat() + "Z"
        }
```

### 3. Registrar no `app/main.py`

```python
from fastapi import FastAPI
from app.routers import analise_btc, analise_ciclo, test_endpoint_notion, obter_indicadores

app = FastAPI(
    title="BTC Turbo API",
    description="Sistema de análise de indicadores BTC",
    version="1.0.0"
)

# Rotas principais
app.include_router(analise_ciclo.router, prefix="/analise-ciclo")
app.include_router(analise_btc.router, prefix="/analise-btc")

# API centralizadora de dados
app.include_router(obter_indicadores.router, prefix="/api")

# Rota de teste (temporária)
app.include_router(test_endpoint_notion.router, prefix="/debug")
```

### 4. Integração com APIs de Score

#### Exemplo: Atualizar `/analise-ciclo`
```python
# app/routers/analise_ciclo.py

from fastapi import APIRouter, HTTPException
import requests
from app.config import get_settings

router = APIRouter()

@router.get("/")
def analisar_ciclo():
    """
    Análise do bloco ciclo usando dados centralizados.
    Chama API obter-indicadores para garantir dados atuais.
    """
    try:
        settings = get_settings()
        
        # Chama API centralizadora para obter dados atuais
        response = requests.get(f"http://localhost:{settings.PORT}/api/obter-indicadores")
        response.raise_for_status()
        
        dados_api = response.json()
        dados_ciclo = dados_api["dados_brutos"]["ciclo"]
        
        if not dados_ciclo:
            raise HTTPException(status_code=500, detail="Dados do bloco ciclo indisponíveis")
        
        # Calcula scores usando dados reais
        return {
            "score": calcular_score_bloco_ciclo(dados_ciclo),
            "indicadores": {
                "MVRV_Z": {
                    "valor": dados_ciclo["mvrv_z_score"],
                    "score": calcular_score_mvrv(dados_ciclo["mvrv_z_score"])
                },
                "Realized_Ratio": {
                    "valor": dados_ciclo["realized_ratio"],
                    "score": calcular_score_realized(dados_ciclo["realized_ratio"])
                },
                "Puell_Multiple": {
                    "valor": dados_ciclo["puell_multiple"],
                    "score": calcular_score_puell(dados_ciclo["puell_multiple"])
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter dados: {str(e)}")

def calcular_score_bloco_ciclo(dados_ciclo):
    """Calcula score consolidado do bloco ciclo"""
    # Implementar lógica de cálculo
    return 5.5

def calcular_score_mvrv(valor):
    """Calcula score do MVRV baseado no valor"""
    # Implementar lógica específica
    return 6.0

def calcular_score_realized(valor):
    """Calcula score do Realized Ratio baseado no valor"""
    # Implementar lógica específica
    return 5.5

def calcular_score_puell(valor):
    """Calcula score do Puell Multiple baseado no valor"""
    # Implementar lógica específica
    return 5.0
```

## 📋 CHECKLIST DE IMPLEMENTAÇÃO

### ✅ Pré-Requisitos (já existe)
- [ ] PostgreSQL configurado e funcionando
- [ ] Tabelas criadas (indicadores_ciclo, etc.)
- [ ] `postgres_helper.py` implementado
- [ ] `notion_ciclo_reader.py` funcionando

### ✅ Implementação (fazer)
- [ ] Criar `app/routers/atualizar.py`
- [ ] Criar `app/services/blocos/update_ciclo.py`
- [ ] Registrar router no `main.py`
- [ ] Deploy da aplicação

### ✅ Testes (validar)
- [ ] `/api/atualizar-indicadores` (sem parâmetros)
- [ ] `/api/atualizar-indicadores?forcar=true`
- [ ] Verificar dados no PostgreSQL após cada teste
- [ ] Verificar logs de funcionamento

## 🧪 TESTES OBRIGATÓRIOS

### Teste 1: Cache Válido
```bash
POST /api/atualizar-indicadores
# Deve retornar: "atualizado": false, "motivo": "cache_valido"
```

### Teste 2: Forçar Atualização
```bash
POST /api/atualizar-indicadores?forcar=true
# Deve retornar: "atualizado": true, "motivo": "forcado"
```

### Teste 3: Cache Expirado
```bash
# Esperar > 8 horas ou alterar threshold para 0.1h
POST /api/atualizar-indicadores
# Deve retornar: "atualizado": true, "motivo": "cache_expirado"
```

## 📊 FORMATO DE RESPOSTA ESPERADO

```json
{
  "timestamp": "2025-05-26T20:00:00.000000Z",
  "parametro_forcar": false,
  "blocos_processados": {
    "ciclo": {
      "atualizado": true,
      "motivo": "cache_expirado",
      "fonte": "Notion",
      "timestamp_dados": "2025-05-26T20:00:00.000000",
      "timestamp_processamento": "2025-05-26T20:00:01.000000Z"
    }
  },
  "dados_brutos": {
    "ciclo": {
      "mvrv_z_score": 2.75,
      "realized_ratio": 46204.0,
      "puell_multiple": 1.44
    }
  },
  "resumo": {
    "total_blocos": 1,
    "blocos_atualizados": 1,
    "blocos_cache": 0,
    "blocos_erro": 0
  }
}
```

### Cenário com Cache Válido
```json
{
  "timestamp": "2025-05-26T20:00:00.000000Z",
  "parametro_forcar": false,
  "blocos_processados": {
    "ciclo": {
      "atualizado": false,
      "motivo": "cache_valido",
      "fonte": "Notion",
      "timestamp_dados": "2025-05-26T19:30:00.000000",
      "timestamp_processamento": "2025-05-26T20:00:01.000000Z"
    }
  },
  "dados_brutos": {
    "ciclo": {
      "mvrv_z_score": 2.75,
      "realized_ratio": 46204.0,
      "puell_multiple": 1.44
    }
  },
  "resumo": {
    "total_blocos": 1,
    "blocos_atualizados": 0,
    "blocos_cache": 1,
    "blocos_erro": 0
  }
}
```

### Cenário com Erro
```json
{
  "timestamp": "2025-05-26T20:00:00.000000Z",
  "parametro_forcar": false,
  "blocos_processados": {
    "ciclo": {
      "atualizado": false,
      "motivo": "erro",
      "erro": "Connection to database failed",
      "tipo_erro": "ConnectionError",
      "timestamp_erro": "2025-05-26T20:00:01.000000Z"
    }
  },
  "dados_brutos": {
    "ciclo": null
  },
  "resumo": {
    "total_blocos": 1,
    "blocos_atualizados": 0,
    "blocos_cache": 0,
    "blocos_erro": 1
  }
}
```

## 🚨 TRATAMENTO DE ERROS

### Erro Individual (bloco falha)
- Bloco com erro não impede outros blocos
- Erro é registrado no relatório
- Log detalhado do problema

### Erro Total (todos os blocos falham)
- HTTP 500 com detalhes completos
- Relatório completo no detail
- Logs estruturados para debugging

## 🔮 PREPARAÇÃO PARA EXPANSÃO

### Estrutura Preparada para Novos Blocos
```python
# Adicionar na lista de blocos:
blocos = [
    ("ciclo", "app.services.blocos.update_ciclo", "update_ciclo"),
    ("momentum", "app.services.blocos.update_momentum", "update_momentum"),  # ← Futuro
    ("risco", "app.services.blocos.update_risco", "update_risco"),          # ← Futuro
    ("tecnico", "app.services.blocos.update_tecnico", "update_tecnico")     # ← Futuro
]
```

### Template para Novos Blocos
```python
# app/services/blocos/update_NOME.py
def update_NOME(forcar: bool = False) -> Dict:
    # 1. Verificar cache ou forçar
    # 2. Se válido: retornar PostgreSQL
    # 3. Se inválido: buscar origem → salvar PostgreSQL
    # 4. Retornar resultado padronizado
```

## 📌 PONTOS CRÍTICOS

1. **SEMPRE Retornar Dados Brutos**: API sempre retorna dados atuais do PostgreSQL
2. **Separação Clara**: `blocos_processados` = status da operação, `dados_brutos` = dados atuais
3. **Import Dinâmico**: Permite adicionar blocos sem alterar código principal
4. **Tratamento de Erro Individual**: Um bloco com problema não quebra todos
5. **Cache Granular**: Cada bloco tem seu próprio controle de atualização
6. **Logs Estruturados**: Facilita debugging em produção
7. **Dados Sempre Disponíveis**: Cliente sempre recebe dados, mesmo se cache for usado

## 🎯 REGRA FUNDAMENTAL

**A API SEMPRE retorna os dados brutos atuais do PostgreSQL:**
- ✅ **Cache usado**: Retorna dados existentes do PostgreSQL
- ✅ **Dados atualizados**: Retorna dados recém-salvos no PostgreSQL  
- ❌ **Erro no bloco**: Retorna `null` para aquele bloco
- ✅ **Outros blocos OK**: Retorna dados dos blocos que funcionaram

**Cliente sempre tem acesso aos dados mais recentes disponíveis no sistema!**

---

**🎯 ENTREGÁVEIS:**
1. Arquivo `atualizar.py` funcionando
2. Arquivo `update_ciclo.py` funcionando  
3. Router registrado no main.py
4. Testes passando com ambos parâmetros
5. Logs estruturados funcionando

**⏱️ TEMPO ESTIMADO: 4-6 horas de desenvolvimento**