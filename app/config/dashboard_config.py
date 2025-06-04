# app/config/dashboard_config.py

DASHBOARD_CONFIG = {
    "versao": "1.0.21",
    "api_endpoint": "/api/v1/analise-btc",
    "subtitle": "Sistema v1.0.21 - Carregando dados...",
    
    "pesos_blocos": {
        "tecnico": 50,
        "ciclos": 30, 
        "momentum": 20,
        "riscos": 0
    },
    
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