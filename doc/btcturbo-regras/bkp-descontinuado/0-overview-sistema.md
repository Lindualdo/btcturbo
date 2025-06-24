# BTCTURBO - Sistema de Análise BTC - 4 Camadas - Overview


```
1 - Analise de mercado 
- faz analise em 3 blocos (ciclos, momentum e tecncio) e gera um score final
- com base no score define o ciclo de mercado 
- o cilco responde se devo estar posicionado e o tamanho das posições
2 - Analise de risco
- analisa os indicadores financeiros (plataforma AAVE)
- o score final define a saúde da minha posição
- responde se minha posição está segura
3 - Analise de alavancagem
- Analise o score de mercado, indicadores de ciclo e IFR mensal
- retorna o limite da margem de alavancagem (max 3X)
4 - Execução tática
- aplica regras e validações de proteção (gate system)
- se liberado para operar, define o setup e estrategia
```


```
┌─────────────────────────────────────────────────────────────────┐
│                    SISTEMA DE ANÁLISE BTC                       │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    1. ANÁLISE DE MERCADO                        │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │    CICLOS   │  │  MOMENTUM   │  │  TÉCNICO    │              │
│  │             │  │             │  │             │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
│           │              │              │                       │
│           └──────────────┼──────────────┘                       │
│                          ▼                                      │
│                  ┌─────────────┐                                │
│                  │ SCORE FINAL │ ──────┐                        │
│                  └─────────────┘       │                        │
│                          │             │                        │
│                          ▼             │                        │
│                  ┌─────────────┐       │                        │
│                  │CICLO MERCADO│       │                        │
│                  └─────────────┘       │                        │
│                          │             │                        │
│                          ▼             │                        │
│            Posicionamento + Tamanho    │                        │
└────────────────────────────────────────┼───────────────────────-┘
                                         │
┌────────────────────────────────────────┼────────────────────────┐
│                    2. ANÁLISE DE RISCO │                        │
├────────────────────────────────────────┼────────────────────────┤
│          ┌─────────────────┐           │                        │
│          │ INDICADORES     │           │                        │
│          │ FINANCEIROS     │           │                        │
│          │ (AAVE)          │           │                        │
│          └─────────────────┘           │                        │
│                    │                   │                        │
│                    ▼                   │                        │
│          ┌─────────────────┐           │                        │
│          │ SCORE SAÚDE     │           │                        │
│          │ POSIÇÃO         │           │                        │
│          └─────────────────┘           │                        │
│                    │                   │                        │
│                    ▼                   │                        │
│            Posição Segura?             │                        │
└────────────────────────────────────────┼────────────────────────┘
                                         │
┌────────────────────────────────────────┼───────────────────────┐
│                 3. ANÁLISE ALAVANCAGEM │                       │
├────────────────────────────────────────┼───────────────────────┤
│  ┌─────────────┐  ┌──────────────┐  ┌──┼─────────────┐         │
│  │SCORE MERCADO│  │INDICADORES   │  │  │IFR MENSAL   │         │
│  │             │  │CICLO         │  │  │             │         │
│  └─────────────┘  └──────────────┘  └──┼─────────────┘         │
│           │              │             │     │                 │
│           └──────────────┼─────────────┘     │                 │
│                          ▼                   │                 │
│                  ┌─────────────┐             │                 │
│                  │ LIMITE      │             │                 │
│                  │ MARGEM      │             │                 │
│                  │ (MAX 3X)    │             │                 │
│                  └─────────────┘             │                 │
└──────────────────────────────────────────────┼─────────────────┘
                                               │
┌───────────────────────────────────────────── ┼─────────────────┐
│                 4. EXECUÇÃO TÁTICA           │                 │
├───────────────────────────────────────────── ┼─────────────────┤
│          ┌─────────────────┐                 │                 │
│          │ GATE SYSTEM     │                 │                 │
│          │ (Proteções)     │                 │                 │
│          └─────────────────┘                 │                 │
│                    │                         │                 │
│                    ▼                         │                 │
│          ┌─────────────────┐                 │                 │
│          │ Liberado para   │                 │                 │
│          │ Operar?         │                 │                 │
│          └─────────────────┘                 │                 │
│                    │                         │                 │
│                    ▼                         │                 │
│          ┌─────────────────┐                 │                 │
│          │ SETUP +         │ ◄───────────────┘                 │
│          │ ESTRATÉGIA      │                                   │
│          └─────────────────┘                                   │
│                    │                                           │
│                    ▼                                           │
│               EXECUÇÃO                                         │
└────────────────────────────────────────────────────────────────┘
```

## Fluxo de Decisão

**ENTRADA** → Análise Mercado → Análise Risco → Análise Alavancagem → Execução Tática → **OPERAÇÃO**

### Pontos de Controle:

1. **Mercado**: Define se deve estar posicionado
2. **Risco**: Valida se posição está segura  
3. **Alavancagem**: Estabelece limite máximo (3x)
4. **Execução**: Gate system + validações finais

### Saídas por Camada:

- **Camada 1**: Ciclo de mercado + Tamanho posição
- **Camada 2**: Status segurança posição
- **Camada 3**: Limite margem alavancagem
- **Camada 4**: Setup + Estratégia de execução