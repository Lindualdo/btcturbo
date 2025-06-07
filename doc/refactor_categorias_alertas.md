# Refatoração Sistema Alertas - Categorias DOC

## Estrutura Atual (Confusa)
```
TipoAlerta: POSICAO, VOLATILIDADE, MERCADO
CategoriaAlerta: CRITICO, URGENTE, INFORMATIVO
```

## Nova Estrutura (DOC)
```
CategoriaAlerta: CRITICOS, URGENTES, VOLATILIDADE, TATICOS, ONCHAIN
PrioridadeInterna: 0=crítico, 1=urgente, 2=informativo
```

---

## 🔴 CATEGORIA: CRÍTICOS
**Detector:** `CriticosDetector`
**Finalidade:** Proteção imediata de capital

### Alertas (5):
1. Health Factor < 1.3 → "🚨 CRÍTICO: Reduzir 70% AGORA"
2. Distância Liquidação < 20% → "🚨 PERIGO: EMERGÊNCIA"  
3. Score Risco < 30 → "🚨 RISCO EXTREMO: Fechar posição"
4. Portfolio Loss 24h > 20% → "🚨 STOP LOSS: Avaliar saída"
5. Leverage > MVRV Max * 1.2 → "🚨 OVERLEVERAGED"

---

## 🟡 CATEGORIA: URGENTES  
**Detector:** `UrgentesDetector`
**Finalidade:** Aviso antes dos críticos

### Alertas (3):
1. Health Factor < 1.5 → "⚠️ ATENÇÃO: Monitorar de perto"
2. Distância Liquidação < 30% → "⚠️ CUIDADO: Preparar redução"
3. Score Risco < 50 → "⚠️ ALERTA: Posição arriscada"

---

## ⚡ CATEGORIA: VOLATILIDADE
**Detector:** `VolatilidadeDetector` 
**Finalidade:** Timing e breakouts

### Alertas (5):
1. BBW < 5% por 7+ dias → "🔥 EXPLOSÃO IMINENTE"
2. Volume spike > 300% → "⚡ VOLUME SPIKE"
3. ATR < 1.5% → "🔥 ATR MÍNIMO"
4. EMA144 > 20% + RSI > 70 → "💰 ZONA REALIZAÇÃO"
5. Pump & Drift detectado → "📊 PUMP & DRIFT"

---

## 📊 CATEGORIA: TÁTICOS
**Detector:** `TaticosDetector`
**Finalidade:** Entradas/saídas específicas

### Alertas (6):
1. EMA144 < -8% + RSI < 40 → "🛒 COMPRA: Desconto + oversold"
2. Score mercado > 70 + leverage < max*0.7 → "🛒 AUMENTAR: Espaço para leverage"
3. EMA144 > 15% + 5 dias green → "💰 PARCIAL: Rally estendido"
4. Matriz tática breakout → "🎯 ENTRADA/SAÍDA"
5. DCA opportunity → "💎 ACUMULAÇÃO"
6. Funding negativo + preço estável → "🔄 OPORTUNIDADE"

---

## 🐋 CATEGORIA: ONCHAIN
**Detector:** `OnchainDetector`
**Finalidade:** Smart money movements

### Alertas (5):
1. Exchange whale ratio > 85% → "🐋 BALEIAS DEPOSITANDO"
2. Dormancy flow > 500k → "🐋 DISTRIBUIÇÃO: HODLers antigos"
3. Miners to exchanges > threshold → "⛏️ MINERADORES VENDENDO"
4. Divergência preço vs netflow → "🔄 DIVERGÊNCIA"
5. Funding negativo + preço estável → "🔄 OPORTUNIDADE"

---

## Implementação

### Models
```python
class CategoriaAlerta(str, Enum):
    CRITICOS = "criticos"
    URGENTES = "urgentes" 
    VOLATILIDADE = "volatilidade"
    TATICOS = "taticos"
    ONCHAIN = "onchain"

class AlertaCreate(BaseModel):
    categoria: CategoriaAlerta
    prioridade: int  # 0=crítico, 1=urgente, 2=info
    titulo: str
    mensagem: str
    # ...
```

### Engine
```python
self.detectores = {
    CategoriaAlerta.CRITICOS: CriticosDetector(),
    CategoriaAlerta.URGENTES: UrgentesDetector(), 
    CategoriaAlerta.VOLATILIDADE: VolatilidadeDetector(),
    CategoriaAlerta.TATICOS: TaticosDetector(),
    CategoriaAlerta.ONCHAIN: OnchainDetector()
}
```

### Debug Endpoints
```
/alertas-debug/criticos      # Health Factor, Score Risco, etc
/alertas-debug/urgentes      # Avisos antes dos críticos
/alertas-debug/volatilidade  # BBW, Volume, ATR
/alertas-debug/taticos       # Matriz tática, DCA
/alertas-debug/onchain       # Baleias, divergências
/alertas-debug/geral         # Overview todas categorias
```

### Resumo Widget
```json
{
  "criticos": 2,
  "urgentes": 1, 
  "volatilidade": 0,
  "taticos": 3,
  "onchain": 1,
  "total_ativos": 7
}
```

---

## Migração

### Fase 1: Renomear atual
- `PosicaoDetector` → `CriticosDetector`
- Manter `VolatilidadeDetector`

### Fase 2: Implementar faltantes  
- `UrgentesDetector` (3 alertas)
- `TaticosDetector` (6 alertas)
- `OnchainDetector` (5 alertas)

### Fase 3: Atualizar endpoints
- Models, Engine, Debug Service
- Routers seguem categorias DOC

**Total:** 24 alertas em 5 categorias claras