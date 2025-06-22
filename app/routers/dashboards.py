# source: app/routers/dashboards.py
from fastapi import APIRouter
from app.services.dashboards.dash_main_service import processar_dash_main, obter_dash_main
from app.services.dashboards.dash_mercado_service   import processar_dash_mercado, obter_dash_mercado
from app.services.utils.helpers.postgres.mercado.database_helper import get_ciclo_mercado
from app.services.dashboards.dash_main.analise_alavancagem import  executar_analise_alavancagem

router = APIRouter()

# processa as 4 camadas de analise (analise de mercado, de riscos, de alavancagem e execução tática)
@router.post("/dash-main")
async def post_dash_main():
    return processar_dash_main()

# Obtem o dashboard principal (analise de mercado, de riscos, de alavancagem e execução tática)
@router.get("/dash-main")
async def get_dash_main():
    return obter_dash_main()

# processa o dashboard de mercado 
# analisa os scores de ciclo, momentum e tecnico e gera score ponderado de mercado 
# grava indicadores e scores de cada bloco + score ponderado de mercado
@router.post("/dash-mercado")
async def post_dash_mercado():
    return processar_dash_mercado()

# Obtem os dados para visualização do dashboard de mercado 
@router.get("/dash-mercado")
async def get_dash_mercado():
    return obter_dash_mercado()

@router.get("/dash-mercado/debug")
async def get_dash_mercado():
    return get_ciclo_mercado()

@router.get("/dash-main/alavancagem")
async def get_dash_mercado():
    dados_mercado = get_ciclo_mercado()
    alavancagem_permitida = dados_mercado["ciclo_detalhes"]["alavancagem"]
    return executar_analise_alavancagem(alavancagem_permitida)