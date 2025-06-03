# app/routers/dashboards.py - CORRIGIDO v1.0.21

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

router = APIRouter()

# Configuração correta do Jinja2
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def dashboard_principal(request: Request):
    """
    Dashboard principal v1.0.21 - CORRIGIDO
    
    Problemas resolvidos:
    - Context variables para components
    - Configuração de gráficos
    - Estrutura de dados completa
    """
    
    # Context completo para o template
    context = {
        "request": request,
        "current_page": "home",
        "versao": "1.0.21",
        "subtitle": "Sistema v1.0.21 - Carregando dados...",
        
        # Configuração para JavaScript
        "config": {
            "versao": "1.0.21",
            "api_endpoint": "/api/v1/analise-btc",
            "novos_pesos": {
                "tecnico": 50,
                "ciclos": 30, 
                "momentum": 20,
                "riscos": 0
            }
        },
        
        # Dados para gráficos gauge
        "gauges": [
            {
                "id": "geral",
                "title": "🎯 Score Geral", 
                "is_main": True,
                "info": "Consolidado v1.0.21",
                "clickable": False
            },
            {
                "id": "tecnico",
                "title": "📈 Análise Técnica",
                "peso": 50,
                "clickable": True,
                "url": "/dashboard/tecnico",
                "info": "Clique para detalhes"
            },
            {
                "id": "ciclos", 
                "title": "🔄 Ciclos",
                "peso": 30,
                "clickable": True,
                "url": "/dashboard/ciclos",
                "info": "Clique para detalhes"
            },
            {
                "id": "momentum",
                "title": "⚡ Momentum", 
                "peso": 20,
                "clickable": True,
                "url": "/dashboard/momentum",
                "info": "Clique para detalhes"
            },
            {
                "id": "riscos",
                "title": "🚨 Riscos",
                "peso": 0,
                "clickable": True, 
                "url": "/dashboard/riscos",
                "info": "Só referência",
                "is_reference": True
            }
        ]
    }
    
    return templates.TemplateResponse("dashboard_principal.html", context)