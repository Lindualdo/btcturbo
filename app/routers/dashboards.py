# app/routers/dashboards.py

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def dashboard_index():
    """Página inicial dos dashboards"""
    return """
    <html>
    <head>
        <title>BTC Turbo - Dashboards</title>
        <style>
            body { 
                font-family: Arial, sans-serif; margin: 40px; 
                background: #0f111a; color: white; 
            }
            h1 { color: #f7931a; font-size: 2.5rem; margin-bottom: 1rem; }
            .subtitle { color: #888; font-size: 1.2rem; margin-bottom: 2rem; }
            .dashboard-links { 
                display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px; margin-top: 30px; 
            }
            .dashboard-link { 
                background: #161b22; padding: 30px 20px; border-radius: 12px; 
                text-decoration: none; color: white; text-align: center;
                transition: all 0.3s ease; border: 2px solid transparent;
            }
            .dashboard-link:hover { 
                background: #1e1e1e; border-color: #f7931a; 
                transform: translateY(-2px); box-shadow: 0 5px 15px rgba(247, 147, 26, 0.2);
            }
            .dashboard-link h3 { margin: 0 0 10px 0; font-size: 1.3rem; }
            .status { font-weight: 600; }
            .status.funcionando { color: #4caf50; }
            .status.externo { color: #ff9800; }
            .footer { 
                margin-top: 50px; padding-top: 30px; 
                border-top: 1px solid #333; text-align: center; 
            }
            .footer a { color: #f7931a; text-decoration: none; margin: 0 15px; }
            .footer a:hover { text-decoration: underline; }
            @media (max-width: 768px) {
                body { margin: 20px; }
                .dashboard-links { grid-template-columns: 1fr; }
            }
        </style>
    </head>
    <body>
        <h1>🚀 BTC Turbo - Dashboards</h1>
        <div class="subtitle">Sistema v1.0.10 - Todos os dashboards funcionando!</div>
        
        <div class="dashboard-links">
            <a href="/dashboard/riscos" class="dashboard-link">
                <h3>📊 Riscos</h3>
                <p class="status funcionando">✅ Funcionando</p>
                <small>Distância Liquidação & Health Factor</small>
            </a>
            
            <a href="/dashboard/momentum" class="dashboard-link">
                <h3>⚡ Momentum</h3>
                <p class="status funcionando">✅ Funcionando</p>
                <small>RSI, Funding, OI Change & Long/Short</small>
            </a>
            
            <a href="/dashboard/ciclos" class="dashboard-link">
                <h3>🔄 Ciclos</h3>
                <p class="status funcionando">✅ Funcionando</p>
                <small>MVRV, Realized Price & Puell Multiple</small>
            </a>
            
            <a href="/dashboard/tecnico" class="dashboard-link">
                <h3>📈 Técnico</h3>
                <p class="status externo">🔗 API Externa</p>
                <small>EMAs Multi-TF & Sistema Técnico</small>
            </a>
        </div>
        
        <div class="footer">
            <a href="/docs">📋 APIs de Dados</a>
            <a href="/ping">🏥 Health Check</a>
            <a href="/api/v1/diagnostico/health-check">🔧 Diagnóstico</a>
        </div>
    </body>
    </html>
    """