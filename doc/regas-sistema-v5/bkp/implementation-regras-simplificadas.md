# Simplificação usando Dashboard Atual:

## 1. Tela Principal - Adicionar Widget
┌─────────────────────────────┐
│ 💡 DECISÃO DO DIA          │
│                             │
│ [COMPRAR 30%] ✅           │
│ "Pullback 4H detectado"     │
│                             │
│ Confiança: ⭐⭐⭐⭐         │
│ Executar até: 18:00         │
└─────────────────────────────┘

## 2. Criar "Modo Simplificado"
Toggle no header para alternar entre:

- Modo Completo: Todos os scores e detalhes
- Modo Simples: Só decisão + confiança

## 3. Sistema de Confiança

- ⭐⭐⭐⭐⭐ = Todos indicadores alinhados
- ⭐⭐⭐ = Maioria alinhada
- ⭐ = Sinal fraco, opcional

## Tarefas para Desenvolvimento:

### Fase 1 - Backend

- Criar endpoint /decisao-simplificada
- Adicionar lógica de confiança
- Implementar detecção pullback 4H

### Fase 2 - Frontend

- Widget decisão na home
- Toggle modo simples/completo
- Histórico de decisões tomadas

### Fase 3 - Alertas

- Webhook quando decisão muda
- Push notification mobile
- Email resumo semanal

### Fase 4 - Tracking

- Log decisões executadas vs ignoradas
- Taxa de acerto por nível confiança
- Ajuste automático de parâmetros

Mantém sistema completo mas adiciona camada de simplicidade por cima.Tentar novamenteASe essas regras que definimos, onde entrará aqui?EditarAs regras entram no endpoint /decisao-simplificada:

```python
def decisao_simplificada():
    # 1. Aplica hierarquia
    if score_risco < 50:
        return "REDUZIR 70%"
    
    # 2. Verifica cenários (8 definidos)
    if detectar_pullback_4h():
        return "COMPRAR 30%"
    
    # 3. Matriz EMA/RSI
    if ema_distance > 15 and rsi > 65:
        return "VENDER 15%"
    
    # 4. Default
    return "MANTER"
```

O backend já tem todas as regras implementadas. O widget só mostra o resultado final com confiança baseada em quantos indicadores concordam com a decisão.Tentar novamenteO Claude pode cometer erros. Confira sempre as respostas.