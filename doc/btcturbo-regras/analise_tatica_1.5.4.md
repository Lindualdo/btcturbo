# BTC TURBO v1.5.4 - ESPECIFICAÇÃO EXECUÇÃO TÁTICA

**Versão:** 1.5.4  
**Objetivo:** Simplificar arquitetura com inteligência concentrada nos setups  
**Data:** Junho 2025  

---

## 🎯 ARQUITETURA SIMPLIFICADA

```
dash_main_service > analise_tecnica_service > setup_detector_utils > setups
                                                    ↓
                                            analise_tecnica_helper
                                                    ↓
                                            tradingview_helper
```

---

## 📁 ESTRUTURA DE ARQUIVOS

```
dash_main/analise_tecnica/
├── analise_tecnica_service.py          # Orquestrador simples
├── setup_detector_utils.py             # Fornece dados técnicos para setups
├── gate_system_utils.py                # Mockado: sempre aprova
└── setups_compra/
    ├── pullback_tendencia.py           # Setup inteligente completo
    ├── oversold_extremo.py             # Setup inteligente completo
    ├── teste_suporte.py                # Setup inteligente completo
    ├── rompimento_resistencia.py       # Setup inteligente completo
    └── cruzamento_medias.py             # Setup inteligente completo

dash_main/helpers/
└── analise_tecnica_helper.py           # Busca TODOS dados técnicos
```

---

## 🔧 RESPONSABILIDADES DETALHADAS

### **1. analise_tecnica_service.py**
```python
def executar_analise(dados_mercado, dados_risco, dados_alavancagem):
    # 1. Gate system (mockado - sempre aprova)
    # 2. Chama setup_detector_utils.identificar_setup()
    # 3. Retorna resultado final
```

### **2. setup_detector_utils.py**
```python
def identificar_setup():
    # 1. Chama analise_tecnica_helper.get_todos_dados_tecnicos()
    # 2. Fornece mesmos dados para todos os setups
    # 3. Testa setups por prioridade
    # 4. Para no primeiro encontrado
```

### **3. analise_tecnica_helper.py**
```python
def get_todos_dados_tecnicos():
    # Busca TODOS dados técnicos via tradingview_helper
    # RSI 4H, EMAs, preços, distâncias
    # Retorna dataset completo consolidado
```

### **4. gate_system_utils.py**
```python
def aplicar_gate_system():
    # Mockado: sempre retorna LIBERADO
    return {"liberado": True, "motivo": "Mockado v1.5.4"}
```

### **5. Setups Individuais**
**Cada setup processa TUDO internamente:**
- Recebe dados técnicos completos
- Aplica suas condições específicas  
- Calcula força própria
- Define tamanho posição (mockado)
- Retorna: `{dados_tecnicos, estrategia, encontrado}`

---

## 📊 DADOS TÉCNICOS CONSOLIDADOS

```python
dados_tecnicos = {
    "rsi_4h": float,
    "precos": {
        "atual": float,
        "ema_17": float,
        "ema_144": float
    },
    "distancias": {
        "ema_144_distance": float,  # Percentual
        "ema_17_distance": float    # Percentual
    },
    "timestamp": datetime
}
```

---

## 🎯 SETUPS DE COMPRA

### Prioridade e Configuração

| Setup | Condições | Força | Tamanho | Status |
|-------|-----------|-------|---------|--------|
| **OVERSOLD_EXTREMO** | RSI < 30 | Dinâmica por proximidade | 40% mockado | ✅ Implementar |
| **PULLBACK_TENDENCIA** | RSI < 45 + EMA144 ±3% | Dinâmica por proximidade | 30% mockado | 🔄 Refatorar |
| **TESTE_SUPORTE** | Preço próximo EMA144 ±2% | Dinâmica por proximidade | 25% mockado | ✅ Implementar |
| **ROMPIMENTO** | Preço > resistência | Custom | 20% mockado | ✅ Implementar |
| **CRUZAMENTO_MEDIAS** | EMA17 > EMA144 + distância | Custom | 25% mockado | ✅ Implementar |

### Cálculo de Força (Exemplo)
```python
# Cada setup define sua própria lógica
def calcular_forca_pullback(rsi, ema_distance):
    if rsi < 35 and abs(ema_distance) < 1:
        return "muito_alta"
    elif rsi < 40 and abs(ema_distance) < 2:
        return "alta"
    elif rsi < 45 and abs(ema_distance) < 3:
        return "media"
    else:
        return "baixa"
```

---

## 🔄 RETORNO PADRONIZADO

### Setup Encontrado
```json
{
    "encontrado": true,
    "setup": "PULLBACK_TENDENCIA",
    "forca": "alta",
    "tamanho_posicao": 30,
    "dados_tecnicos": {
        "rsi_4h": 42.3,
        "precos": {
            "atual": 103500.0,
            "ema_144": 103000.0
        },
        "distancias": {
            "ema_144_distance": 1.2
        }
    },
    "estrategia": {
        "decisao": "COMPRAR",
        "setup": "PULLBACK_TENDENCIA",
        "urgencia": "alta",
        "justificativa": "RSI 42.3 + EMA144 dist +1.2%"
    }
}
```

### Nenhum Setup
```json
{
    "encontrado": false,
    "setup": "NENHUM",
    "dados_tecnicos": {
        "rsi_4h": 55.0,
        "precos": {...},
        "distancias": {...}
    },
    "estrategia": {
        "decisao": "AGUARDAR",
        "setup": "NENHUM",
        "urgencia": "baixa",
        "justificativa": "Nenhum setup identificado"
    }
}
```

---

## 🚫 REMOVIDOS NA v1.5.4

- ❌ `comprar_helper.py` (lógica movida para setups)
- ❌ Validações complexas do gate system
- ❌ Overrides especiais
- ❌ Processadores externos de estratégia
- ❌ Lógicas dispersas entre arquivos

---

## 🔄 MOCKADOS (IMPLEMENTAR DEPOIS)

- Gate system validações reais
- Tamanhos de posição dinâmicos
- Validações de volume
- Health factor checks
- Stop loss automático

---

## 📋 IMPLEMENTAÇÃO PRIORITÁRIA

### 1. **analise_tecnica_helper.py**
```python
def get_todos_dados_tecnicos():
    # Buscar via tradingview_helper:
    # - RSI 4H atual
    # - Preço atual BTC
    # - EMA 17, 144 valores
    # - Calcular distâncias percentuais
    # - Timestamp dos dados
```

### 2. **Refatorar pullback_tendencia.py**
- Receber dados consolidados
- Processar internamente 
- Retornar formato padronizado

### 3. **Implementar outros 4 setups**
- oversold_extremo.py
- teste_suporte.py  
- rompimento_resistencia.py
- cruzamento_medias.py

### 4. **Simplificar arquivos existentes**
- analise_tecnica_service.py (mínimo)
- setup_detector_utils.py (mínimo)

---

## 🎯 REGRAS DE DESENVOLVIMENTO

### Arquitetura
- ✅ Cada setup é autocontido e inteligente
- ✅ Dados técnicos centralizados em um helper
- ✅ Arquivos < 200 linhas
- ✅ Sem lógica dispersa
- ✅ Um arquivo = uma responsabilidade

### Dados
- ❌ Sem valores fixos/simulados
- ✅ Fallbacks com erro + log
- ✅ Timestamp em todos os dados
- ✅ Validação de ranges

### Logs
- ✅ Log em cada etapa crítica
- ✅ Rastreamento completo do fluxo
- ✅ Dados técnicos logados

---

## 🚀 FLUXO DE TESTE

```bash
# Endpoint principal
POST /api/v3/dash-main

# Logs esperados
🎯 Executando Camada 4: Execução Tática
🚪 Gate: LIBERADO (mockado v1.5.4)
📊 Coletando dados técnicos consolidados...
🔍 Testando setup: OVERSOLD_EXTREMO
🔍 Testando setup: PULLBACK_TENDENCIA
✅ Setup PULLBACK_TENDENCIA identificado - Força: alta
🎯 Decisão: COMPRAR - Urgência: alta
```

---

**Foco v1.5.4:** Arquitetura mínima, setups inteligentes, dados centralizados.  
**Próximo:** v1.5.5 com gate system real e validações avançadas.