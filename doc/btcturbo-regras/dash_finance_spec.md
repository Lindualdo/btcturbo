# Dashboard Finance - Especificação Técnica

## 1. VISÃO GERAL

Dashboard para visualização de históricos financeiros do sistema BTC Turbo:
- Health Factor histórico
- Alavancagem atual vs permitida
- Crescimento patrimônio líquido
- Evolução capital investido

**Princípio**: Apenas consultas de dados existentes, sem gravar novos dados.

## 2. ARQUITETURA

```
app/services/dashboards/
├── dash_finance_service.py          # Service principal (GET endpoints)
└── dash_finance/
    └── queries_helper.py            # Queries por indicador
```

**Router**: Adicionar endpoints em `app/routers/dashboards.py`

## 3. ENDPOINTS

### 3.1 Estrutura
```
GET /api/v1/dash-finance/health-factor?periodo=30d
GET /api/v1/dash-finance/alavancagem?periodo=30d
GET /api/v1/dash-finance/patrimonio?periodo=30d
GET /api/v1/dash-finance/capital-investido?periodo=30d
```

### 3.2 Filtros Suportados
- `30d` - Últimos 30 dias
- `3m` - Últimos 3 meses
- `6m` - Últimos 6 meses
- `1y` - Último ano
- `all` - Todos os dados

### 3.3 Formato Resposta
```json
{
  "status": "success",
  "indicador": "health_factor",
  "periodo": "30d",
  "dados": [
    {"timestamp": "2025-06-24T17:00:00Z", "valor": 2.88},
    {"timestamp": "2025-06-24T16:00:00Z", "valor": 2.92}
  ],
  "total_registros": 720
}
```

## 4. FONTES DE DADOS

| Indicador | Tabela | Campo | Observações |
|-----------|--------|-------|-------------|
| Health Factor | `indicadores_risco` | `health_factor` | Direto |
| Alavancagem Atual | `dash_main` | `alavancagem_atual` | Após migração |
| Alavancagem Permitida | `dash_main` | `alavancagem_permitida` | Novo campo |
| Patrimônio | `indicadores_risco` | `net_asset_value` | Capital líquido |
| Capital Investido | `indicadores_risco` | `supplied_asset_value` | Posição total |

## 5. MIGRAÇÃO ALAVANCAGEM PERMITIDA

### 5.1 Criar Campo
```sql
ALTER TABLE dash_main 
ADD COLUMN alavancagem_permitida DECIMAL(3,1),
ADD COLUMN alavancagem_atual DECIMAL(3,1);
```

### 5.2 Migração Dados Existentes
```sql
-- Alavancagem permitida do JSON
UPDATE dash_main 
SET alavancagem_permitida = (alavancagem_json->'alavancagem'->'permitida')::decimal
WHERE alavancagem_permitida IS NULL;

-- Alavancagem atual do JSON  
UPDATE dash_main 
SET alavancagem_atual = (alavancagem_json->'alavancagem'->'atual')::decimal
WHERE alavancagem_atual IS NULL;
```

### 5.3 Alterar Gravação
**Arquivo**: `app/services/dashboards/dash_main/helpers/data_builder.py`

```python
# Adicionar campos na função build_dashboard_data()
campos = {
    # ... campos existentes
    "alavancagem_atual": dados_alavancagem["alavancagem"]["atual"],
    "alavancagem_permitida": dados_alavancagem["alavancagem"]["permitida"]
}
```

## 6. QUERIES OTIMIZADAS

**REGRA**: Dados gerados a cada hora - usar sempre último registro de cada dia.

### 6.1 Health Factor
```sql
SELECT 
    DATE(timestamp) as data,
    timestamp,
    health_factor as valor
FROM indicadores_risco r1
WHERE timestamp >= %s
  AND timestamp = (
    SELECT MAX(timestamp) 
    FROM indicadores_risco r2 
    WHERE DATE(r1.timestamp) = DATE(r2.timestamp)
  )
ORDER BY timestamp DESC;
```

### 6.2 Alavancagem
```sql
SELECT 
    DATE(timestamp) as data,
    timestamp,
    alavancagem_atual as atual,
    alavancagem_permitida as permitida
FROM dash_main d1
WHERE timestamp >= %s
  AND timestamp = (
    SELECT MAX(timestamp) 
    FROM dash_main d2 
    WHERE DATE(d1.timestamp) = DATE(d2.timestamp)
  )
ORDER BY timestamp DESC;
```

### 6.3 Patrimônio
```sql
SELECT 
    DATE(timestamp) as data,
    timestamp,
    net_asset_value as valor
FROM indicadores_risco r1
WHERE timestamp >= %s
  AND timestamp = (
    SELECT MAX(timestamp) 
    FROM indicadores_risco r2 
    WHERE DATE(r1.timestamp) = DATE(r2.timestamp)
  )
ORDER BY timestamp DESC;
```

### 6.4 Capital Investido  
```sql
SELECT 
    DATE(timestamp) as data,
    timestamp,
    supplied_asset_value as valor
FROM indicadores_risco r1
WHERE timestamp >= %s
  AND timestamp = (
    SELECT MAX(timestamp) 
    FROM indicadores_risco r2 
    WHERE DATE(r1.timestamp) = DATE(r2.timestamp)
  )
ORDER BY timestamp DESC;
```

## 7. IMPLEMENTAÇÃO

### 7.1 Service Principal
```python
# dash_finance_service.py
def obter_health_factor(periodo: str) -> dict:
    """Retorna histórico health factor"""
    
def obter_alavancagem(periodo: str) -> dict:
    """Retorna histórico alavancagens atual/permitida"""
    
def obter_patrimonio(periodo: str) -> dict:
    """Retorna evolução patrimônio líquido"""
    
def obter_capital_investido(periodo: str) -> dict:
    """Retorna evolução capital investido"""
```

### 7.2 Helper Queries
```python
# queries_helper.py
def get_health_factor_history(periodo: str) -> list:
def get_alavancagem_history(periodo: str) -> list:
def get_patrimonio_history(periodo: str) -> list:
def get_capital_history(periodo: str) -> list:
def convert_periodo_to_date(periodo: str) -> datetime:
```

### 7.3 Router
```python
# dashboards.py
@router.get("/dash-finance/health-factor")
async def get_health_factor(periodo: str = "30d"):
    return obter_health_factor(periodo)
```

## 8. VALIDAÇÕES

### 8.1 Período
- Validar formato (30d, 3m, 6m, 1y, all)
- Default: 30d se inválido

### 8.2 Dados
- Tratar registros NULL
- Ordenar por timestamp DESC
- Limitar resultados se necessário

### 8.3 Erros
```python
# Fallback padrão
return {
    "status": "error", 
    "erro": str(e),
    "dados": []
}
```

## 9. LOGS

```python
logger.info(f"🔍 Consultando {indicador} - período: {periodo}")
logger.info(f"✅ {len(dados)} registros encontrados")
logger.error(f"❌ Erro consulta {indicador}: {str(e)}")
```

## 10. TESTES

### 10.1 Endpoints
```bash
GET /api/v1/dash-finance/health-factor?periodo=30d
GET /api/v1/dash-finance/alavancagem?periodo=3m  
GET /api/v1/dash-finance/patrimonio?periodo=all
```

### 10.2 Validação
- Verificar formato timestamp
- Confirmar valores numéricos
- Testar todos os períodos

## 11. PRÓXIMOS PASSOS

1. ✅ Migração campo alavancagem_permitida
2. ✅ Implementar queries_helper.py
3. ✅ Criar dash_finance_service.py  
4. ✅ Adicionar endpoints no router
5. ✅ Testar todos os indicadores
6. ✅ Validar frontend plotting

## 12. MANUTENÇÃO

### 12.1 Performance
- Índices em `timestamp` (já existem)
- Considerar particionamento se volume crescer

### 12.2 Evolução
- Novos indicadores: adicionar em queries_helper.py
- Novos períodos: expandir convert_periodo_to_date()
- Agregações: implementar em service específico

---

**Desenvolvido seguindo padrões BTC Turbo: simplicidade, objetividade e reuso.**