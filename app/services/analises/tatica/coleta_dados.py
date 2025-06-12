# app/services/analises/tatica/coleta_dados.py

from datetime import datetime
import logging
from app.services.utils.helpers.tradingview.rsi_helper import obter_rsi_diario
from app.services.utils.helpers.analise.ema144_live_helper import obter_ema144_distance_atualizada
from app.services.utils.helpers.analise.simulacao_helper import obter_dados_posicao
from app.services.utils.helpers.tradingview.bbw_calculator import obter_bbw_com_score

# Importar services das outras camadas
from app.services.analises.analise_mercado import calcular_analise_mercado
from app.services.analises.analise_risco import calcular_analise_risco
from app.services.analises.analise_alavancagem import calcular_analise_alavancagem

logger = logging.getLogger(__name__)

def coletar_dados_todas_camadas():
    """
    Coleta dados das 4 camadas + dados táticos extras
    
    Returns:
        dict: Todos os dados necessários para análise tática
        
    Raises:
        Exception: Se dados críticos indisponíveis
    """
    try:
        logger.info("🎯 Coletando dados de todas as camadas...")
        
        # 1. Dados táticos básicos (EMA + RSI) - CRÍTICOS
        try:
            ema_distance = obter_ema144_distance_atualizada()
            rsi_diario = obter_rsi_diario()
            logger.info(f"✅ Dados táticos: EMA={ema_distance:+.1f}%, RSI={rsi_diario:.1f}")
        except Exception as e:
            raise Exception(f"Dados táticos indisponíveis: {str(e)}")
        
        # 2. Análise de Mercado (Camada 1) - CRÍTICA
        try:
            dados_mercado = calcular_analise_mercado()
            if dados_mercado.get("status") != "success":
                raise Exception(dados_mercado.get("erro", "Análise mercado falhou"))
            score_mercado = dados_mercado["score_consolidado"]
            logger.info(f"✅ Score Mercado: {score_mercado}")
        except Exception as e:
            raise Exception(f"Camada Mercado falhou: {str(e)}")
        
        # 3. Análise de Risco (Camada 2) - CRÍTICA
        try:
            dados_risco = calcular_analise_risco()
            if dados_risco.get("status") != "success":
                raise Exception(dados_risco.get("erro", "Análise risco falhou"))
            score_risco = dados_risco["score_consolidado"]
            logger.info(f"✅ Score Risco: {score_risco}")
        except Exception as e:
            raise Exception(f"Camada Risco falhou: {str(e)}")
        
        # 4. Análise de Alavancagem (Camada 3) - CRÍTICA
        try:
            dados_alavancagem = calcular_analise_alavancagem()
            if dados_alavancagem.get("status") != "success":
                raise Exception(dados_alavancagem.get("erro", "Análise alavancagem falhou"))
            
            # Extrair MVRV dos dados de alavancagem
            mvrv = dados_alavancagem["inputs"]["mvrv_z_score"]
            max_leverage_permitida = dados_alavancagem["parametros"]["max_leverage"]
            logger.info(f"✅ MVRV: {mvrv}, Max Leverage: {max_leverage_permitida}x")
        except Exception as e:
            raise Exception(f"Camada Alavancagem falhou: {str(e)}")
        
        # 5. Dados extras para cenários específicos
        dados_extras = {}
        try:
            posicao_atual = obter_dados_posicao()
            if posicao_atual and dados_risco.get("composicao", {}).get("breakdown"):
                breakdown_risco = dados_risco["composicao"]["breakdown"]
                
                # Health Factor - CRÍTICO
                hf_valor = breakdown_risco.get("health_factor", {}).get("valor_display")
                if not hf_valor or hf_valor == "N/A":
                    raise Exception("Health Factor indisponível")
                
                try:
                    dados_extras["health_factor"] = float(str(hf_valor).replace("$", "").replace(",", ""))
                except (ValueError, TypeError):
                    raise Exception(f"Health Factor inválido: {hf_valor}")
                
                # Distância Liquidação - CRÍTICA  
                dist_valor = breakdown_risco.get("dist_liquidacao", {}).get("valor_display")
                if not dist_valor or dist_valor == "N/A":
                    raise Exception("Distância liquidação indisponível")
                
                try:
                    dados_extras["dist_liquidacao"] = float(str(dist_valor).replace("%", ""))
                except (ValueError, TypeError):
                    raise Exception(f"Distância liquidação inválida: {dist_valor}")
                
                logger.info(f"✅ Dados extras: HF={dados_extras['health_factor']}, Dist={dados_extras['dist_liquidacao']}%")
            else:
                raise Exception("Dados de posição ou breakdown risco indisponíveis")
            
            # BBW - CRÍTICO para cenários específicos
            try:
                bbw_data = obter_bbw_com_score()
                if not bbw_data or "bbw_percentage" not in bbw_data:
                    raise Exception("BBW retornou dados inválidos")
                
                dados_extras["bbw_percentage"] = bbw_data["bbw_percentage"]
                
                estado = bbw_data.get("estado", "unknown")
                score_bbw = bbw_data.get("score_bbw", 0)
                logger.info(f"✅ BBW obtido: {dados_extras['bbw_percentage']:.2f}% ({estado}, score: {score_bbw})")
                
            except Exception as e:
                raise Exception(f"BBW indisponível: {str(e)}")
            
        except Exception as e:
            raise Exception(f"Dados extras falharam: {str(e)}")
        
        # Retornar dados consolidados
        return {
            "ema_distance": ema_distance,
            "rsi_diario": rsi_diario,
            "score_mercado": score_mercado,
            "score_risco": score_risco,
            "mvrv": mvrv,
            "max_leverage_permitida": max_leverage_permitida,
            "dados_extras": dados_extras,
            "posicao_atual": posicao_atual,
            # Objetos completos para resposta
            "dados_mercado": dados_mercado,
            "dados_risco": dados_risco,
            "dados_alavancagem": dados_alavancagem
        }
        
    except Exception as e:
        logger.error(f"❌ Erro na coleta de dados: {str(e)}")
        raise

def _erro_dados_criticos(componente: str, erro: str) -> dict:
    """Retorna erro padronizado para dados críticos indisponíveis"""
    return {
        "analise": "tatica_completa",
        "timestamp": datetime.utcnow().isoformat(),
        "status": "error",
        "erro": f"Dados críticos indisponíveis: {componente}",
        "detalhes": erro,
        "componente_faltante": componente,
        "acao_recomendada": f"Corrigir {componente} antes de tomar decisões táticas"
    }