# app/routers/dashboards.py

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from app.services.template_service import template_service
from app.services.scores import ciclos, momentum, riscos, tecnico

router = APIRouter()

@router.get("/riscos", response_class=HTMLResponse)
async def dashboard_riscos():
    """Dashboard de análise de riscos"""
    try:
        # Buscar dados da API interna
        dados = riscos.calcular_score()
        
        # Renderizar template
        html = template_service.render_dashboard("riscos", dados)
        return html
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar dashboard riscos: {str(e)}")

@router.get("/tecnico", response_class=HTMLResponse)
async def dashboard_tecnico():
    """Dashboard de análise técnica (placeholder)"""
    try:
        dados = tecnico.calcular_score()
        
        # Por enquanto retorna dados JSON até criarmos o template
        return f"""
        <html>
        <head><title>BTC Turbo - Técnico</title></head>
        <body>
            <h1>Dashboard Técnico (Em Desenvolvimento)</h1>
            <pre>{dados}</pre>
            <a href="/dashboard/riscos">Ir para Riscos</a>
        </body>
        </html>
        """
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar dashboard técnico: {str(e)}")

@router.get("/ciclos", response_class=HTMLResponse)
async def dashboard_ciclos():
    """Dashboard de análise de ciclos (placeholder)"""
    try:
        dados = ciclos.calcular_score()
        
        return f"""
        <html>
        <head><title>BTC Turbo - Ciclos</title></head>
        <body>
            <h1>Dashboard Ciclos (Em Desenvolvimento)</h1>
            <pre>{dados}</pre>
            <a href="/dashboard/riscos">Ir para Riscos</a>
        </body>
        </html>
        """
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar dashboard ciclos: {str(e)}")

@router.get("/momentum", response_class=HTMLResponse)
async def dashboard_momentum():
    """Dashboard de análise de momentum (placeholder)"""
    try:
        dados = momentum.calcular_score()
        
        return f"""
        <html>
        <head><title>BTC Turbo - Momentum</title></head>
        <body>
            <h1>Dashboard Momentum (Em Desenvolvimento)</h1>
            <pre>{dados}</pre>
            <a href="/dashboard/riscos">Ir para Riscos</a>
        </body>
        </html>
        """
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar dashboard momentum: {str(e)}")

@router.get("/consolidado", response_class=HTMLResponse)
async def dashboard_consolidado():
    """Dashboard consolidado com todos os blocos (placeholder)"""
    try:
        # Buscar dados de todos os blocos
        dados_completos = {
            "ciclos": ciclos.calcular_score(),
            "momentum": momentum.calcular_score(), 
            "riscos": riscos.calcular_score(),
            "tecnico": tecnico.calcular_score()
        }
        
        return f"""
        <html>
        <head><title>BTC Turbo - Consolidado</title></head>
        <body>
            <h1>Dashboard Consolidado (Em Desenvolvimento)</h1>
            <h2>Todos os Blocos:</h2>
            <pre>{dados_completos}</pre>
            <a href="/dashboard/riscos">Ir para Riscos</a>
        </body>
        </html>
        """
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar dashboard consolidado: {str(e)}")

@router.get("/", response_class=HTMLResponse)
async def dashboard_index():
    """Página inicial dos dashboards"""
    return """
    <html>
    <head>
        <title>BTC Turbo - Dashboards</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #0f111a; color: white; }
            h1 { color: #f7931a; }
            .dashboard-links { display: flex; flex-wrap: wrap; gap: 20px; margin-top: 30px; }
            .dashboard-link { 
                background: #161b22; 
                padding: 20px; 
                border-radius: 8px; 
                text-decoration: none; 
                color: white;
                min-width: 200px;
                text-align: center;
                transition: background 0.3s;
            }
            .dashboard-link:hover { background: #1e1e1e; }
            .status { color: #4caf50; }
            .placeholder { color: #888; }
        </style>
    </head>
    <body>
        <h1>🚀 BTC Turbo - Dashboards</h1>
        <p>Escolha um dashboard para visualizar:</p>
        
        <div class="dashboard-links">
            <a href="/dashboard/riscos" class="dashboard-link">
                <h3>📊 Riscos</h3>
                <p class="status">✅ Funcionando</p>
            </a>
            
            <a href="/dashboard/tecnico" class="dashboard-link">
                <h3>📈 Técnico</h3>
                <p class="placeholder">🚧 Em desenvolvimento</p>
            </a>
            
            <a href="/dashboard/ciclos" class="dashboard-link">
                <h3>🔄 Ciclos</h3>
                <p class="placeholder">🚧 Em desenvolvimento</p>
            </a>
            
            <a href="/dashboard/momentum" class="dashboard-link">
                <h3>⚡ Momentum</h3>
                <p class="placeholder">🚧 Em desenvolvimento</p>
            </a>
            
            <a href="/dashboard/consolidado" class="dashboard-link">
                <h3>🎯 Consolidado</h3>
                <p class="placeholder">🚧 Em desenvolvimento</p>
            </a>
        </div>
        
        <div style="margin-top: 40px;">
            <a href="/docs" style="color: #f7931a;">📋 Ver APIs de Dados</a> | 
            <a href="/ping" style="color: #f7931a;">🏥 Health Check</a>
        </div>
    </body>
    </html>
    """