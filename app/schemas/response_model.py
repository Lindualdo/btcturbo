# app/schemas/response_model.py

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
    blocos: Dict[str, BlocoCiclo]
