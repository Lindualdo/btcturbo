# app/routers/dashboards.py - REFATORADO v1.0.21

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

# Configuração de templates
templates = Jinja2Templates(directory="app/templates")

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def dashboard_principal(request: Request):
    """
    Dashboard principal v1.0.21 - REFATORADO com Templates
    
    Mudanças:
    - HTML separado em templates Jinja2
    - CSS/JS em arquivos dedicados  
    - Código Python reduzido de 870 para ~30 linhas
    - Manutenção muito mais fácil
    """
    
    # Dados para o template
    context = {
        "request": request,
        "current_page": "home",
        "versao": "1.0.21",
        "subtitle": "Sistema v1.0.21 - Carregando dados...",
        
        # Configuração dos blocos
        "blocos": {
            "tecnico": {
                "title": "📈 Análise Técnica",
                "peso": 50,
                "url": "/dashboard/tecnico"
            },
            "ciclos": {
                "title": "🔄 Ciclos", 
                "peso": 30,
                "url": "/dashboard/ciclos"
            },
            "momentum": {
                "title": "⚡ Momentum",
                "peso": 20, 
                "url": "/dashboard/momentum"
            },
            "riscos": {
                "title": "🚨 Riscos",
                "peso": 0,
                "url": "/dashboard/riscos",
                "nota": "Apenas referência"
            }
        },
        
        # Configurações da API
        "config": {
            "versao": "1.0.21",
            "api_endpoint": "/api/v1/analise-btc",
            "novos_pesos": {
                "tecnico": 50,
                "ciclos": 30, 
                "momentum": 20,
                "riscos": 0
            }
        }
    }
    
    return templates.TemplateResponse("dashboard_principal.html", context)

# Funções auxiliares para configuração
def get_dashboard_config():
    """Configuração padrão dos dashboards"""
    return {
        "versao": "1.0.21",
        "api_endpoint": "/api/v1/analise-btc",
        "pesos": {
            "tecnico": 50,
            "ciclos": 30,
            "momentum": 20,
            "riscos": 0
        }
    }

def get_blocos_config():
    """Configuração dos blocos do dashboard"""
    return {
        "tecnico": {
            "title": "📈 Análise Técnica",
            "peso": 50,
            "url": "/dashboard/tecnico",
            "emoji": "📈"
        },
        "ciclos": {
            "title": "🔄 Ciclos",
            "peso": 30,
            "url": "/dashboard/ciclos", 
            "emoji": "🔄"
        },
        "momentum": {
            "title": "⚡ Momentum",
            "peso": 20,
            "url": "/dashboard/momentum",
            "emoji": "⚡"
        },
        "riscos": {
            "title": "🚨 Riscos",
            "peso": 0,
            "url": "/dashboard/riscos",
            "emoji": "🚨",
            "nota": "Apenas referência"
        }
    }