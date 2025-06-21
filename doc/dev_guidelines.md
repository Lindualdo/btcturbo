# GUIDELINES-DEV.md - Instruções para Agente LLM

## 🎯 Padrão de Trabalho Obrigatório

### **Regras Rígidas - NUNCA Viole**
- ❌ NÃO alucinar - seja técnico, objetivo e profissional
- ❌ NÃO over-engineering - faça o código mais simples possível
- ❌ NÃO refactore sem solicitação expressa
- ❌ NÃO supor informações - tenha certeza antes de implementar
- ❌ NÃO deixar valores fixos/simulados no código
- ❌ NÃO alterar regras durante implementação sem aprovação

### **Sempre Faça**
- ✅ Confirme com usuário se não tiver certeza
- ✅ Fallbacks devem retornar erro + log (nunca dados falsos)
- ✅ Separe implementações nas camadas: routers > services > utils > helpers
- ✅ Arquivos máximo 200 linhas
- ✅ Uma finalidade por arquivo
- ✅ Procure funções existentes antes de criar novas

## 🏗️ Arquitetura BTC Turbo

```
app/
├── routers/           # Endpoints FastAPI
├── services/          # Lógica de negócio
│   ├── coleta/       # Dados externos (Notion, TradingView)
│   ├── indicadores/  # Obtenção banco dados
│   ├── scores/       # Algoritmos pontuação
│   ├── dashboards/   # Dashboards principais
│   └── utils/helpers/ # Funções auxiliares
```

## 📝 Padrões de Código

### **Nomenclatura**
```python
# Funções: verbo_substantivo
def coletar_indicadores(), calcular_score_ciclo()

# Variáveis: snake_case descritivo  
dados_mercado, score_consolidado, health_factor

# Logs com emojis identificação
logger.info("🔄 Iniciando...")    # Processo
logger.info("✅ Sucesso")         # Sucesso
logger.error("❌ Erro")           # Erro
```

### **Estrutura Função Padrão**
```python
def nome_funcao(params):
    """Docstring explicando função"""
    try:
        logger.info("🔄 Iniciando [processo]...")
        
        # 1. Validações
        # 2. Lógica principal
        # 3. Log resultado
        
        logger.info("✅ [Processo] concluído")
        return resultado
        
    except Exception as e:
        logger.error(f"❌ Erro [processo]: {str(e)}")
        return {"status": "erro", "detalhes": str(e)}
```

### **Imports Organizados**
```python
# 1. Standard library
from datetime import datetime
import logging

# 2. Third party
from fastapi import APIRouter

# 3. App imports
from app.services.utils.helpers.postgres.base import execute_query
```

## 🔧 Tecnologias Específicas

### **FastAPI**
```python
# Router padrão
router = APIRouter()

@router.post("/endpoint")
async def endpoint_function():
    return service_function()
```

### **PostgreSQL**
```python
# SEMPRE usar helpers existentes
from app.services.utils.helpers.postgres.base import execute_query

# NUNCA SQL direto nos services
def get_dados():
    query = "SELECT * FROM tabela ORDER BY timestamp DESC LIMIT 1"
    return execute_query(query, fetch_one=True)
```

### **APIs Externas**
```python
# Sempre timeout + fallback
def buscar_external_api():
    try:
        response = requests.get(url, timeout=10)
        return response.json()
    except Exception as e:
        logger.error(f"❌ API falhou: {e}")
        return None  # NUNCA retornar dados simulados
```

## 📊 Regras de Negócio

### **Blocos Sistema**
- **ciclos**: MVRV, NUPL, Realized Ratio, Puell Multiple
- **momentum**: RSI, Funding Rates, SOPR, Long/Short Ratio
- **riscos**: Health Factor, Distance Liquidação
- **tecnico**: EMAs, RSI, Padrões Gráficos

### **Scores (0-10)**
- 8-10: Tendência Forte
- 6-8: Correção Saudável
- 4-6: Neutro
- 2-4: Reversão
- 0-2: Bear Confirmado

### **Endpoints Atuais**
```
POST /api/v1/coletar-indicadores/{bloco}
GET  /api/v1/obter-indicadores/{bloco}
GET  /api/v1/calcular-score/{bloco}
POST /api/v1/dash-mercado
GET  /api/v1/dash-mercado
POST /api/v1/dash-main
GET  /api/v1/dash-main
```

## 🚨 Validação Antes de Implementar

### **Perguntas Obrigatórias**
1. Esta funcionalidade já existe?
2. Qual camada específica (router/service/utils/helpers)?
3. Precisa de dados externos ou só banco?
4. Impacta outros endpoints?
5. Logs suficientes para debug?

### **Checklist Final**
- [ ] Função < 200 linhas
- [ ] Try/catch implementado
- [ ] Logs em etapas críticas
- [ ] Imports organizados
- [ ] Sem valores fixos
- [ ] Documentação regras negócio
- [ ] Reutiliza funções existentes

## 💬 Comunicação com Usuário

### **Sempre Confirme**
- "Entendi que precisa implementar X na camada Y. Correto?"
- "Vou usar a função existente Z ou criar nova? Por quê?"
- "Esta alteração impacta endpoints A, B. Prossigo?"

### **Nunca Assuma**
- ❌ "Vou implementar da forma que acho melhor"
- ❌ "Adicionei esta funcionalidade extra"
- ❌ "Refatorei o código para melhorar"

### **Sempre Explique**
- ✅ "Implementei X porque Y solicitou"
- ✅ "Usei função Z existente em vez de criar nova"
- ✅ "Adicionei logs nos pontos críticos A, B, C"

---

**Objetivo**: Código simples, confiável e manutenível para trading BTC alavancado.