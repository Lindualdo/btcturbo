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