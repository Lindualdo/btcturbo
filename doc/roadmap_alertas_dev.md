# Sistema Alertas v5.0.8 - Roadmap Desenvolvimento

## 🎯 Estado Atual

**✅ Implementado:**
- Estrutura completa (Engine, Models, PostgreSQL)
- 5 alertas base com dados reais
- Endpoints básicos funcionando

**📍 Próximos Passos:**

## Fase 1: Endpoints Individuais (URGENTE)

### Criar 5 endpoints separados para uso imediato:

```python
# app/routers/alertas_individuais.py

@router.get("/alertas/health-factor-critico")
async def check_health_factor_critico():
    # Health Factor < 1.3
    
@router.get("/alertas/score-risco-critico") 
async def check_score_risco_critico():
    # Score < 30

@router.get("/alertas/health-factor-urgente")
async def check_health_factor_urgente():
    # Health Factor < 1.5

@router.get("/alertas/distancia-liquidacao")
async def check_distancia_liquidacao():
    # Dist < 30%

@router.get("/alertas/bbw-comprimido")
async def check_bbw_comprimido():
    # BBW < 5% há 7+ dias
```

**Retorno padrão:**
```json
{
  "alerta_ativo": true,
  "titulo": "🚨 HEALTH FACTOR CRÍTICO",
  "mensagem": "Health Factor 1.25 < 1.3 - Reduzir 70% AGORA",
  "valor_atual": 1.25,
  "threshold": 1.3,
  "acao_recomendada": "Reduzir 70% da posição",
  "timestamp": "2025-06-07T10:30:00Z"
}
```

## Fase 2: Completar Sistema com Mocks

### 2.1 Detectores Restantes (Mock)
```python
# mercado_detector.py
def verificar_alertas():
    return [
        mock_alerta("🔴 MVRV > 5", "Zona histórica de topo"),
        mock_alerta("⚠️ Score Mercado caiu 25pts", "Mudança drástica")
    ]

# tatico_detector.py  
def verificar_alertas():
    return [
        mock_alerta("💰 EMA144 +22% + RSI 75", "Realizar 40%"),
        mock_alerta("🛒 EMA144 -12% + RSI 35", "Adicionar 50%")
    ]

# onchain_detector.py
def verificar_alertas():
    return [
        mock_alerta("🐋 Baleias depositando 85%", "Pressão vendedora"),
        mock_alerta("🔄 Divergência preço/netflow", "Cuidado distribuição")
    ]
```

### 2.2 Helper Mock Centralizado
```python
# app/services/utils/helpers/alertas_mock_helper.py

ALERTAS_MOCK = {
    "mercado": [
        {"titulo": "🔴 TOPO ZONE", "msg": "MVRV 5.2 - Reduzir exposição", "prob": 0.1},
        {"titulo": "⚠️ MUDANÇA REGIME", "msg": "Score caiu 22pts em 24h", "prob": 0.3}
    ],
    "tatico": [
        {"titulo": "💰 REALIZAR", "msg": "EMA +22% RSI 75", "prob": 0.2},
        {"titulo": "🛒 COMPRAR", "msg": "EMA -12% RSI 35", "prob": 0.4}
    ],
    "onchain": [
        {"titulo": "🐋 BALEIAS", "msg": "85% whale ratio", "prob": 0.1},
        {"titulo": "📊 VOLUME SECO", "msg": "5 dias declinando", "prob": 0.6}
    ]
}

def gerar_alertas_mock(tipo: str, quantidade: int = 2):
    # Algoritmo: 70% chance nenhum, 30% chance alertas
```

## Fase 3: Frontend Dashboard

### 3.1 Widget Principal
```html
<!-- Usar widget já criado -->
app/templates/components/widget_alertas.html
```

### 3.2 Central Alertas (Nova Página)
```html
app/templates/alertas_central.html
- Timeline histórico
- Filtros por categoria  
- Ações (resolver, snooze)
- Configurações
```

## Fase 4: Substituir Mocks por Dados Reais

### 4.1 Implementar por prioridade:
1. **Mercado:** MVRV extremos, score changes
2. **Tático:** EMA+RSI matrix, pump&drift
3. **OnChain:** Whale flows, divergências

### 4.2 Padrão de desenvolvimento:
```python
# 1. Mock primeiro
def verificar_alertas_mock(): return []

# 2. Dados reais depois  
def verificar_alertas_real(): 
    # Usar helpers existentes
    # Seguir padrão posicao_detector.py
```

## Fase 5: Melhorias Avançadas

### 5.1 Sistema Notificações
- Webhook Telegram/Discord
- Email críticos
- Push notifications

### 5.2 Configurações Usuário
- Thresholds customizados
- Cooldowns por tipo
- Filtros pessoais

### 5.3 Machine Learning
- Pattern recognition alertas
- False positive reduction
- Confidence scoring

## 📂 Arquivos para Criar

**Imediato:**
- `app/routers/alertas_individuais.py`
- `app/services/utils/helpers/alertas_mock_helper.py`

**Médio prazo:**
- `app/templates/alertas_central.html`
- Completar detectores mercado/tatico/onchain

**Longo prazo:**
- Sistema notificações
- ML features

## 🔧 Comandos Úteis

```bash
# Testar alertas individuais
curl /api/alertas/health-factor-critico

# Gerar dados mock
python -c "from app.services.utils.helpers.alertas_mock_helper import gerar_mock; print(gerar_mock('mercado'))"

# Limpar alertas antigos
DELETE FROM alertas_historico WHERE timestamp < NOW() - INTERVAL '7 days';
```

## 🎯 Objetivos

**Sprint 1 (1-2 dias):** Endpoints individuais funcionando
**Sprint 2 (3-5 dias):** Sistema completo com mocks  
**Sprint 3 (1-2 semanas):** Substituir mocks por dados reais
**Sprint 4 (2-3 semanas):** Dashboard e melhorias

---

*Sistema modular, escalável e testável seguindo padrões estabelecidos.*