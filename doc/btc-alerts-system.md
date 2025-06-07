# Sistema de Alertas - BTC Hold Alavancado

## 🎯 Estrutura de Alertas por Categoria

### 1️⃣ ALERTAS DE POSIÇÃO (Proteção de Capital)

#### 🔴 Críticos - Ação Imediata
```python
# Risco de Liquidação
if health_factor < 1.3:
    alert("🚨 CRÍTICO: Health Factor {value} - Reduzir 70% AGORA")
    
if dist_liquidation < 20:
    alert("🚨 PERIGO: Liquidação em -{value}% - EMERGÊNCIA")
    
if score_risco < 30:
    alert("🚨 RISCO EXTREMO: Score {value} - Fechar posição")

# Circuit Breakers
if portfolio_loss_24h > 20:
    alert("🚨 STOP LOSS: Perda -{value}% em 24h - Avaliar saída")
    
if leverage_current > mvrv_max_leverage * 1.2:
    alert("🚨 OVERLEVERAGED: {current}x > {max}x permitido")
```

#### 🟡 Urgentes - Ação em 1-4h
```python
if health_factor < 1.5:
    alert("⚠️ ATENÇÃO: Health Factor baixo - Monitorar de perto")
    
if dist_liquidation < 30:
    alert("⚠️ CUIDADO: Margem apertando - Preparar redução")
    
if score_risco < 50:
    alert("⚠️ ALERTA: Posição ficando arriscada")
```

---

### 2️⃣ ALERTAS DE MERCADO (Análise Macro)

#### 🔴 Extremos de Mercado
```python
# Indicadores de Topo
if mvrv_z > 5:
    alert("🔴 TOPO ZONE: MVRV Z-Score {value} - Reduzir exposição")
    
if rsi_weekly > 75 and rsi_daily > 75:
    alert("🔴 EUFORIA: RSI extremo em múltiplos timeframes")
    
if funding_rate_7d > 0.15:
    alert("🔴 SUPERAQUECIDO: Funding {value}% - Correção iminente")

# Indicadores de Fundo
if mvrv_z < 0:
    alert("🟢 OPORTUNIDADE: MVRV negativo - Zona de acumulação")
    
if sth_sopr < 0.87:
    alert("🟢 CAPITULAÇÃO: Novatos vendendo no loss extremo")
```

#### 🟡 Mudanças de Regime
```python
if score_mercado_change_24h > 20:
    alert("⚠️ MUDANÇA DRÁSTICA: Score {before}→{after} em 24h")
    
if ema_cross_detected:
    alert("⚠️ EMA CROSS: {type} em formação - Possível reversão")
    
if volume_spike > 300:
    alert("⚠️ VOLUME SPIKE: {value}% acima da média")
```

---

### 3️⃣ ALERTAS DE VOLATILIDADE (Timing)

### Alertas (5):
1. BBW < 10% por 5+ dias → "🔥 EXPLOSÃO IMINENTE"
2. Volume spike > 200% → "⚡ VOLUME SPIKE"
3. ATR < 2% → "🔥 ATR MÍNIMO"
4. EMA144 > 15% + RSI > 65 → "💰 ZONA REALIZAÇÃO"
5. Pump & Drift detectado → "📊 PUMP & DRIFT"


#### 🟡 Padrões de Movimento
```python
# Pump & Drift (insight do usuário)
if price_change_24h > 5 and lateral_days >= 2:
    alert("📊 PUMP & DRIFT: Correção 50% provável nas próximas 48h")
    
if consecutive_doji_candles > 3:
    alert("📊 INDECISÃO: {days} dias de Doji - Decisão próxima")
    
if volume_down_days > 5:
    alert("📊 VOLUME SECO: Preparar para movimento direcional")
```

---

### 4️⃣ ALERTAS TÁTICOS (Execução)

#### 🎯 Pontos de Entrada/Saída
```python
# Realizações
if ema144_distance > 20 and rsi_daily > 70:
    alert("💰 REALIZAR: EMA +{ema}% com RSI {rsi} - Tomar 40%")
    
if ema144_distance > 15 and consecutive_green_days > 5:
    alert("💰 PARCIAL: Rally estendido - Considerar realização 25%")

# Compras
if ema144_distance < -8 and rsi_daily < 40:
    alert("🛒 COMPRA: Desconto -{ema}% com RSI {rsi} - Adicionar")
    
if score_mercado > 70 and leverage < max_leverage * 0.7:
    alert("🛒 AUMENTAR: Espaço para leverage - Score {score}")
```

---

### 5️⃣ ALERTAS ON-CHAIN (Smart Money)

#### 🐋 Movimentos de Baleias
```python
if exchange_whale_ratio > 85:
    alert("🐋 BALEIAS DEPOSITANDO: {value}% das transações")
    
if dormancy_flow > 500000:
    alert("🐋 DISTRIBUIÇÃO: HODLers antigos movimentando")
    
if miners_to_exchanges > threshold:
    alert("⛏️ MINERADORES VENDENDO: Pressão adicional")
```

#### 📊 Divergências On-Chain
```python
if price_up and netflow_positive:
    alert("🔄 DIVERGÊNCIA: Preço subindo mas BTC entrando em exchanges")
    
if funding_negative and price_stable:
    alert("🔄 OPORTUNIDADE: Funding negativo com preço estável")
```

---

## 📱 Dashboard de Alertas

```
┌────────────────────────────────────────────────────────────┐
│ CENTRAL DE ALERTAS            🔴 2  🟡 4  🟢 1  ⚡ 3       │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ ┌──────────────────────────────────────────────────────┐  │
│ │ 🚨 CRÍTICOS (2)                          [EXPANDIR]  │  │
│ ├──────────────────────────────────────────────────────┤  │
│ │ • Health Factor 1.42 - Reduzir posição              │  │
│ │   [Ver Detalhes] [Simular Redução] [Executar]       │  │
│ │                                                      │  │
│ │ • MVRV > 5.2 - Zona de topo histórica              │  │
│ │   [Análise] [Histórico] [Estratégia Saída]         │  │
│ └──────────────────────────────────────────────────────┘  │
│                                                            │
│ ┌──────────────────────────────────────────────────────┐  │
│ │ ⚡ VOLATILIDADE (3)                      [EXPANDIR]  │  │
│ ├──────────────────────────────────────────────────────┤  │
│ │ • 🔥 BBW 4.8% há 9 dias - EXPLOSÃO IMINENTE        │  │
│ │   Histórico: Últimas 5 ocorrências = +/-15% avg    │  │
│ │   [Preparar Capital] [Definir Stops] [Ignorar 24h] │  │
│ │                                                      │  │
│ │ • 📊 Volume -70% (3 dias) - Breakout próximo       │  │
│ │ • 📊 Pump & Drift detectado - Correção em 48h      │  │
│ └──────────────────────────────────────────────────────┘  │
│                                                            │
│ ┌──────────────────────────────────────────────────────┐  │
│ │ TIMELINE DE ALERTAS                                 │  │
│ ├──────────────────────────────────────────────────────┤  │
│ │ 14:32 │ ⚡ BBW compressão extrema                   │  │
│ │ 13:45 │ 🟡 Score mercado caiu 8 pontos            │  │
│ │ 11:20 │ 🟢 RSI oversold em timeframe 4H           │  │
│ │ 09:15 │ 🔴 Health Factor atravessou 1.5           │  │
│ │ 08:00 │ 📊 Relatório diário gerado               │  │
│ └──────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────┘
```

---

## ⚙️ Configuração de Alertas

### Prioridades e Notificações
```python
PRIORIDADE_CONFIG = {
    "CRITICO": {
        "notificacao": ["push", "email", "sms"],
        "som": "alarme.mp3",
        "repeticao": "5min até ação",
        "cor": "vermelho"
    },
    "URGENTE": {
        "notificacao": ["push", "email"],
        "som": "alert.mp3",
        "repeticao": "30min",
        "cor": "amarelo"
    },
    "VOLATILIDADE": {
        "notificacao": ["push"],
        "som": "ping.mp3",
        "repeticao": "1x",
        "cor": "roxo"
    },
    "INFORMATIVO": {
        "notificacao": ["dashboard"],
        "som": None,
        "repeticao": None,
        "cor": "azul"
    }
}
```

### Filtros Personalizados
```python
# Usuario pode configurar
FILTROS = {
    "ignorar_pequenas_variacoes": True,  # < 3%
    "agrupar_similares": True,           # Mesmo tipo em 1h
    "modo_silencioso": {
        "inicio": "23:00",
        "fim": "07:00",
        "exceto": ["CRITICO"]
    },
    "cooldown_por_tipo": {
        "volatilidade": "4h",
        "mercado": "2h",
        "tatico": "1h"
    }
}
```

---

## 📊 Widget Resumo para Dashboard Principal

```
┌─────────────────────────┐
│ 🔔 ALERTAS ATIVOS       │
├─────────────────────────┤
│ 🔴 Críticos:        2   │
│ ⚡ Volatilidade:    3   │
│ 🟡 Atenção:        4   │
│ 🟢 Oportunidade:   1   │
├─────────────────────────┤
│ Próxima ação:          │
│ "Reduzir 25% se        │
│  EMA144 > 20%"         │
│                         │
│ [Central Completa →]    │
└─────────────────────────┘
```

---

## 🔄 Regras de Negócio

### Hierarquia de Alertas
1. **Proteção sempre prevalece**: Alertas de risco sobrepõem oportunidades
2. **Volatilidade é informativa**: Não gera ação automática, apenas preparação
3. **Confirmação em críticos**: Requer confirmação manual para executar

### Inteligência de Alertas
```python
# Evita spam
if similar_alert_last_hour:
    skip_or_group()
    
# Contextualiza
if alert_type == "volatilidade" and position == 0:
    modify_message("Oportunidade de entrada após breakout")
    
# Aprende padrões
if user_ignored_last_5_similar:
    reduce_priority()
```

---

## 📈 Métricas de Eficácia

Dashboard deve trackear:
- Taxa de acerto por tipo de alerta
- Tempo médio de resposta do usuário  
- Alertas mais ignorados (revisar threshold)
- Correlação alerta → resultado

---

* Sistema de Alertas v2.0 - Independente dos Scores*
* Foco em timing, proteção e oportunidades*
* Scores dizem "se", alertas dizem "quando"