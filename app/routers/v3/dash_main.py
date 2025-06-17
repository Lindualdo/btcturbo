# routers/v3/dash_home.py
from fastapi import APIRouter
from app.services.v3.dash_home_service import calcular_dashboard_v3, obter_dashboard_v3, debug_dashboard_v3

router = APIRouter()

@router.post("/dashboard-home")
async def post_dashboard_v3():
    """POST - Calcula novo dashboard V3"""
    return calcular_dashboard_v3()

@router.get("/dashboard-home")
async def get_dashboard_v3():
    """GET - Retorna último dashboard V3"""
    return obter_dashboard_v3()

@router.get("/dashboard-home/debug")
async def debug_dashboard_v3_endpoint():
    """DEBUG - Info sistema V3"""
    return debug_dashboard_v3()