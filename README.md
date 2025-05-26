# BTC Turbo API

API para análise modular de indicadores do Bitcoin com FastAPI.

## 📁 Estrutura

- `routers/` — Endpoints da API
- `services/` — Lógica de cálculo (separado por bloco/indicador)
- `models/` — ORM SQLAlchemy
- `schemas/` — Modelos de resposta (Pydantic)
- `db/` — Conexão com PostgreSQL
- `doc/` — Documentação e resumo do projeto


## 🌏 Infraestrutura & Deploy

### 🚀 Railway (Produção)
- Ambiente provisionado com Docker + FastAPI.
- Deploy contínuo via GitHub (branch `main`).
- Variáveis de ambiente configuradas manualmente:
  - `TV_USERNAME`
  - `TV_PASSWORD`
  - `NOTION_TOKEN`
  - `NOTION_DATABASE_ID_EMA`
  - `NOTION_DATABASE_ID_MACRO`
  - `WALLET_ADDRESS`

---

## 🚀 Dependências Principais

- `FastAPI` / `Uvicorn`
- `tvDatafeed` (via GitHub: `rongarDF`)
- `pandas`
- `notion-client`
- `pydantic-settings >= 2.0.0`
- `web3`

---

## 🔧 Padrões Técnicos

- APIs organizadas por domínio (`/v1/analise-tecnica-emas`, `/v1/analise-ciclos`).
- Separação clara entre lógica, serviços e configuração.
- `config.py` centralizado via `BaseSettings` e `@lru_cache`.
- Dockerfile controlado manualmente (Railway via modo Dockerfile).
- Swagger e OpenAPI prontos para uso.
- Uso de query parameters para `username` e `password` (TV).
- 📚 Cada novo endpoint deve seguir o padrão `routers + services + utils`.

```python
app.include_router(analise_tecnica_emas.router, prefix="/api/v1")
```

### Nos Routers usar assim
```python
@router.get("/analise-ciclos", 
            summary="Análise de ciclos do BTC", 
            tags=["Ciclos"])
```