# app/routers/dashboards.py - Simplificado v1.0.21

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from app.config.dashboard_config import DASHBOARD_CONFIG
from app.utils.dashboard_helpers import build_dashboard_context

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def dashboard_principal(request: Request):
    """Dashboard principal v1.0.24 - Simplificado com config externa"""
    
    context = build_dashboard_context(request, DASHBOARD_CONFIG)
    return templates.TemplateResponse("dashboard_principal.html", context)