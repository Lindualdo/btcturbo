# 📘 Manual Técnico do Desenvolvedor — API BTC Turbo

Este documento define as **regras técnicas obrigatórias** para desenvolvimento, manutenção e expansão da API BTC Turbo.  
Todo novo código deverá seguir esta arquitetura e os padrões definidos aqui.

---

## 🎯 Objetivo do Projeto

Construir uma API modular em **FastAPI** que:
- Consolida scores por indicadores e blocos temáticos (Ciclo, Momentum, Risco, Técnico)
- Gera uma resposta JSON padronizada para ser consumida por sistemas externos
- Permite manutenção, testes e extensibilidade com segurança e clareza

---

## 🧱 Estrutura de Pastas

```
app/
├── main.py                  # Entrada da aplicação FastAPI
├── config.py                # Configurações e variáveis de ambiente
├── db/                      # Conexão com o PostgreSQL
│   └── database.py
├── models/                  # ORM (SQLAlchemy)
│   └── indicators.py
├── schemas/                 # Pydantic - definição de resposta da API
│   └── response_model.py
├── routers/                 # Endpoints da API (1 por rota)
│   ├── analise_btc.py
│   ├── analise_ciclo.py
│   └── atualizar.py
├── services/                # Lógica de negócio dividida por blocos e indicadores
│   ├── blocos/              # Cálculo de cada bloco (ciclo, risco...)
│   │   └── ciclo.py
│   ├── ciclo/               # Indicadores individuais do bloco ciclo
│   │   ├── mvrv_z_score.py
│   │   ├── puell_multiple.py
│   │   └── realized_ratio.py
│   └── utils/               # Lógicas auxiliares internas aos serviços
│       └── indicadores_helper.py
├── utils/                   # Utilitários genéricos usados em todo o projeto
│   └── formula_utils.py
schemas/
└── response_model.py        # Schema de resposta padrão da API
```

---

## 🧩 Modelo de Resposta: `AnaliseBTCResponse`

Local: `app/schemas/response_model.py`

Todos os endpoints que retornarem a análise consolidada devem usar este modelo com:

```python
@router.get("/", response_model=AnaliseBTCResponse)
```

A estrutura inclui:
- `timestamp`, `score_final`, `score_ajustado`
- `modificador_volatilidade`, `classificacao_geral`, `kelly_allocation`, `acao_recomendada`
- `alertas_ativos`, `pesos_dinamicos`
- `blocos` com `score` e `indicadores`

---

## 🛠️ Padrão de Implementação por Indicador

Cada indicador deve seguir este padrão:

### 1. `get_dado_<indicador>()`
- Verifica se os dados estão atualizados usando `is_indicator_outdated(nome)`
- Se não estiverem, chama `force_update_indicator(nome)`
- Sempre retorna `valor`, `score`, `last_update`

### 2. `calcular_score_<indicador>()`
- Usa `get_dado_<indicador>()`
- Retorna `{ "valor": ..., "score": ... }`

Exemplo (mvrv_z_score.py):
```python
def calcular_score_mvrv():
    dado = get_dado_mvrv()
    return { "valor": dado["valor"], "score": dado["score"] }
```

---

## 🔁 Modularização dos Blocos

Cada **bloco** (ex: Ciclo) possui:
- Um arquivo em `services/blocos/ciclo.py`
- Função `calcular_bloco_ciclo()`
- Essa função chama os `calcular_score_*` dos seus indicadores e monta:
```python
{
  "score": 5.5,
  "indicadores": {
    "MVRV_Z": { "valor": ..., "score": ... },
    ...
  }
}
```

---
## Json padrão para os blocos - usar analise-ciclos como modelo

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

---

## Json padrão para analise-btc (api principal)

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
        "ciclo": 0.4,
        "momentum": 0.25,
        "risco": 0.15,
        "tecnico": 0.2
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

---

## 🧠 Regras para Dados Atualizados

- Toda função de cálculo **deve verificar se os dados estão atualizados**
- A verificação é feita com:
```python
from app.services.utils.indicadores_helper import is_indicator_outdated, force_update_indicator
```
- Tempo de validade: 8 horas
- Se estiver desatualizado, deve forçar atualização com `force_update_indicator()`

---

## 🚨 Padrões de Nomenclatura

| Elemento                      | Padrão                             |
|------------------------------|-------------------------------------|
| Função de score indicador    | `calcular_score_<nome>()`          |
| Função de dado bruto         | `get_dado_<nome>()`                |
| Nome do arquivo indicador    | `<nome>.py` em snake_case          |
| Score de bloco               | `calcular_bloco_<bloco>()`         |
| Retorno de cada indicador    | `{"valor": ..., "score": ...}`     |
| Bloco no JSON                | `{"score": ..., "indicadores": {}}`|

---

## 🔐 Segurança e Validação

- Sempre tipar o retorno com `response_model`
- Nunca retornar JSONs "soltos" fora do schema
- Usar `List[str]`, `Dict[str, ...]`, `datetime` — não strings genéricas

---

## 🔍 Swagger e Testes

- Acesse `/docs` para validar a estrutura
- Qualquer mudança no modelo exige validação contra o schema
- Validar com clientes externos se a estrutura permanece íntegra

---

## 📌 Conclusão

Este padrão garante:
- Robustez da arquitetura
- Clareza entre devs
- Integração com automações e sistemas externos

**NUNCA** quebre a estrutura de retorno sem versionamento.  
**TODO novo indicador ou bloco deve seguir o padrão descrito aqui.**