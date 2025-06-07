# app/services/alertas/models.py

from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class TipoAlerta(str, Enum):
    POSICAO = "posicao"
    MERCADO = "mercado"
    VOLATILIDADE = "volatilidade"
    TATICO = "tatico"
    ONCHAIN = "onchain"

class CategoriaAlerta(str, Enum):
    CRITICO = "critico"
    URGENTE = "urgente"
    INFORMATIVO = "informativo"

class AlertaResponse(BaseModel):
    id: int
    tipo: TipoAlerta
    categoria: CategoriaAlerta
    prioridade: int
    
    titulo: str
    mensagem: str
    
    threshold_configurado: Optional[float]
    valor_atual: Optional[float]
    dados_contexto: Dict[str, Any]
    
    ativo: bool
    resolvido: bool
    resolvido_em: Optional[datetime]
    
    timestamp: datetime
    
    # Campos computados
    tempo_ativo: Optional[str] = None
    acao_sugerida: Optional[str] = None
    icone: str = ""
    cor: str = ""

class AlertaResumo(BaseModel):
    """Widget principal dashboard"""
    criticos: int
    urgentes: int
    informativos: int
    volatilidade: int
    
    total_ativos: int
    ultima_verificacao: datetime
    proxima_acao: Optional[str]
    
    # Breakdown por tipo
    por_tipo: Dict[str, int]

class AlertaConfig(BaseModel):
    tipo: TipoAlerta
    categoria: CategoriaAlerta
    
    habilitado: bool
    threshold_customizado: Optional[float]
    cooldown_minutos: int
    
    notificacao_dashboard: bool
    notificacao_webhook: bool
    webhook_url: Optional[str]

class AlertaCreate(BaseModel):
    """Para criação interna de alertas"""
    tipo: TipoAlerta
    categoria: CategoriaAlerta
    prioridade: int
    
    titulo: str
    mensagem: str
    
    threshold_configurado: Optional[float]
    valor_atual: Optional[float]
    dados_contexto: Dict[str, Any] = {}
    
    cooldown_minutos: int = 60

class AlertaDetectado(BaseModel):
    """Resultado de detecção"""
    detectado: bool
    alerta: Optional[AlertaCreate]
    motivo: Optional[str]
    valor_atual: Optional[float]
    dados_debug: Dict[str, Any] = {}