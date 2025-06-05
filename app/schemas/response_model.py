
# app/schemas/response_model.py

from pydantic import BaseModel
from datetime import datetime
from typing import Dict, List, Union

class IndicadorResponse(BaseModel):
    valor: Union[float, str]
    score: float

class BlocoResponse(BaseModel):
    score: float
    indicadores: Dict[str, IndicadorResponse]

class PesosDinamicos(BaseModel):
    ciclo: float
    momentum: float
    risco: float
    tecnico: float

class AnaliseBTCResponse(BaseModel):
    timestamp: datetime
    score_final: float
    score_ajustado: float
    modificador_volatilidade: float
    classificacao_geral: str
    kelly_allocation: str
    acao_recomendada: str
    alertas_ativos: List[str]
    pesos_dinamicos: PesosDinamicos
    blocos: Dict[str, BlocoResponse]

# Alias para compatibilidade
BlocoCiclo = BlocoResponse