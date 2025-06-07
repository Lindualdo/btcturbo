# app/services/alertas/detectores/posicao_detector.py

import logging
from typing import List, Optional
from datetime import datetime, timedelta
from ..models import AlertaCreate, TipoAlerta, CategoriaAlerta
from ...utils.helpers.postgres import get_dados_risco
from ...analises.analise_risco import calcular_analise_risco
from ...analises.analise_alavancagem import calcular_analise_alavancagem

logger = logging.getLogger(__name__)

class PosicaoDetector:
    """
    Detecta TODOS os 5 alertas críticos conforme doc:
    1. Health Factor < 1.3
    2. Distância Liquidação < 20%  
    3. Score Risco < 30
    4. Portfolio Loss 24h > 20%
    5. Leverage > MVRV Max * 1.2
    """
    
    def verificar_alertas(self) -> List[AlertaCreate]:
        """Verifica todos os alertas críticos de posição"""
        alertas = []
        
        try:
            # Buscar todos os dados necessários
            dados_risco = get_dados_risco()
            analise_risco = calcular_analise_risco()
            analise_alavancagem = calcular_analise_alavancagem()
            
            if not dados_risco:
                logger.warning("⚠️ Dados de risco indisponíveis")
                return alertas
            
            # 1. CRÍTICO: Health Factor < 1.3
            hf_critico = self._check_health_factor_critico(dados_risco)
            if hf_critico:
                alertas.append(hf_critico)
            
            # 2. CRÍTICO: Distância Liquidação < 20%
            dist_critico = self._check_distancia_liquidacao_critico(dados_risco)
            if dist_critico:
                alertas.append(dist_critico)
            
            # 3. CRÍTICO: Score Risco < 30
            score_critico = self._check_score_risco_critico(analise_risco)
            if score_critico:
                alertas.append(score_critico)
            
            # 4. CRÍTICO: Portfolio Loss 24h > 20%
            loss_critico = self._check_portfolio_loss_critico(dados_risco)
            if loss_critico:
                alertas.append(loss_critico)
            
            # 5. CRÍTICO: Leverage > MVRV Max * 1.2
            leverage_critico = self._check_overleveraged_critico(dados_risco, analise_alavancagem)
            if leverage_critico:
                alertas.append(leverage_critico)
            
            logger.info(f"🚨 Críticos: {len(alertas)} alertas detectados")
            return alertas
            
        except Exception as e:
            logger.error(f"❌ Erro detector críticos: {str(e)}")
            return []
    
    def _check_health_factor_critico(self, dados_risco) -> Optional[AlertaCreate]:
        """1. Health Factor < 1.3 = Reduzir 70% AGORA"""
        try:
            health_factor = float(dados_risco.get("health_factor", 999))
            
            if health_factor < 1.3:
                return AlertaCreate(
                    tipo=TipoAlerta.POSICAO,
                    categoria=CategoriaAlerta.CRITICO,
                    prioridade=0,
                    titulo="🚨 CRÍTICO: Health Factor",
                    mensagem=f"Health Factor {health_factor:.2f} - Reduzir 70% AGORA",
                    threshold_configurado=1.3,
                    valor_atual=health_factor,
                    dados_contexto={
                        "acao_recomendada": "Reduzir 70% da posição imediatamente",
                        "risco": "Liquidação iminente",
                        "timeframe": "Imediato",
                        "tipo_critico": "health_factor"
                    },
                    cooldown_minutos=5
                )
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro check HF crítico: {str(e)}")
            return None
    
    def _check_distancia_liquidacao_critico(self, dados_risco) -> Optional[AlertaCreate]:
        """2. Distância Liquidação < 20% = EMERGÊNCIA"""
        try:
            dist_liquidacao = self._extract_distance_value(dados_risco.get("dist_liquidacao"))
            
            if dist_liquidacao and dist_liquidacao < 20:
                return AlertaCreate(
                    tipo=TipoAlerta.POSICAO,
                    categoria=CategoriaAlerta.CRITICO,
                    prioridade=0,
                    titulo="🚨 PERIGO: Liquidação",
                    mensagem=f"Liquidação em -{dist_liquidacao:.1f}% - EMERGÊNCIA",
                    threshold_configurado=20.0,
                    valor_atual=dist_liquidacao,
                    dados_contexto={
                        "acao_recomendada": "Reduzir posição urgentemente",
                        "risco": "Liquidação iminente",
                        "timeframe": "Imediato",
                        "tipo_critico": "distancia_liquidacao"
                    },
                    cooldown_minutos=5
                )
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro check distância crítico: {str(e)}")
            return None
    
    def _check_score_risco_critico(self, analise_risco) -> Optional[AlertaCreate]:
        """3. Score Risco < 30 = Fechar posição"""
        try:
            if analise_risco.get("status") != "success":
                return None
            
            score_risco = analise_risco.get("score_consolidado", 100)
            
            if score_risco < 30:
                return AlertaCreate(
                    tipo=TipoAlerta.POSICAO,
                    categoria=CategoriaAlerta.CRITICO,
                    prioridade=0,
                    titulo="🚨 RISCO EXTREMO",
                    mensagem=f"Score {score_risco:.1f} - Fechar posição",
                    threshold_configurado=30.0,
                    valor_atual=score_risco,
                    dados_contexto={
                        "acao_recomendada": "Fechar posição completamente",
                        "risco": "Perda total possível",
                        "classificacao": analise_risco.get("classificacao", "crítico"),
                        "tipo_critico": "score_risco"
                    },
                    cooldown_minutos=10
                )
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro check score crítico: {str(e)}")
            return None
    
    def _check_portfolio_loss_critico(self, dados_risco) -> Optional[AlertaCreate]:
        """4. Portfolio Loss 24h > 20% = Stop Loss"""
        try:
            # Calcular perda 24h baseado nos dados atuais
            portfolio_loss_24h = self._calculate_portfolio_loss_24h(dados_risco)
            
            if portfolio_loss_24h and portfolio_loss_24h > 20:
                return AlertaCreate(
                    tipo=TipoAlerta.POSICAO,
                    categoria=CategoriaAlerta.CRITICO,
                    prioridade=0,
                    titulo="🚨 STOP LOSS",
                    mensagem=f"Perda -{portfolio_loss_24h:.1f}% em 24h - Avaliar saída",
                    threshold_configurado=20.0,
                    valor_atual=portfolio_loss_24h,
                    dados_contexto={
                        "acao_recomendada": "Avaliar saída completa da posição",
                        "risco": "Circuit breaker ativado",
                        "timeframe": "Imediato",
                        "tipo_critico": "portfolio_loss"
                    },
                    cooldown_minutos=15
                )
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro check portfolio loss: {str(e)}")
            return None
    
    def _check_overleveraged_critico(self, dados_risco, analise_alavancagem) -> Optional[AlertaCreate]:
        """5. Leverage > MVRV Max * 1.2 = OVERLEVERAGED"""
        try:
            if analise_alavancagem.get("status") != "success":
                return None
            
            # CORRIGIDO: Campo correto da tabela indicadores_risco
            alavancagem_atual = self._extract_leverage_value(dados_risco.get("alavancagem"))
            max_permitido = analise_alavancagem.get("alavancagem_recomendada", 2.0)
            threshold_critico = max_permitido * 1.2
            
            if alavancagem_atual and alavancagem_atual > threshold_critico:
                return AlertaCreate(
                    tipo=TipoAlerta.POSICAO,
                    categoria=CategoriaAlerta.CRITICO,
                    prioridade=0,
                    titulo="🚨 OVERLEVERAGED",
                    mensagem=f"{alavancagem_atual:.1f}x > {threshold_critico:.1f}x permitido",
                    threshold_configurado=threshold_critico,
                    valor_atual=alavancagem_atual,
                    dados_contexto={
                        "acao_recomendada": f"Reduzir para max {max_permitido:.1f}x",
                        "alavancagem_maxima": max_permitido,
                        "excesso_percentual": ((alavancagem_atual / threshold_critico) - 1) * 100,
                        "tipo_critico": "overleveraged"
                    },
                    cooldown_minutos=10
                )
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro check overleveraged: {str(e)}")
            return None
    
    def _extract_distance_value(self, dist_raw) -> Optional[float]:
        """Extrai valor numérico da distância"""
        if not dist_raw:
            return None
        
        try:
            if isinstance(dist_raw, str):
                return float(dist_raw.replace("%", ""))
            return float(dist_raw)
        except:
            return None
    
    def _extract_leverage_value(self, leverage_raw) -> Optional[float]:
        """Extrai valor numérico da alavancagem"""
        if not leverage_raw:
            return None
        
        try:
            if isinstance(leverage_raw, dict):
                return float(leverage_raw.get("valor_numerico", 0))
            return float(leverage_raw)
        except:
            return None
    
    def _calculate_portfolio_loss_24h(self, dados_risco) -> Optional[float]:
        """Calcula perda do portfólio em 24h"""
        try:
            # Usar dados do PostgreSQL se disponível
            # Por enquanto, mock baseado em variação do BTC
            from ...utils.helpers.price_helper import get_btc_price
            
            btc_atual = get_btc_price()
            net_asset_value = dados_risco.get("net_asset_value", 0)
            
            # Mock: assumir perda proporcional se NAV baixo
            if net_asset_value < 50000:  # Exemplo: se NAV < 50k = perda alta
                return 25.0  # Mock de 25% de perda
            
            return None  # Sem perda crítica detectada
            
        except Exception as e:
            logger.error(f"❌ Erro calculando portfolio loss: {str(e)}")
            return None

    def get_debug_info(self) -> dict:
        """Retorna informações completas para debug"""
        try:
            dados_risco = get_dados_risco()
            analise_risco = calcular_analise_risco()
            analise_alavancagem = calcular_analise_alavancagem()
            
            # Extrair todos os valores
            health_factor = float(dados_risco.get("health_factor", 999)) if dados_risco else None
            dist_liquidacao = self._extract_distance_value(dados_risco.get("dist_liquidacao")) if dados_risco else None
            score_risco = analise_risco.get("score_consolidado", 100) if analise_risco.get("status") == "success" else None
            portfolio_loss = self._calculate_portfolio_loss_24h(dados_risco) if dados_risco else None
            alavancagem_atual = self._extract_leverage_value(dados_risco.get("alavancagem")) if dados_risco else None
            max_leverage = analise_alavancagem.get("alavancagem_recomendada", 2.0) if analise_alavancagem.get("status") == "success" else None
            
            # Verificar cada alerta
            alertas_status = {
                "health_factor": {
                    "valor_atual": health_factor,
                    "threshold": 1.3,
                    "disparado": health_factor < 1.3 if health_factor else False,
                    "acao": "Reduzir 70% AGORA" if health_factor and health_factor < 1.3 else "Monitorar"
                },
                "distancia_liquidacao": {
                    "valor_atual": dist_liquidacao,
                    "threshold": 20.0,
                    "disparado": dist_liquidacao < 20 if dist_liquidacao else False,
                    "acao": "EMERGÊNCIA - Reduzir posição" if dist_liquidacao and dist_liquidacao < 20 else "Monitorar"
                },
                "score_risco": {
                    "valor_atual": score_risco,
                    "threshold": 30.0,
                    "disparado": score_risco < 30 if score_risco else False,
                    "acao": "Fechar posição" if score_risco and score_risco < 30 else "Monitorar"
                },
                "portfolio_loss_24h": {
                    "valor_atual": portfolio_loss,
                    "threshold": 20.0,
                    "disparado": portfolio_loss > 20 if portfolio_loss else False,
                    "acao": "Stop Loss ativado" if portfolio_loss and portfolio_loss > 20 else "Monitorar"
                },
                "overleveraged": {
                    "valor_atual": alavancagem_atual,
                    "threshold": max_leverage * 1.2 if max_leverage else None,
                    "disparado": alavancagem_atual > (max_leverage * 1.2) if alavancagem_atual and max_leverage else False,
                    "acao": f"Reduzir para {max_leverage:.1f}x" if alavancagem_atual and max_leverage and alavancagem_atual > (max_leverage * 1.2) else "Monitorar"
                }
            }
            
            return {
                "categoria": "CRÍTICOS - Posição",
                "timestamp": datetime.utcnow().isoformat(),
                "dados_coletados": {
                    "health_factor": health_factor,
                    "dist_liquidacao": dist_liquidacao,
                    "score_risco": score_risco,
                    "portfolio_loss_24h": portfolio_loss,
                    "alavancagem_atual": alavancagem_atual,
                    "max_leverage_permitido": max_leverage
                },
                "alertas_status": alertas_status,
                "total_disparados": sum(1 for a in alertas_status.values() if a["disparado"]),
                "fontes_dados": {
                    "dados_risco_ok": dados_risco is not None,
                    "analise_risco_ok": analise_risco.get("status") == "success",
                    "analise_alavancagem_ok": analise_alavancagem.get("status") == "success"
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Erro debug críticos: {str(e)}")
            return {
                "categoria": "CRÍTICOS - Posição",
                "timestamp": datetime.utcnow().isoformat(),
                "erro": str(e),
                "status": "error"
            }