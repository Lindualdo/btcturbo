# app/services/utils/helpers/v3/data_builder_v3.py

import logging
from datetime import datetime
from typing import Dict

logger = logging.getLogger(__name__)

def build_dashboard_data(dados_mercado: dict, dados_risco: dict, dados_alavancagem: dict, mock_estrategia: dict) -> dict:
    """
    Constrói dados V3 formato compatível com JSON esperado
    
    Args:
        dados_mercado: Dados reais Camada 1
        dados_risco: Dados reais Camada 2  
        dados_alavancagem: Dados reais Camada 3
        mock_estrategia: Mock Camada 4 (temporário)
    """
    try:
        logger.info("🔧 Construindo dados Dashboard V3...")
        
        # Validar inputs obrigatórios
        if not dados_mercado:
            raise Exception("Dados mercado ausentes")
        if not dados_risco or dados_risco.get("status") != "success":  
            raise Exception("Dados risco inválidos")
        if not dados_alavancagem or dados_alavancagem.get("status") != "success":
            raise Exception("Dados alavancagem inválidos")
        
        # Extrair dados reais das camadas 1-3
        btc_price = _extract_btc_price(dados_mercado, dados_risco)
        position_usd = _extract_position_value(dados_risco)
        rsi_diario = _extract_rsi_diario()
        ema_data = _extract_ema_data()
        
        # Campos para PostgreSQL
        campos = {
            "btc_price": btc_price,
            "score_mercado": dados_mercado["score_mercado"],
            "score_risco": dados_risco["score"],
            "ciclo_atual": dados_mercado["ciclo"],
            "setup_4h": mock_estrategia.get("setup_4h", "INDEFINIDO"),
            "decisao_final": mock_estrategia.get("decisao", "AGUARDAR_IMPLEMENTACAO"),
            "alavancagem_atual": dados_alavancagem.get("alavancagem_atual", 0),
            "health_factor": dados_risco["health_factor"],
            "ema_distance": ema_data["distance"],
            "rsi_diario": rsi_diario
        }
        
        # JSON completo formato esperado
        dashboard_json = {
            "header": {
                "btc_price": campos["btc_price"],
                "position_usd": position_usd
            },
            "scores": {
                "ciclo": campos["ciclo_atual"],
                "risco": campos["score_risco"],
                "mercado": campos["score_mercado"],
                "classificacao_risco": dados_risco["classificacao"],
                "classificacao_mercado": dados_mercado["classificacao_mercado"]
            },
            "tecnicos": {
                "rsi": campos["rsi_diario"],
                "preco_ema144": ema_data["price"],
                "ema_144_distance": campos["ema_distance"]
            },
            "estrategia": {
                "decisao": campos["decisao_final"],
                "setup_4h": campos["setup_4h"],
                "urgencia": mock_estrategia.get("urgencia", "baixa"),
                "justificativa": mock_estrategia.get("justificativa", "Aguardando implementação Camada 4")
            },
            "alavancagem": {
                "atual": dados_alavancagem.get("alavancagem_atual", 0),
                "status": _determine_leverage_status(dados_alavancagem),
                "permitida": dados_alavancagem.get("alavancagem_permitida", 0),
                "divida_total": dados_alavancagem.get("divida_total", 0),
                "valor_a_reduzir": dados_alavancagem.get("valor_a_reduzir", 0),
                "valor_disponivel": dados_alavancagem.get("valor_disponivel", 0)
            },
            "indicadores": {
                "mvrv": dados_mercado["indicadores"]["mvrv"],
                "nupl": dados_mercado["indicadores"]["nupl"],
                "health_factor": campos["health_factor"],
                "dist_liquidacao": dados_risco["dist_liquidacao"]
            }
        }
        
        return {
            "campos": campos,
            "json": dashboard_json
        }
        
    except Exception as e:
        logger.error(f"❌ Erro construir dados V3: {str(e)}")
        raise Exception(f"Falha construir dados: {str(e)}")

def _extract_btc_price(dados_mercado: dict, dados_risco: dict) -> float:
    """Extrai preço BTC de fontes disponíveis"""
    try:
        # Tentar extrair de dados de risco primeiro
        if "btc_price" in dados_risco:
            return float(dados_risco["btc_price"])
        
        # Fallback: buscar via TradingView
        from app.services.utils.helpers.tradingview.price_helper import get_btc_price
        price = get_btc_price()
        logger.info(f"✅ BTC Price via TradingView: ${price:,.2f}")
        return price
        
    except Exception as e:
        logger.error(f"❌ Erro extrair BTC price: {str(e)}")
        raise Exception(f"BTC price indisponível: {str(e)}")

def _extract_position_value(dados_risco: dict) -> float:
    """Extrai valor posição de dados de risco"""
    try:
        # Buscar dados de posição
        from app.services.indicadores import riscos
        dados_pos = riscos.obter_indicadores()
        
        if dados_pos.get("status") == "success" and "posicao_atual" in dados_pos:
            posicao = dados_pos["posicao_atual"]
            if "posicao_total" in posicao:
                valor = posicao["posicao_total"].get("valor_numerico", 0)
                return float(valor) if valor else 0.0
        
        logger.warning("⚠️ Position USD não disponível")
        return 0.0
        
    except Exception as e:
        logger.error(f"❌ Erro extrair position value: {str(e)}")
        return 0.0

def _extract_rsi_diario() -> float:
    """Extrai RSI diário via TradingView"""
    try:
        from app.services.utils.helpers.tradingview.rsi_helper import obter_rsi_diario
        rsi = obter_rsi_diario()
        logger.info(f"✅ RSI Diário: {rsi:.1f}")
        return rsi
        
    except Exception as e:
        logger.error(f"❌ Erro RSI diário: {str(e)}")
        raise Exception(f"RSI diário indisponível: {str(e)}")

def _extract_ema_data() -> dict:
    """Extrai dados EMA144"""
    try:
        from app.services.indicadores import tecnico
        dados_tec = tecnico.obter_indicadores()
        
        if dados_tec.get("status") == "success":
            # Buscar EMA144 nos indicadores
            indicadores = dados_tec.get("indicadores", {})
            sistema_emas = indicadores.get("Sistema_EMAs", {})
            
            if "detalhes" in sistema_emas:
                detalhes = sistema_emas["detalhes"]
                diario = detalhes.get("diario", {})
                emas = diario.get("emas", {})
                ema144 = emas.get("ema144", {})
                
                if ema144:
                    return {
                        "price": ema144.get("valor", 0),
                        "distance": ema144.get("distancia_percentual", 0)
                    }
        
        logger.warning("⚠️ EMA144 não disponível")
        return {"price": 0, "distance": 0}
        
    except Exception as e:
        logger.error(f"❌ Erro EMA144: {str(e)}")
        return {"price": 0, "distance": 0}

def _determine_leverage_status(dados_alavancagem: dict) -> str:
    """Determina status alavancagem baseado nos dados reais"""
    try:
        atual = dados_alavancagem.get("alavancagem_atual", 0)
        permitida = dados_alavancagem.get("alavancagem_permitida", 0)
        
        if atual > permitida * 1.1:
            return "deve_reduzir"
        elif atual < permitida * 0.8:
            return "pode_aumentar"
        else:
            return "adequada"
            
    except Exception as e:
        logger.error(f"❌ Erro status alavancagem: {str(e)}")
        return "indefinido"

def build_response_format(dashboard_data: dict, record_id: int, timestamp: datetime) -> dict:
    """
    Constrói resposta final formato esperado
    """
    try:
        age_minutes = (datetime.utcnow() - timestamp).total_seconds() / 60
        
        return {
            "status": "success",
            "data": dashboard_data["json"],
            "metadata": {
                "id": record_id,
                "timestamp": timestamp.isoformat(),
                "age_minutes": round(age_minutes, 5),
                "versao": "v3_4_camadas"
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Erro construir resposta: {str(e)}")
        raise Exception(f"Falha construir resposta: {str(e)}")