# Sistema Unificado de Decisões - BTC Hold Alavancado

## 🎯 Função Principal de Decisão

```python
def decisao_unificada(dados):
    """
    Retorna decisão única e clara com base em hierarquia de prioridades
    """
    
    # 1. DEFESA CRÍTICA (Override tudo)
    if dados['score_risco'] < 30:
        return {
            'acao': 'FECHAR_TUDO',
            'tamanho': 100,
            'urgencia': 'IMEDIATA',
            'motivo': 'Risco crítico - proteção capital'
        }
    
    if dados['score_risco'] < 50:
        return {
            'acao': 'REDUZIR',
            'tamanho': 70,
            'urgencia': 'URGENTE',
            'motivo': 'Risco elevado'
        }
    
    if dados['alavancagem_atual'] > dados['max_permitida']:
        excesso = calcular_percentual_excesso(dados)
        return {
            'acao': 'REDUZIR',
            'tamanho': excesso,
            'urgencia': 'ALTA',
            'motivo': f'Overleveraged: {dados["alavancagem_atual"]}x > {dados["max_permitida"]}x'
        }
    
    if dados['score_mercado'] < 40:
        return {
            'acao': 'REDUZIR',
            'tamanho': 50,
            'urgencia': 'MEDIA',
            'motivo': 'Mercado desfavorável'
        }
    
    # 2. CENÁRIOS ESPECÍFICOS (8 cenários definidos)
    cenario = identificar_cenario(dados)
    if cenario:
        return cenario['acao']
    
    # 3. MATRIZ TÁTICA EMA/RSI (Fallback)
    return decisao_tatica(dados)
```

## 📊 Cenários Completos Unificados

### 🛡️ DEFESA (Prioridade Máxima)

| Condição | Ação | Tamanho | Urgência | Stop Loss |
|----------|------|---------|----------|-----------|
| Score Risco < 30 | FECHAR | 100% | IMEDIATA | - |
| Score Risco < 50 | REDUZIR | 70% | URGENTE | -5% |
| Alavancagem > Max | REDUZIR | Excesso | ALTA | -8% |
| Score Mercado < 40 | REDUZIR | 50% | MÉDIA | -10% |
| Health Factor < 1.3 | REDUZIR | 80% | IMEDIATA | - |

### 📈 OPORTUNIDADES (Todos filtros OK)

#### Cenário: Correção em Bull
```python
condições = {
    'score_mercado': [60, 70],
    'score_risco': > 70,
    'mvrv': [2.0, 2.8],
    'timeframe_4h': {
        'ema_distance': [-2, +2],
        'rsi': [35, 45]
    },
    'estrutura_maior': 'alinhada_bullish'
}

acao = {
    'decisao': 'ADICIONAR',
    'tamanho': 30,
    'urgencia': 'MEDIA',
    'stop_loss': -8,
    'target': '+15% ou RSI > 65',
    'justificativa': 'Pullback saudável em tendência'
}
```

#### Cenário: Início Bull Market
```python
condições = {
    'score_mercado': > 70,
    'score_risco': > 80,
    'mvrv': < 1.5,
    'ema_distance': [-5, +5],
    'rsi_diario': [40, 60]
}

acao = {
    'decisao': 'ADICIONAR',
    'tamanho': 50,
    'urgencia': 'ALTA',
    'alavancagem_alvo': 2.5,
    'stop_loss': -12,
    'justificativa': 'Setup histórico de fundo'
}
```

#### Cenário: Bull Maduro
```python
condições = {
    'score_mercado': [65, 75],
    'mvrv': > 2.5,
    'ema_distance': > 15,
    'rsi_diario': > 65
}

acao = {
    'decisao': 'REALIZAR',
    'tamanho': 25,
    'urgencia': 'BAIXA',
    'justificativa': 'Tomada de lucro em alta'
}
```

### 🎯 MATRIZ TÁTICA UNIFICADA

| Situação | EMA144 | RSI | Timeframe | Ação | Tamanho | Justificativa |
|----------|---------|-----|-----------|------|---------|---------------|
| **COMPRAS** |
| Capitulação | < -10% | < 30 | Diário | ADICIONAR | 75% | Extremo histórico |
| Correção Forte | -10 a -5% | < 45 | Diário | ADICIONAR | 35% | Desconto significativo |
| Pullback 4H | -2 a +2% | < 45 | 4H | ADICIONAR | 30% | Correção em tendência |
| Teste Suporte | -5 a 0% | 40-50 | Diário | ADICIONAR | 20% | Suporte confirmado |
| **REALIZAÇÕES** |
| Extremo | > +20% | > 70 | Diário | REALIZAR | 40% | Sobrecomprado extremo |
| Esticado | +15 a +20% | > 65 | Diário | REALIZAR | 25% | Tomada de lucro |
| Moderado | +10 a +15% | > 60 | Diário | REALIZAR | 10% | Realização tática |
| Rally 4H | > +5% | > 70 | 4H | REALIZAR | 15% | Momentum curto prazo |
| **NEUTRO** |
| Zona Neutra | -5 a +10% | 45-60 | Qualquer | HOLD | 0% | Aguardar sinal |

## 🚨 Sistema de Alertas Integrado

### Alertas de Entrada
```python
# Pullback 4H em tendência diária
if daily_trend == 'bullish' and h4_rsi < 40 and ema_4h_distance < 2:
    alert("🎯 SETUP 4H: Pullback em tendência - ADICIONAR")

# Correção semanal mantida
if weekly_ath_streak >= 4 and daily_correction > 8:
    alert("💎 CORREÇÃO EM ATH SEMANAL: Oportunidade rara")
```

### Alertas de Saída
```python
# Realização em força
if ema_distance > 15 and rsi > 65 and consecutive_green > 5:
    alert("💰 REALIZAR: 5 dias de alta + RSI alto")

# Divergência
if price_new_high and rsi < previous_high_rsi:
    alert("⚠️ DIVERGÊNCIA: Considerar realização")
```

## 📊 Função de Decisão Detalhada

```python
def obter_decisao_completa(dados_mercado, dados_posicao):
    # Fase do mercado
    fase = determinar_fase_mvrv(dados_mercado['mvrv'])
    
    # Verificações de segurança
    if not passar_filtros_seguranca(dados_posicao):
        return decisao_defesa(dados_posicao)
    
    # Verificar múltiplos timeframes
    setup_4h = verificar_setup_4h(dados_mercado)
    if setup_4h['valido']:
        return {
            'acao': 'ADICIONAR',
            'tamanho': 30,
            'timeframe': '4H',
            'motivo': 'Pullback em tendência maior',
            'stop': -5,
            'target': 'EMA144 4H +5%'
        }
    
    # Aplicar matriz principal
    return aplicar_matriz_tatica(dados_mercado, fase)
```

## 🎯 Quick Decision Framework

```
1. RISCO < 50? → SAIR
2. OVERLEVERAGED? → REDUZIR
3. MERCADO < 40? → REDUZIR 50%
4. PULLBACK 4H DETECTADO? → ADICIONAR 30%
5. EMA > 15% + RSI > 65? → REALIZAR 25%
6. RESTO → HOLD
```

## 📈 Fases de Mercado (MVRV)

| MVRV | Fase | Max Alavancagem | Viés |
|------|------|-----------------|------|
| < 1.0 | Bottom | 3.0x | Compra agressiva |
| 1.0-2.0 | Acumulação | 2.5x | Compra moderada |
| 2.0-3.0 | Bull Médio | 2.0x | Hold/Realização tática |
| > 3.0 | Topo | 1.5x | Realização/Proteção |

---

*Sistema Unificado v1.0 - Decisões claras e hierárquicas*