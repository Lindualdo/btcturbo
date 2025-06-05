#/app/rouuters/alertas.py

from fastapi import APIRouter
from services import alertas as alertas_service

router = APIRouter()

@router.get("/api/v1/alertas")
async def obter_alertas():
    return alertas_service.get_alertas()
