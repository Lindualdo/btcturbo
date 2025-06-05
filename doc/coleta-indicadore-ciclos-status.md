# 📋 Release 1.0.16 - Documentação de Progresso
**BTC Turbo - Coleta Indicadores Bloco CICLO**

---

## 🎯 OBJETIVO DA RELEASE

Implementar coleta automatizada dos 3 indicadores do bloco CICLO usando BigQuery + APIs públicas:

1. **MVRV Z-Score** (peso 20%)
2. **Realized Price Ratio** (peso 15%) 
3. **Puell Multiple** (peso 5%)

**Meta:** Substituir mock por coleta real e gravar no PostgreSQL

---

## Ultima implementação - 01/06/25
✅ IMPLEMENTAÇÃO COMPLETA: RC REAL via BigQuery
📁 ESTRUTURA CRIADA:

bigquery_rc_calculator.py - Cálculo RC real UTXO-by-UTXO
historical_data.py - Série histórica otimizada
mvrv_calculator.py - MVRV Z-Score final

🧪 NOVOS ENDPOINTS DE TESTE:
Otimizado (rápido):
/api/v1/debug/mvrv-z-score-real
Preciso (lento mas real):
/api/v1/debug/mvrv-z-score-precise
Teste de qualidade:
/api/v1/debug/test-rc-accuracy

## 📁 ESTRUTURA de CALCLULO MVRV-Z-SCORE:

´´´
app/services/utils/helpers/
├── market_cap_helper.py          ✅ (existente)
├── realized_cap/                 🆕 (nova pasta)
│   ├── __init__.py
│   ├── bigquery_rc_calculator.py 🆕 (cálculo RC real)
│   ├── historical_data.py        🆕 (série histórica)
│   └── mvrv_calculator.py        🆕 (MVRV Z-Score final)
└── realized_cap_helper.py        🔄 (simplificar - só API atual)
´´´


## 📍 STATUS ATUAL - 40% COMPLETO

### ✅ ETAPAS CONCLUÍDAS

#### 1. Market Cap Calculation (100% ✅)
- **Arquivo:** `app/services/utils/helpers/market_cap_helper.py`
- **Funções implementadas:**
  - `get_btc_price()` - CoinGecko → Binance → CoinMarketCap fallback
  - `get_btc_supply()` - CoinGecko → Blockchain.com fallback
  - `get_current_market_cap()` - Cálculo e validação completa
  - `compare_with_reference()` - Comparação vs CoinGecko
- **Validação:** Range $1.2T-$1.8T
- **Status:** ✅ Funcionando perfeitamente

#### 2. BigQuery Infrastructure (100% ✅)
- **Conexão:** Configurada no Railway
- **Project ID:** `bitcoin-indicators-460816` (corrigido)
- **Credenciais:** Service Account funcionando
- **Acesso:** 1.197.656.576 transações Bitcoin disponíveis
- **Status:** ✅ Conexão validada

#### 3. Realized Cap Calculation (95% 🔄)
- **Arquivo:** `app/services/utils/helpers/realized_cap_helper.py`
- **BigQuery Helper:** Classe implementada
- **Schema descoberto:** Campo `value` (não `output_value`)
- **Status:** 🔄 Query corrigida sendo testada

---

### ETAPA 6: Puell Multiple
```python
# Criar: app/services/utils/helpers/puell_calculator.py
def calculate_puell_multiple() -> float:
    """
    Fórmula: Receita Diária Mineradores USD / MA365(Receita Diária)
    Receita = (Block Reward + Fees) × Preço BTC
    """
```

### ETAPA 7: Realized Price Ratio
```python
# Expandir: market_cap_helper.py
def calculate_realized_price_ratio() -> float:
    """
    Fórmula: Preço BTC / (Realized Cap / Supply Circulante)
    Componentes já implementados, só calcular
    """
```

### ETAPA 8: Integração Final
```python
# Atualizar: app/services/coleta/ciclos.py
def coletar(forcar_coleta: bool):
    """Substituir mock por coleta real"""
    try:
        # 1. Calcular MVRV Z-Score
        mvrv_z = calculate_mvrv_z_score()
        
        # 2. Calcular Realized Price Ratio  
        realized_ratio = calculate_realized_price_ratio()
        
        # 3. Calcular Puell Multiple
        puell_multiple = calculate_puell_multiple()
        
        # 4. Gravar no PostgreSQL
        success = insert_dados_ciclo(
            mvrv_z_score=mvrv_z,
            realized_ratio=realized_ratio,
            puell_multiple=puell_multiple,
            fonte="bigquery/apis"
        )
        
        return {
            "bloco": "ciclos",
            "status": "sucesso" if success else "erro",
            "dados_coletados": {
                "mvrv_z_score": mvrv_z,
                "realized_ratio": realized_ratio,
                "puell_multiple": puell_multiple
            }
        }
    except Exception as e:
        return {"bloco": "ciclos", "status": "erro", "detalhes": str(e)}
```

---

## 🔧 ARQUIVOS DO PROJETO

### Arquivos Criados ✅
```
app/services/utils/helpers/
├── market_cap_helper.py          ✅ COMPLETO
├── realized_cap_helper.py        🔄 95% COMPLETO
└── [FUTUROS]
    ├── mvrv_calculator.py        ⏳ PRÓXIMO
    ├── puell_calculator.py       ⏳ PENDENTE
    └── price_ratio_calculator.py ⏳ PENDENTE

app/routers/
└── debug.py                      ✅ COMPLETO (endpoints teste)
```

### Arquivos para Atualizar
```
app/services/coleta/
└── ciclos.py                     ⏳ REMOVER MOCK

app/main.py                       ✅ DEBUG ROUTER ADICIONADO
```

---

## 🧪 ENDPOINTS DE TESTE

### Market Cap (✅ Funcionando)
```bash
# Preço BTC atual
GET /api/v1/debug/btc-price

# Supply BTC atual  
GET /api/v1/debug/btc-supply

# Market Cap completo
GET /api/v1/debug/market-cap

# Comparação vs CoinGecko (deve bater 99%+)
GET /api/v1/debug/market-cap-comparison
```

### BigQuery (✅ Funcionando)
```bash
# Conexão básica
GET /api/v1/debug/bigquery-test

# Teste detalhado com diagnóstico
GET /api/v1/debug/bigquery-detailed-test

# Schema das tabelas Bitcoin
GET /api/v1/debug/bigquery-schema
```

### Realized Cap (🔄 Testando)
```bash
# Cálculo via BigQuery
GET /api/v1/debug/realized-cap

# Comparação BigQuery vs APIs externas
GET /api/v1/debug/realized-cap-comparison
```

---

## ⚠️ PROBLEMAS RESOLVIDOS

### 1. BigQuery 403 Forbidden ✅
- **Problema:** `User does not have bigquery.jobs.create permission`
- **Causa:** Project ID mismatch
  - Settings: `bitcoin-indicators`
  - JSON: `bitcoin-indicators-460816`
- **Solução:** Corrigido `GOOGLE_CLOUD_PROJECT=bitcoin-indicators-460816` no Railway

### 2. BigQuery Schema Errors ✅
- **Problema:** `Unrecognized name: is_spent` e `output_value`
- **Causa:** Campos não existem nas tabelas públicas
- **Solução:** Descoberto schema real via `/debug/bigquery-schema`
  - Campo correto: `value` (não `output_value`)
  - Sem campo `is_spent` disponível

### 3. Query Structure ✅
- **Descoberto:** Estrutura real das tabelas Bitcoin
- **Tables:** `outputs`, `transactions`, `inputs`
- **Key fields:** `value`, `block_timestamp`, `transaction_hash`

---

## 📊 VALIDAÇÕES IMPLEMENTADAS

### Market Cap
- **Range:** $0.5T - $3T (validação automática)
- **Componentes:** Preço $10k-$200k, Supply 19M-21M BTC
- **Precisão:** <5% diferença vs CoinGecko

### Realized Cap  
- **Range:** $200B - $1T (validação automática)
- **Estimativa:** 30-60% do Market Cap
- **Fallback:** Valor conservador $450B

### BigQuery
- **Conexão:** Validação automática
- **Dados:** 1.2B+ transações disponíveis
- **Performance:** <10s queries típicas

---

## 🚀 COMANDOS PARA NOVO DEV

### Setup Local
```bash
# Clonar projeto
git clone [repo-url]
cd btcturbo

# Instalar dependências  
pip install -r requirements.txt

# Configurar .env (copiar do Railway)
GOOGLE_CLOUD_PROJECT=bitcoin-indicators-460816
GOOGLE_APPLICATION_CREDENTIALS_JSON={...}
```

### Testes de Validação
```bash
# Testar Market Cap (deve retornar ~$1.4T)
curl https://btcturbo-production.up.railway.app/api/v1/debug/market-cap

# Testar BigQuery (deve retornar success)
curl https://btcturbo-production.up.railway.app/api/v1/debug/bigquery-test

# Testar Realized Cap (aguardando)
curl https://btcturbo-production.up.railway.app/api/v1/debug/realized-cap
```

### Debug Local
```bash
# Rodar servidor
uvicorn app.main:app --reload --port 8000

# Testar endpoints
http://localhost:8000/api/v1/debug/market-cap
http://localhost:8000/docs  # Swagger docs
```

---

## 📈 CRONOGRAMA ESTIMADO

| Etapa | Tempo | Status |
|-------|-------|--------|
| Market Cap | 2h | ✅ Completo |
| BigQuery Setup | 3h | ✅ Completo |
| Realized Cap | 2h | 🔄 95% |
| Série Histórica | 3h | ⏳ Próximo |
| MVRV Z-Score | 2h | ⏳ Pendente |
| Puell Multiple | 4h | ⏳ Pendente |
| Realized Price Ratio | 1h | ⏳ Pendente |
| Integração Final | 2h | ⏳ Pendente |
| **TOTAL** | **19h** | **40% Completo** |

---

## 🎯 PRÓXIMA AÇÃO IMEDIATA

1. **Aguardar:** Teste Realized Cap com query corrigida
2. **Se OK:** Implementar Série Histórica (Etapa 4)
3. **Se erro:** Debug BigQuery query específica

---

## 📝 NOTAS TÉCNICAS

### Formulas Implementadas
- ✅ **Market Cap:** `Preço BTC × Supply Circulante`
- 🔄 **Realized Cap:** `Σ(UTXO_value × price_when_created)` (aproximação via BigQuery)
- ⏳ **MVRV Z:** `(MC - RC) / StdDev(MC-RC series)`
- ⏳ **Puell:** `Daily_Mining_Revenue / MA365(Daily_Revenue)`
- ⏳ **Realized Ratio:** `BTC_Price / (RC / Supply)`

### Fontes de Dados
- **BigQuery:** Dados blockchain primários (1.2B+ transações)
- **CoinGecko:** Preços e supply (fallback confiável)
- **Binance:** Preços tempo real
- **Blockchain.com:** Supply circulante

### Qualidade Esperada
- **Precisão:** Equivalente ao Glassnode (±5%)
- **Atualização:** Tempo real para preços, diária para on-chain
- **Confiabilidade:** Sistema robusto de fallbacks

---

**Documentação gerada em:** 31/05/2025 21:02 UTC  
**Último commit:** Release 1.0.16 - Realized Cap query correction  
**Próximo milestone:** Série Histórica + MVRV Z-Score calculation