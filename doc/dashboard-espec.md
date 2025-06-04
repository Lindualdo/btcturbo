# 🔄 PROCESSO COMPLETO PASSO A PASSO - Dashboard BTC

## Visão Geral
Este documento detalha o fluxo completo desde a requisição inicial até a renderização final do dashboard de análise Bitcoin, passando por 17 etapas bem definidas.

---

## 1. REQUISIÇÃO INICIAL
```
GET /dashboard/
```

## 2. ROTEAMENTO FASTAPI
**Arquivo:** `app/main.py`

```python
app.include_router(dashboards.router, prefix="/dashboard", tags=["📱 Dashboards"])
```

## 3. ROUTER DASHBOARD
**Arquivo:** `app/routers/dashboards.py`  
**Função:** `dashboard_principal(request: Request)`

```python
@router.get("/", response_class=HTMLResponse)
async def dashboard_principal(request: Request):
    # Prepara context para o template
    context = {
        "request": request,
        "current_page": "home",
        "versao": "1.0.21",
        "config": {
            "api_endpoint": "/api/v1/analise-btc",
            "novos_pesos": {"tecnico": 50, "ciclos": 30, "momentum": 20, "riscos": 0}
        },
        "gauges": [
            {"id": "geral", "title": "🎯 Score Geral", "is_main": True},
            {"id": "tecnico", "title": "📈 Análise Técnica", "peso": 50, "url": "/dashboard/tecnico"},
            # ... outros gauges
        ]
    }
    
    # Renderiza template
    return templates.TemplateResponse("dashboard_principal.html", context)
```

## 4. RENDERIZAÇÃO DO TEMPLATE
**Arquivo:** `app/templates/dashboard_principal.html`

O template:
- Herda de `base.html`
- Recebe o context com configurações
- Renderiza HTML com placeholders para gráficos
- Embarca JavaScript que vai fazer fetch da API

## 5. RESPOSTA HTML ENVIADA AO BROWSER

```html
<!DOCTYPE html>
<html>
<!-- Menu de navegação -->
<!-- Grid com 5 canvas vazios para gráficos -->
<!-- JavaScript embarcado -->
<script>
// Aqui está a lógica que vai chamar a API
async function carregarDados() {
    const response = await fetch('/api/v1/analise-btc');
    // ...
}
</script>
</html>
```

## 6. BROWSER EXECUTA JAVASCRIPT
**Função JavaScript:** `carregarDados()`

```javascript
async function carregarDados() {
    // Mostra "Carregando..."
    document.getElementById('statusInfo').innerHTML = '<strong>🔄 Carregando dados...</strong>';
    
    // CHAMA A API PRINCIPAL
    const response = await fetch('/api/v1/analise-btc');
    const dados = await response.json();
    
    // Processa e exibe os dados
    exibirDados(dados);
}
```

## 7. SEGUNDA REQUISIÇÃO - API CONSOLIDADA
```
GET /api/v1/analise-btc
```

## 8. ROTEAMENTO DA API
**Arquivo:** `app/main.py`

```python
app.include_router(analise.router, prefix="/api/v1", tags=["📈 Análise"])
```

## 9. ROUTER ANÁLISE
**Arquivo:** `app/routers/analise.py`  
**Função:** `analise_btc_simplificada()`

```python
@router.get("/analise-btc")
async def analise_btc_simplificada(
    incluir_risco: bool = Query(False),
    force_update: bool = Query(False)
):
    try:
        # 1. VERIFICAR CACHE
        if not force_update:
            cache_data = get_score_cache_diario(incluir_risco=False)
            if cache_data:
                return cache_data  # RETORNA CACHE SE EXISTE
        
        # 2. BUSCAR DADOS FRESCOS - ORQUESTRA OS 4 BLOCOS
        dados_blocos = {
            "tecnico": tecnico.calcular_score(),      # ← CHAMA SERVICE
            "ciclos": ciclos.calcular_score(),        # ← CHAMA SERVICE  
            "momentum": momentum.calcular_score(),    # ← CHAMA SERVICE
            "riscos": riscos.calcular_score()         # ← CHAMA SERVICE
        }
        
        # 3. CALCULAR SCORE FINAL PONDERADO
        score_final = calcular_score_consolidado(dados_blocos)
        
        # 4. SALVAR NO CACHE
        save_score_cache_diario(resultado)
        
        # 5. RETORNAR JSON PADRONIZADO
        return resposta_final
    except Exception as e:
        return {"error": str(e)}
```

## 10. CADA BLOCO CHAMA SEU SERVICE
**Exemplo: Técnico**  
**Arquivo:** `app/services/scores/tecnico.py`

```python
def calcular_score():
    # 1. BUSCA DADOS BRUTOS DO BANCO
    dados_indicadores = indicadores_tecnico.obter_indicadores()
    
    # 2. APLICA REGRAS DE PONTUAÇÃO
    score_final = aplicar_regras_pontuacao(dados_indicadores)
    
    # 3. RETORNA JSON FORMATADO
    return {
        "bloco": "tecnico",
        "score_consolidado": score_final,
        "classificacao_consolidada": classificacao,
        "indicadores": {...}
    }
```

## 11. OBTER INDICADORES DO BANCO
**Arquivo:** `app/services/indicadores/tecnico.py`

```python
def obter_indicadores():
    # CHAMA HELPER POSTGRESQL
    dados_db = get_dados_tecnico()  # ← PostgreSQL query
    
    if dados_db:
        return {
            "indicadores": {
                "Sistema_EMAs": {"valor": dados_db["sistema_emas"], "score": ...},
                # ...
            },
            "status": "success"
        }
```

## 12. HELPER POSTGRESQL
**Arquivo:** `app/services/utils/helpers/postgres/tecnico_helper.py`

```python
def get_dados_tecnico():
    query = """
        SELECT sistema_emas, padroes_graficos, timestamp, fonte
        FROM indicadores_tecnico 
        ORDER BY timestamp DESC 
        LIMIT 1
    """
    return execute_query(query, fetch_one=True)
```

## 13. API RETORNA JSON CONSOLIDADO

```json
{
    "score_final": 6.18,
    "classificacao": "bom", 
    "kelly_allocation": "50%",
    "acao_recomendada": "Manter posição",
    "blocos": {
        "tecnico": {"score_consolidado": 7.54, "classificacao_consolidada": "Correção Saudável"},
        "ciclos": {"score_consolidado": 4.75, "classificacao_consolidada": "neutro"},
        "momentum": {"score_consolidado": 4.9, "classificacao_consolidada": "neutro"},
        "riscos": {"score_consolidado": 9.5, "classificacao_consolidada": "ótimo"}
    }
}
```

## 14. JAVASCRIPT PROCESSA RESPOSTA
**Função:** `exibirDados(dados)`

```javascript
function exibirDados(dados) {
    // 1. SCORE GERAL
    const scoreGeral = Math.round(dados.score_final * 10);  // 6.18 → 62
    exibirGrafico('geral', scoreGeral, dados.classificacao);
    
    // 2. CADA BLOCO
    const blocos = dados.blocos;
    for (const [nome, dadosBloco] of Object.entries(blocos)) {
        const score = Math.round(dadosBloco.score_consolidado * 10);
        const classificacao = dadosBloco.classificacao_consolidada;
        
        // Mapear nome para ID do gráfico
        let graficoId = nome === 'ciclo' ? 'ciclos' : nome;
        
        exibirGrafico(graficoId, score, classificacao);
    }
    
    // 3. ATUALIZAR STATUS
    document.getElementById('statusInfo').innerHTML = '✅ Dados carregados';
}
```

## 15. RENDERIZAR CADA GRÁFICO
**Função:** `exibirGrafico(id, score, classificacao)`

```javascript
function exibirGrafico(id, score, classificacao) {
    // 1. ATUALIZAR TEXTO
    document.getElementById('classificacao_' + id).textContent = 
        `Score: ${score} - ${classificacao}`;
    
    // 2. RENDERIZAR GAUGE COM CHART.JS
    renderizarGauge('gaugeChart_' + id, score);
}
```

## 16. CHART.JS DESENHA GRÁFICO
**Função:** `renderizarGauge(canvasId, score)`

```javascript
function renderizarGauge(canvasId, score) {
    const canvas = document.getElementById(canvasId);
    const ctx = canvas.getContext('2d');
    
    // Criar gráfico Chart.js tipo 'doughnut'
    new Chart(ctx, {
        type: 'doughnut',
        // ... configurações
        plugins: [{
            afterDraw: (chart) => {
                // Desenhar arcos coloridos
                // Desenhar ponteiro baseado no score
                // Desenhar centro
            }
        }]
    });
}
```

## 17. RESULTADO FINAL NO BROWSER
- 5 gráficos gauge renderizados
- Textos com scores e classificações atualizados
- Status "✅ Dados carregados"
- Interface totalmente funcional

---

## 🔄 RESUMO DO FLUXO

1. **GET /dashboard/** 
   ↓
2. **dashboards.py::dashboard_principal()** 
   ↓
3. **Renderiza dashboard_principal.html**
   ↓
4. **Browser executa JavaScript**
   ↓
5. **fetch('/api/v1/analise-btc')**
   ↓
6. **analise.py::analise_btc_simplificada()**
   ↓
7. **Orquestra 4 services** (tecnico, ciclos, momentum, riscos)
   ↓
8. **Cada service consulta PostgreSQL**
   ↓
9. **Retorna JSON consolidado**
   ↓
10. **JavaScript processa e renderiza gráficos**
    ↓
11. **Dashboard 100% funcional**

**Total:** 2 requisições HTTP, múltiplas consultas PostgreSQL, renderização Chart.js

---

## Estrutura de Arquivos

```
app/
├── main.py
├── routers/
│   ├── dashboards.py
│   └── analise.py
├── services/
│   ├── scores/
│   │   └── tecnico.py
│   ├── indicadores/
│   │   └── tecnico.py
│   └── utils/
│       └── helpers/
│           └── postgres/
│               └── tecnico_helper.py
└── templates/
    └── dashboard_principal.html
```

---
