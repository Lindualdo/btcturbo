# BTC Turbo API

API para análise modular de indicadores do Bitcoin com FastAPI.

## 🔧 Arquitetura

- Modular por bloco (`ciclo`, `momentum`, etc.)
- Verificação automática de dados desatualizados
- Preparado para Railway e GitHub

## 📁 Estrutura

- `routers/` — Endpoints da API
- `services/` — Lógica de cálculo (separado por bloco/indicador)
- `models/` — ORM SQLAlchemy
- `schemas/` — Modelos de resposta (Pydantic)
- `db/` — Conexão com PostgreSQL
- `doc/` — Documentação e resumo do projeto

## ▶️ Execução

```bash
uvicorn app.main:app --reload
```