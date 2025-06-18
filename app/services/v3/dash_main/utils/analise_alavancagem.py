# app/services/v3/dash_main/utils/analise_alavancagem.py

import logging
from datetime import datetime
from typing import Dict
from app.services.utils.helpers.tradingview.rsi_helper import obter_rsi_mensal_para_alavancagem

logger = logging.getLogger(__name__)

def executar_analise_alavancagem(dados_mercado: dict, dados_risco: dict) -> dict:
    """
    Camada 3: Análise Alavancagem
    
    Input: Score mercado + indicadores ciclo + RSI mensal
    Output: Limite margem alavancagem (max 3x)
    """
    try:
        logger.info("⚖️ Executando Camada 3: Análise Alavancagem...")
        
        # 1. Extrair inputs necessários
        score_mercado = dados_mercado["score_mercado"]
        mvrv = dados_mercado["indicadores"]["mvrv"]
        
        # 2. Buscar RSI Mensal via TradingView
        rsi_mensal = obter_rsi_mensal_para_alavancagem()
        
        # 3. Calcular alavancagem máxima pela tabela
        alavancagem_maxima = _calcular_alavancagem_maxima(mvrv, rsi_mensal, score_mercado)
        
        # 4. Aplicar fator redutor por score mercado
        fator_redutor = _obter_fator_redutor(score_mercado)
        alavancagem_permitida = alavancagem_maxima * fator_redutor
        
        # 5. Aplicar proteções adicionais
        protecoes = _aplicar_protecoes(score_mercado, dados_mercado, dados_risco)
        if protecoes["bloqueado"]:
            alavancagem_permitida = 0.0
        
        # 5. Buscar dados posição atual para cálculos financeiros
        dados_posicao = _obter_dados_posicao()
        
        # 6. Calcular simulação financeira usando fórmula V2 exata
        simulacao = _calcular_simulacao_financeira(dados_posicao, alavancagem_permitida)
        
        # 7. Construir resposta
        return {
            "status": "success",
            "alavancagem_maxima": round(alavancagem_maxima, 1),
            "alavancagem_permitida": round(alavancagem_permitida, 1),
            "alavancagem_atual": dados_posicao.get("alavancagem_atual", 0),
            "fator_redutor": fator_redutor,
            "posicao_financeira": {
                "divida_total": dados_posicao.get("divida_total", 0),
                "capital_liquido": dados_posicao.get("capital_liquido", 0),
                "posicao_total": dados_posicao.get("posicao_total", 0),
                "valor_disponivel": simulacao.get("valor_disponivel", 0),
                "valor_a_reduzir": simulacao.get("valor_a_reduzir", 0),
                "status_posicao": simulacao.get("status", "indefinido")
            },
            "inputs": {
                "mvrv": mvrv,
                "rsi_mensal": round(rsi_mensal, 1),
                "score_mercado": score_mercado
            },
            "protecoes": protecoes,
            "detalhes_calculo": f"Base {alavancagem_maxima}x × Redutor {fator_redutor} = {alavancagem_permitida:.1f}x",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Erro Camada 3 Alavancagem: {str(e)}")
        return {
            "status": "error",
            "erro": str(e),
            "alavancagem_permitida": 0.0,
            "timestamp": datetime.utcnow().isoformat()
        }

def _calcular_alavancagem_maxima(mvrv: float, rsi_mensal: float, score_mercado: float) -> float:
    """
    Tabela principal MVRV × RSI × Score → Alavancagem máxima
    """
    # Regras prioritárias
    if score_mercado < 50:
        return 0.0  # Bloqueado se mercado ruim
    
    if rsi_mensal > 80:
        return 1.5  # Proteção RSI extremo
    
    if mvrv > 3.0:
        return 1.5  # Proteção MVRV alto
    
    # Tabela principal
    if mvrv < 1.0 and rsi_mensal < 30 and score_mercado > 70:
        return 3.0
    elif mvrv < 1.0 and rsi_mensal < 30 and 50 <= score_mercado <= 70:
        return 2.5
    elif mvrv < 1.0 and 30 <= rsi_mensal <= 50 and score_mercado > 60:
        return 2.5
    elif 1.0 <= mvrv <= 2.0 and 30 <= rsi_mensal <= 50 and score_mercado > 60:
        return 2.5
    elif 1.0 <= mvrv <= 2.0 and 50 <= rsi_mensal <= 70 and score_mercado > 60:
        return 2.0
    elif 2.0 <= mvrv <= 3.0 and 30 <= rsi_mensal <= 70 and score_mercado > 50:
        return 2.0
    elif 2.0 <= mvrv <= 3.0 and rsi_mensal > 70 and score_mercado > 50:
        return 1.5
    else:
        return 1.5  # Fallback conservador

def _obter_fator_redutor(score_mercado: float) -> float:
    """
    Fator redutor baseado no score de mercado
    """
    if 40 <= score_mercado < 50:
        return 0.5
    elif 50 <= score_mercado < 60:
        return 0.8
    elif 60 <= score_mercado <= 80:
        return 1.0
    elif score_mercado > 80:
        return 0.8  # Proteção topo
    else:
        return 0.0  # Bloqueado

def _aplicar_protecoes(score_mercado: float, dados_mercado: dict, dados_risco: dict) -> dict:
    """
    Proteções adicionais conforme especificação
    """
    protecoes_ativas = []
    bloqueado = False
    
    # Verificar health factor crítico
    health_factor = dados_risco.get("health_factor", 0)
    if health_factor < 1.3:
        protecoes_ativas.append("Health Factor crítico < 1.3")
        bloqueado = True
    
    # Score risco muito baixo (converter para base 100)
    score_risco = dados_risco.get("score", 0) * 10  # Converter base 10 → 100
    if score_risco < 40:
        protecoes_ativas.append(f"Score risco crítico < 40 (atual: {score_risco})")
        bloqueado = True
    
    # Divergência entre componentes mercado (implementar quando tiver dados)
    # Acumulação prolongada (implementar quando tiver histórico)
    
    return {
        "bloqueado": bloqueado,
        "protecoes_ativas": protecoes_ativas,
        "total_protecoes": len(protecoes_ativas)
    }

def _obter_dados_posicao() -> dict:
    """Extrai dados financeiros da posição atual"""
    try:
        from app.services.indicadores import riscos
        dados_pos = riscos.obter_indicadores()
        
        if dados_pos.get("status") != "success":
            logger.warning("⚠️ Dados posição indisponíveis")
            return {}
        
        posicao = dados_pos.get("posicao_atual", {})
        
        # Extrair valores numéricos - mapeamento correto V2
        alavancagem_atual = posicao.get("alavancagem_atual", {}).get("valor_numerico", 0)
        divida_total = posicao.get("divida_total", {}).get("valor_numerico", 0)  # total_borrowed
        capital_liquido = posicao.get("capital_liquido", {}).get("valor_numerico", 0)  # net_asset_value
        posicao_total = posicao.get("posicao_total", {}).get("valor_numerico", 0)  # supplied_asset_value
        
        return {
            "alavancagem_atual": float(alavancagem_atual) if alavancagem_atual else 0,
            "divida_total": float(divida_total) if divida_total else 0,
            "capital_liquido": float(capital_liquido) if capital_liquido else 0,
            "posicao_total": float(posicao_total) if posicao_total else 0
        }
        
    except Exception as e:
        logger.error(f"❌ Erro dados posição: {str(e)}")
        return {}

def _calcular_simulacao_financeira(dados_posicao: dict, alavancagem_permitida: float) -> dict:
    """FÓRMULA V2 EXATA com max_leverage da V3"""
    try:
        capital_liquido = dados_posicao.get("capital_liquido", 0)
        posicao_atual_total = dados_posicao.get("posicao_total", 0)
        
        if capital_liquido <= 0:
            logger.warning("⚠️ Capital líquido inválido")
            return {"status": "erro", "valor_disponivel": 0, "valor_a_reduzir": 0}
        
        # FÓRMULA V2 EXATA
        posicao_alvo = alavancagem_permitida * capital_liquido
        diferenca = posicao_alvo - posicao_atual_total
        
        logger.info(f"📊 V2 Formula: Alvo=${posicao_alvo:,.0f} - Atual=${posicao_atual_total:,.0f} = ${diferenca:,.0f}")
        
        if diferenca > 0:
            # Pode aumentar alavancagem
            status = "pode_aumentar"
            valor_disponivel = diferenca
            valor_a_reduzir = 0
        elif diferenca < 0:
            # Deve reduzir alavancagem
            status = "deve_reduzir"
            valor_disponivel = 0
            valor_a_reduzir = abs(diferenca)
        else:
            # Exatamente no limite
            status = "adequada"
            valor_disponivel = 0
            valor_a_reduzir = 0
            
        return {
            "status": status,
            "valor_disponivel": valor_disponivel,
            "valor_a_reduzir": valor_a_reduzir
        }
            
    except Exception as e:
        logger.error(f"❌ Erro simulação financeira: {str(e)}")
        return {"status": "erro", "valor_disponivel": 0, "valor_a_reduzir": 0}