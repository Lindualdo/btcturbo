# Roadmap BTC TURBO 5.0:
## Fase 1 - 5 alertas criticos 
### MVP Simples

```python
- Webhook para Telegram/Discord
- 5 alertas críticos:
  - Health Factor < 1.5
  - BBW < 5% por 7 dias  
  - Score mudou 20+ pontos
  - EMA144 > 20% com RSI > 70
  - MVRV > 3.5
```

### Quick Win - Alerta Telegram em 1 dia:

```python
def check_alerts():
    if health_factor < 1.5:
        telegram_send("🚨 HF baixo: {health_factor}")
    
    if bbw < 5 and days_compressed > 7:
        telegram_send("🔥 BBW: Explosão iminente")
```

## Fase 2: Dashboard

- Página única com:
  - Scores atuais
  - Posição/alavancagem
  - Últimos 10 alertas
  - Gráfico básico

## Fase 3: Backtest

- Mais complexo
- Precisa dados históricos
- Validação do sistema

## 1 - Dashboard Principal - Vista Rápida

´´´
┌─────────────────────────────────────────────────────┐
│ INDICADORES CRÍTICOS           [Expandir Detalhes →] │
├─────────────────────────────────────────────────────┤
│ 📊 BBW: 7.2% (Normal)         ⚡ Próx: < 5%        │
│ 📈 MVRV: 2.24 (Bull Médio)    Max Lev: 2.0x        │
│ 💰 Funding: 0.042% (Neutro)   7D: 0.031%           │
└─────────────────────────────────────────────────────┘
´´´
## 2 - Nas Camadas - Abordagem Híbrida

´´´
SCORE MERCADO: 55.9 ▼
├── Ciclo: 5.5/10  [Ver detalhes ▼]
│   └── MVRV: 2.24 | RPR: 2.1 | Puell: 1.3
├── Momentum: 6.2/10 [Ver detalhes ▼]
│   └── RSI: 52 | Funding: 0.042% | SOPR: 1.02
└── Técnico: 5.8/10 [Ver detalhes ▼]
    └── EMAs: OK | BBW: 7.2% (Normal)
´´´

## Camada 1 - Mercado: Mostrar ambos
´´´
SCORE MERCADO: 55.9 ▼
├── Ciclo: 5.5/10  [Ver detalhes ▼]
│   └── MVRV: 2.24 | RPR: 2.1 | Puell: 1.3
├── Momentum: 6.2/10 [Ver detalhes ▼]
│   └── RSI: 52 | Funding: 0.042% | SOPR: 1.02
└── Técnico: 5.8/10 [Ver detalhes ▼]
    └── EMAs: OK | BBW: 7.2% (Normal)
´´´

## Camada 4 - Execução: Sempre visível
´´´
EXECUÇÃO TÁTICA
├── EMA144: +9.0% ━━━━━━━|━━━━━━━━ (+20%)
├── RSI: 52 ━━━━━━━━|━━━━━━━━ (70)
├── BBW: 7.2% [Normal - Sem alerta]
└── Decisão: HOLD
´´´

## 3. Widget Flutuante (Sempre Visível)
´´´
┌──────────────┐
│ ⚡ TIMING    │
│ BBW: 7.2% ⬇ │
│ MVRV: 2.24   │
│ Fund: 0.04%  │
└──────────────┘
´´´