# routers/v3/dash_home.py
from fastapi import APIRouter
from app.services.v3.dash_main.dash_home_service import processar_dashboard, obter_dashboard, debug_dashboard 

router = APIRouter()

@router.post("/dashboard-home")
async def post_dashboard():
    """POST - Calcula novo dashboard V3"""
    return processar_dashboard()

@router.get("/dashboard-home")
async def get_dashboard():
    """GET - Retorna último dashboard V3"""
    return obter_dashboard()

@router.get("/dashboard-home/debug")
async def debug_dashboard_endpoint():
    """DEBUG - Info sistema V3"""
    return debug_dashboard()