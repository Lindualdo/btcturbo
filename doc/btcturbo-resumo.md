# BTC TURBO - Arquitetura V2

## Objetivo
Sistema modular de análise de indicadores do BTC com score e alertas automatizados.

## Fluxo Geral
1. Coleta de dados (Notion, APIs, TradingView)
2. Armazenamento em PostgreSQL
3. Verificação de desatualização (>8h)
4. Cálculo de score por indicador e bloco
5. Consolidação final via API

## APIs
- `/analise-ciclo` — Bloco ciclo mockado
- `/analise-btc` — Consolidação final mockada (usa ciclo)

## Padrão de Desenvolvimento
- Cada indicador tem seu próprio arquivo
- Blocos agrupam os indicadores
- Atualização forçada será chamada se `last_update` for >8h
- APIs separadas por responsabilidade