# app/schemas/v2/dashboard_response.py

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class HeaderData(BaseModel):
    """Dados do cabeçalho"""
    btc_price: float = Field(..., description="Preço atual do BTC")
    alavancagem_atual: float = Field(..., description="Alavancagem atual")
    status: str = Field(default="operacional", description="Status do sistema")

class ScoresData(BaseModel):
    """Scores consolidados"""
    mercado: float = Field(..., ge=0, le=100, description="Score de mercado (0-100)")
    risco: float = Field(..., ge=0, le=100, description="Score de risco (0-100)")
    mvrv: float = Field(..., description="MVRV Z-Score atual")
    health_factor: float = Field(..., gt=0, description="Health Factor da posição")

class EstrategiaData(BaseModel):
    """Dados da estratégia"""
    decisao: str = Field(..., description="Decisão final (COMPRAR/REALIZAR/HOLD)")
    ciclo: str = Field(..., description="Ciclo de mercado identificado")
    setup_4h: str = Field(..., description="Setup detectado no timeframe 4H")
    justificativa: str = Field(..., description="Justificativa da decisão")
    urgencia: str = Field(..., description="Nível de urgência (critica/alta/media/baixa)")

class TecnicosData(BaseModel):
    """Dados técnicos"""
    ema_distance: float = Field(..., description="Distância percentual da EMA144")
    rsi_diario: float = Field(..., ge=0, le=100, description="RSI diário (0-100)")
    preco_ema144: float = Field(..., description="Valor atual da EMA144")

class AlavancagemData(BaseModel):
    """Dados de alavancagem"""
    atual: float = Field(..., description="Alavancagem atual")
    permitida: float = Field(..., description="Alavancagem máxima permitida")
    valor_disponivel: float = Field(..., description="Capital livre disponível")
    dist_liquidacao: float = Field(..., description="Distância até liquidação (%)")

class DashboardV2Response(BaseModel):
    """Response completo do Dashboard V2"""
    timestamp: datetime = Field(..., description="Timestamp da geração")
    versao: str = Field(default="v2_dashboard", description="Versão do dashboard")
    
    header: HeaderData
    scores: ScoresData
    estrategia: EstrategiaData
    tecnicos: TecnicosData
    alavancagem: AlavancagemData

class DashboardV2Metadata(BaseModel):
    """Metadados do dashboard"""
    id: int = Field(..., description="ID do registro no banco")
    created_at: datetime = Field(..., description="Data/hora de criação")
    age_minutes: float = Field(..., description="Idade em minutos")
    versao: str = Field(default="v2_otimizado", description="Versão do sistema")

class DashboardV2FullResponse(BaseModel):
    """Response completo com metadados"""
    status: str = Field(..., description="Status da operação")
    data: DashboardV2Response = Field(..., description="Dados do dashboard")
    metadata: Optional[DashboardV2Metadata] = Field(None, description="Metadados")

class DashboardV2Error(BaseModel):
    """Response de erro"""
    status: str = Field(default="error", description="Status da operação")
    erro: str = Field(..., description="Mensagem de erro")
    message: str = Field(..., description="Descrição do problema")
    versao: str = Field(default="v2_otimizado", description="Versão do sistema")

class DashboardV2Debug(BaseModel):
    """Response de debug"""
    status: str = Field(..., description="Status da operação")
    versao: str = Field(default="v2_otimizado", description="Versão do sistema")
    ultimo_registro: Dict[str, Any] = Field(..., description="Dados do último registro")
    arquitetura: Dict[str, Any] = Field(..., description="Informações da arquitetura")

# Aliases para compatibilidade
DashboardDecisaoResponse = DashboardV2Response
DashboardDecisaoFullResponse = DashboardV2FullResponse