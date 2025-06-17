# 🔍 TESTE COMPLETO FINAL 
REGRAS DE NEGÓCIO E INTEGRIDADE DO CODIGO - 4 categorias proioritárias de Alertas
- Criticos
- Urgentes
- Volatilidade
- Táticos

## Alertas criticos
Objetivo: Ação imediata

### Regra dos alertas

Debug categoria CRÍTICOS - Proteção capital
- Health Factor < 1.3
- Distância Liquidação < 20%
- Score Risco < 30
- Portfolio Loss 24h > 20%
- Leverage > MVRV Max * 1.2

### Validação confiabilidade do codigo
comparação entre as funções do debug e produção para garantir que ambas usam o mesmo core

´´´
FLUXO DEBUG (/alertas-debug/criticos)
├── main.py
├── routers/
│   └── alertas_debug.py
│       └── debug_alertas_criticos()
├── services/
│   └── alertas/
│       └── debug_service.py
│           └── debug_criticos()
└── detectores/
    └── criticos_detector.py
        └── get_debug_info()
            ├── get_dados_risco()
            ├── calcular_analise_risco()
            ├── calcular_analise_alavancagem()
            ├── _extract_distance_value()
            ├── _extract_leverage_value()
            └── _calculate_portfolio_loss_24h()

FLUXO PRODUÇÃO (/api/v1/alertas/verificar)
├── main.py
├── routers/
│   └── alertas.py
│       └── verificar_alertas()
├── services/
│   └── alertas/
│       └── engine.py
│           └── verificar_todos_alertas()
└── detectores/
    └── criticos_detector.py
        └── verificar_alertas()
            ├── get_dados_risco()               ← MESMA FUNÇÃO
            ├── calcular_analise_risco()        ← MESMA FUNÇÃO
            ├── calcular_analise_alavancagem()  ← MESMA FUNÇÃO
            ├── _check_health_factor_critico()
            │   └── _extract_distance_value()   ← MESMA FUNÇÃO
            ├── _check_distancia_liquidacao_critico()
            │   └── _extract_distance_value()   ← MESMA FUNÇÃO
            ├── _check_score_risco_critico()
            ├── _check_portfolio_loss_critico()
            │   └── _calculate_portfolio_loss_24h() ← MESMA FUNÇÃO
            └── _check_overleveraged_critico()
                └── _extract_leverage_value()   ← MESMA FUNÇÃO
´´´

## ✅ VALIDAÇÃO CONFIABILIDADE
### Funções Compartilhadas:

- get_dados_risco() ✓
- calcular_analise_risco() ✓
- calcular_analise_alavancagem() ✓
- _extract_distance_value() ✓
- _extract_leverage_value() ✓
- _calculate_portfolio_loss_24h() ✓

### 🔍 INTEGRIDADE (Código vs Doc)

Thresholds Conformes:

- Health Factor: 1.3 ✓
- Distância Liquidação: 20% ✓
- Score Risco: 30 ✓
- Portfolio Loss: -20% ✓
- Overleveraged: 2.4x (2.0 * 1.2) ✓

- Todos os 5 alertas implementados conforme especificação.

### Json final - debug
O debug já incorpora os dados da coleta + o resultado dos alertas

```json
{
    "categoria": "CRÍTICOS - Proteção de Capital",
    "timestamp": "2025-06-08T06:45:47.161208",
    "dados_coletados": {
        "health_factor": 2.800525,
        "dist_liquidacao": 64.292412,
        "score_risco": 95.0,
        "aumento_capital_24h": {
            "percentual": 0.76,
            "valor_dolares": 480.01,
            "formatado": "+0.76%"
        },
        "alavancagem_atual": 1.39,
        "max_leverage_permitido": 2.0
    },
    "alertas_status": {
        "health_factor": {
            "valor_atual": 2.800525,
            "threshold": 1.3,
            "disparado": false,
            "acao": "Monitorar"
        },
        "distancia_liquidacao": {
            "valor_atual": 64.292412,
            "threshold": 20.0,
            "disparado": false,
            "acao": "Monitorar"
        },
        "score_risco": {
            "valor_atual": 95.0,
            "threshold": 30.0,
            "disparado": false,
            "acao": "Monitorar"
        },
        "portfolio_loss_24h": {
            "valor_atual": 0.7634649949551949,
            "threshold": -20.0,
            "disparado": false,
            "acao": "Monitorar"
        },
        "overleveraged": {
            "valor_atual": 1.39,
            "threshold": 2.4,
            "disparado": false,
            "acao": "Monitorar"
        }
    },
    "total_disparados": 0,
    "fontes_dados": {
        "dados_risco_ok": true,
        "analise_risco_ok": true,
        "analise_alavancagem_ok": true
    }
}
```
´´´
---

## Alertas urgentes
Obertivo: preventivo, se não agir vira critico

Debug categoria URGENTES - Avisos preventivos
- Health Factor < 1.5
- Distância Liquidação < 30%
- Score Risco < 50

### Validação confiabilidade

### 🔍 INTEGRIDADE (Código vs Doc)

Thresholds Preventivos Conformes:

- Health Factor: 1.5 (vs crítico 1.3) ✓
- Distância Liquidação: 30% (vs crítico 20%) ✓
- Score Risco: 50 (vs crítico 30) ✓

### Gaps Corretos - regras:

- HF: 0.2 diferença
- Distância: 10% diferença
- Score: 20 pontos diferença

### 🔧 MAPEAMENTO VISUAL DOS FLUXOS

´´´
FLUXO DEBUG (/alertas-debug/urgentes)
├── main.py
├── routers/
│   └── alertas_debug.py
│       └── debug_alertas_urgentes()
├── services/
│   └── alertas/
│       └── debug_service.py
│           └── debug_urgentes()
└── detectores/
    └── urgentes_detector.py
        └── get_debug_info()
            ├── get_dados_risco()              ← REUTILIZA CRÍTICOS
            ├── calcular_analise_risco()       ← REUTILIZA CRÍTICOS  
            ├── _extract_distance_value()      ← REUTILIZA CRÍTICOS
            └── _get_zona_risco()

FLUXO PRODUÇÃO (/api/v1/alertas/verificar)
├── main.py
├── routers/
│   └── alertas.py
│       └── verificar_alertas()
├── services/
│   └── alertas/
│       └── engine.py
│           └── verificar_todos_alertas()
└── detectores/
    └── urgentes_detector.py
        └── verificar_alertas()
            ├── get_dados_risco()              ← MESMA FUNÇÃO
            ├── calcular_analise_risco()       ← MESMA FUNÇÃO
            ├── _check_health_factor_urgente()
            │   └── _extract_distance_value()  ← MESMA FUNÇÃO
            ├── _check_distancia_liquidacao_urgente()
            │   └── _extract_distance_value()  ← MESMA FUNÇÃO
            └── _check_score_risco_urgente()
´´´
```Json
{
    "categoria": "URGENTES",
    "timestamp": "2025-06-08T06:59:36.577295",
    "finalidade": "Alertas preventivos antes dos críticos",
    "dados_coletados": {
        "health_factor": 2.800525,
        "dist_liquidacao": 64.292412,
        "score_risco": 95.0
    },
    "alertas_status": {
        "health_factor_urgente": {
            "valor_atual": 2.800525,
            "threshold": 1.5,
            "threshold_critico": 1.3,
            "zona": "SEGURA",
            "disparado": false,
            "acao": "✅ SEGURO: Sem ação necessária"
        },
        "distancia_liquidacao_urgente": {
            "valor_atual": 64.292412,
            "threshold": 30.0,
            "threshold_critico": 20.0,
            "zona": "SEGURA",
            "disparado": false,
            "acao": "✅ SEGURO: Margem confortável"
        },
        "score_risco_urgente": {
            "valor_atual": 95.0,
            "threshold": 50.0,
            "threshold_critico": 30.0,
            "zona": "SEGURA",
            "disparado": false,
            "acao": "✅ SEGURO: Risco controlado"
        }
    },
    "alertas_detectados": 0,
    "resumo_categoria": {
        "total_alertas_possiveis": 3,
        "alertas_disparados": 0,
        "funcao": "Aviso preventivo",
        "urgencia": "BAIXA"
    },
    "relacao_criticos": {
        "health_factor": {
            "urgente": 1.5,
            "critico": 1.3,
            "gap": 0.2
        },
        "dist_liquidacao": {
            "urgente": 30.0,
            "critico": 20.0,
            "gap": 10.0
        },
        "score_risco": {
            "urgente": 50.0,
            "critico": 30.0,
            "gap": 20.0
        }
    },
    "fontes_dados": {
        "dados_risco_ok": true,
        "analise_risco_ok": true,
        "reutilizacao_criticos": true
    }
}
```
´´´
---

## Alertas volatilidade
  
Debug categoria VOLATILIDADE - Timing e breakouts
- BBW < 10% por 5+ dias
- Volume spike > 200%
- ATR < 2.0%
- EMA144 > 15% + RSI > 65
- Pump & Drift detectado

## Validações 

### 🔍 INTEGRIDADE (Código vs Doc)
Thresholds Corrigidos Conformes:

- BBW: 10% (✓ 9.03% detectado, 9 dias consecutivos)
- Volume Spike: 200% (✓ -88% normal)
- ATR: 2.0% (✓ 2.43% normal)
- EMA+RSI: 15%/65 (✓ 9.22%/55.6 não disparado)
- Pump&Drift: 3% (✓ aguardando padrão)

### 🔍 CONFIABILIDAE (Debug vs Prod)

´´´
FLUXO DEBUG (/alertas-debug/volatilidade)
├── routers/alertas_debug.py
├── services/alertas/debug_service.py
└── detectores/volatilidade_detector.py
    └── get_debug_info()
        ├── fetch_ohlc_data()                    ← TradingView
        ├── calculate_bollinger_bands()          ← BBW Helper
        ├── obter_ema144_distance_atualizada()   ← EMA Helper
        ├── obter_rsi_diario()                   ← RSI Helper
        └── _count_consecutive_bbw_days_fixed()  ← Correção NaN

FLUXO PRODUÇÃO (/api/v1/alertas/verificar)
├── routers/alertas.py
├── services/alertas/engine.py
└── detectores/volatilidade_detector.py
    └── verificar_alertas()
        ├── _check_bbw_compressao_extrema()
        │   ├── fetch_ohlc_data()               ← MESMA FUNÇÃO
        │   ├── calculate_bollinger_bands()     ← MESMA FUNÇÃO
        │   └── _count_consecutive_bbw_days_fixed() ← MESMA FUNÇÃO
        ├── _check_volume_spike()
        ├── _check_atr_minimo_historico()
        ├── _check_ema_rsi_realizar()
        │   ├── obter_ema144_distance_atualizada() ← MESMA FUNÇÃO
        │   └── obter_rsi_diario()             ← MESMA FUNÇÃO
        └── _check_pump_and_drift()
´´´
```Json
{
    "categoria": "VOLATILIDADE",
    "timestamp": "2025-06-08T06:45:02.511335",
    "versao": "CORRIGIDA",
    "correcoes_aplicadas": [
        "BBW threshold: 5% → 10%",
        "Volume spike: 300% → 200%",
        "ATR threshold: 1.5% → 2.0%",
        "EMA+RSI: 20%/70 → 15%/65",
        "Pump&Drift: 5% → 3%",
        "ATR sem NaN",
        "BBW dias consecutivos corrigido"
    ],
    "dados_coletados": {
        "bbw_percentage": 9.02,
        "dias_bbw_baixo": 9,
        "volume_spike_percent": -88.9,
        "atr_percent": 2.43,
        "ema144_distance": 9.26,
        "rsi_diario": 55.7
    },
    "alertas_status": {
        "bbw_compressao": {
            "valor_atual": 9.02,
            "threshold": 10.0,
            "disparado": true,
            "acao": "Preparar capital dry powder"
        },
        "volume_spike": {
            "valor_atual": -88.9,
            "threshold": 200.0,
            "disparado": false,
            "acao": "Normal"
        },
        "atr_minimo": {
            "valor_atual": 2.43,
            "threshold": 2.0,
            "disparado": false,
            "acao": "Normal"
        },
        "ema_rsi_realizar": {
            "ema_distance": 9.26,
            "rsi_diario": 55.7,
            "threshold_ema": 15.0,
            "threshold_rsi": 65.0,
            "disparado": false,
            "acao": "Hold"
        },
        "pump_drift": {
            "disparado": false,
            "acao": "Aguardar padrão"
        }
    },
    "alertas_detectados": 1,
    "resumo_categoria": {
        "total_alertas_possiveis": 5,
        "alertas_disparados": 1,
        "urgencia": "ALTA"
    }
}
```
´´´
---

## Alertas Taticos

### Regras
- EMA144 < -8% + RSI < 40 (compra)",
- Score mercado > 70 + leverage baixo (aumentar)",
- EMA144 > 15% + 5 dias green (parcial)",
- Matriz tática breakout",
- DCA opportunity",
- Funding negativo + preço estável"

### 🔍 INTEGRIDADE (Código vs Doc)

Thresholds Conformes:

- Compra Desconto: EMA144 < -8% + RSI < 40 (9.16%/55.4% → não dispara) ✓
- Aumentar Posição: Score > 70 + leverage baixo (57.7 → não dispara) ✓
- Realização Parcial: EMA144 > 15% (9.16% → não dispara) ✓
- Funding Oportunidade: Disparado ✓
- DCA: Condições não atendidas ✓
- Breakout: Aguardando padrão ✓

### 🔍 CONFIABILIDAE (Debug vs Prod)

Mapeamento das funções:

´´´
FLUXO DEBUG (/alertas-debug/taticos)
├── routers/alertas_debug.py
├── services/alertas/debug_service.py
└── detectores/taticos_detector.py
    └── get_debug_info()
        ├── obter_ema144_distance_atualizada()   ← EMA Helper
        ├── obter_rsi_diario()                   ← RSI Helper  
        ├── calcular_analise_mercado()           ← Mercado Analysis
        └── get_dados_risco()                    ← Risk Data

FLUXO PRODUÇÃO (/api/v1/alertas/verificar)
├── routers/alertas.py
├── services/alertas/engine.py
└── detectores/taticos_detector.py
    └── verificar_alertas()
        ├── _check_compra_desconto()
        │   ├── obter_ema144_distance_atualizada() ← MESMA FUNÇÃO
        │   └── obter_rsi_diario()               ← MESMA FUNÇÃO
        ├── _check_aumentar_posicao()
        │   ├── calcular_analise_mercado()       ← MESMA FUNÇÃO
        │   └── get_dados_risco()               ← MESMA FUNÇÃO
        ├── _check_realizacao_parcial()
        ├── _check_funding_oportunidade()
        ├── _check_dca_opportunity()
        └── _check_breakout_confirmation()
´´´

```json
{
    "categoria": "TÁTICOS",
    "timestamp": "2025-06-08T07:40:11.208414",
    "finalidade": "Entradas/saídas específicas baseadas em confluências",
    "dados_coletados": {
        "ema144_distance": 9.16,
        "rsi_diario": 55.4,
        "score_mercado": 57.7,
        "alavancagem_atual": 1.39
    },
    "alertas_status": {
        "compra_desconto": {
            "disparado": false,
            "titulo": "Sem alerta",
            "acao": "Aguardar condições"
        },
        "aumentar_posicao": {
            "disparado": false,
            "titulo": "Sem alerta",
            "acao": "Aguardar condições"
        },
        "realizacao_parcial": {
            "disparado": false,
            "titulo": "Sem alerta",
            "acao": "Aguardar condições"
        },
        "funding_oportunidade": {
            "disparado": true,
            "titulo": "🔄 OPORTUNIDADE: Funding Negativo",
            "acao": "Manter posição - ser pago funding"
        },
        "dca_opportunity": {
            "disparado": false,
            "titulo": "Sem alerta",
            "acao": "Aguardar condições"
        },
        "breakout_confirmation": {
            "disparado": false,
            "titulo": "Sem alerta",
            "acao": "Aguardar condições"
        }
    },
    "alertas_detectados": 1,
    "resumo_categoria": {
        "total_alertas_possiveis": 6,
        "alertas_disparados": 1,
        "funcao": "Timing específico operações",
        "urgencia": "BAIXA"
    }
}
```
´´´
---