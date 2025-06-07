# API Alertas - Documentação

## Endpoints Principais

### 1. Verificar Alertas
```
GET /api/alertas/verificar
```
**Finalidade:** Executa detecção dos 5 alertas críticos e salva no banco
**Uso:** Chamar automaticamente ou manualmente para atualizar alertas
**Retorna:** Status da verificação + quantidade detectada

### 2. Resumo Widget
```
GET /api/alertas/resumo
```
**Finalidade:** Contadores para widget do dashboard
**Uso:** Dashboard principal - auto-refresh
**Retorna:** `{criticos: 2, urgentes: 4, volatilidade: 1, total: 7}`

### 3. Alertas Ativos
```
GET /api/alertas/ativos?categoria=critico&limit=10
```
**Finalidade:** Lista alertas não resolvidos
**Parâmetros:** `categoria`, `tipo`, `limit`
**Uso:** Central de alertas, listagem detalhada
**Retorna:** Array com título, mensagem, ação sugerida

### 4. Histórico
```
GET /api/alertas/historico?dias=7&incluir_resolvidos=true
```
**Finalidade:** Timeline de alertas passados
**Parâmetros:** `dias`, `incluir_resolvidos`, `tipo`
**Uso:** Análise histórica, debug
**Retorna:** Alertas dos últimos N dias

### 5. Resolver Alerta
```
POST /api/alertas/{id}/resolver
```
**Finalidade:** Marca alerta como resolvido
**Uso:** Usuário confirma que tomou ação
**Retorna:** Status da operação

### 6. Silenciar (Snooze)
```
POST /api/alertas/{id}/snooze?minutos=60
```
**Finalidade:** Pausa alerta por X minutos
**Uso:** Evitar spam de alertas já conhecidos
**Retorna:** Status + tempo até reativar

### 7. Health Check
```
GET /api/alertas/health
```
**Finalidade:** Status do sistema de alertas
**Uso:** Monitoramento, debug
**Retorna:** Última verificação, detectores funcionando

## 5 Alertas Implementados

### Críticos (🚨)
1. **Health Factor < 1.3** - Risco liquidação
2. **Score Risco < 30** - Posição extrema

### Urgentes (⚠️)
3. **Health Factor < 1.5** - Atenção necessária
4. **Distância Liquidação < 30%** - Margem apertando

### Volatilidade (⚡)
5. **BBW < 5% por 7+ dias** - Explosão iminente

## Fluxo Recomendado

1. **Dashboard:** `GET /resumo` (auto-refresh 5min)
2. **Detectar:** `GET /verificar` (manual ou cron)
3. **Detalhar:** `GET /ativos` (quando há alertas)
4. **Resolver:** `POST /{id}/resolver` (após ação)

## Exemplo Widget
```javascript
// Auto-refresh do widget
setInterval(async () => {
    const resumo = await fetch('/api/alertas/resumo').then(r => r.json());
    updateWidget(resumo);
}, 5 * 60 * 1000);
```