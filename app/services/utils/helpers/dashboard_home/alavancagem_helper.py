# app/services/utils/helpers/dashboard_home/alavancagem_helper.py

import logging
from app.services.analises.analise_alavancagem import calcular_analise_alavancagem

logger = logging.getLogger(__name__)

def get_alavancagem_data() -> dict:
    """
    Coleta dados de gestão de alavancagem: capital livre, margem, stop loss, etc.
    
    Returns:
        dict com campos de gestão alavancagem ou erro
    """
    try:
        logger.info("📊 Coletando dados de gestão alavancagem...")
        
        # Buscar análise de alavancagem
        dados_alavancagem = calcular_analise_alavancagem()
        
        if dados_alavancagem.get("status") != "success":
            raise Exception(f"Dados de alavancagem indisponíveis: {dados_alavancagem.get('erro')}")
        
        # Extrair campos da análise alavancagem (CAMPOS REAIS)
        valor_disponivel = float(dados_alavancagem.get("valor_disponivel", 0))
        valor_a_reduzir = float(dados_alavancagem.get("valor_a_reduzir", 0))
        status = dados_alavancagem.get("status", "unknown")
        alavancagem_atual = float(dados_alavancagem.get("alavancagem_atual", 0))
        alavancagem_permitida = float(dados_alavancagem.get("alavancagem_permitida", 0))
        capital_liquido = float(dados_alavancagem.get("capital_liquido", 0))
        divida_total = float(dados_alavancagem.get("divida_total", 0))
        posicao_total = float(dados_alavancagem.get("posicao_total", 0))
        acao_simulacao = dados_alavancagem.get("acao_simulacao", "unknown")
        
        # Calcular margem percentual (atual vs permitida)
        margem_percentual = (alavancagem_atual / alavancagem_permitida) * 100 if alavancagem_permitida > 0 else 0
        
        # Extrair stop loss se existir
        stop_loss_percentual = float(dados_alavancagem.get("stop_loss", 10))  # fallback 10%
        
        logger.info(f"✅ Alavancagem: Permitida={alavancagem_permitida:.2f}x, Disponível=${valor_disponivel:,.0f}, Status={status}")
        
        return {
            "status": "success",
            "campos": {
                "valor_disponivel": valor_disponivel,
                "valor_a_reduzir": valor_a_reduzir,
                "status_alavancagem": status,
                "alavancagem_atual": alavancagem_atual,
                "alavancagem_permitida": alavancagem_permitida,
                "margem_percentual": margem_percentual
            },
            "json": {
                "valor_disponivel": valor_disponivel,
                "valor_disponivel_formatado": f"${valor_disponivel:,.2f}",
                "valor_a_reduzir": valor_a_reduzir,
                "valor_a_reduzir_formatado": f"${valor_a_reduzir:,.2f}",
                "status": status,
                "alavancagem_atual": alavancagem_atual,
                "alavancagem_atual_formatado": f"{alavancagem_atual:.2f}x",
                "alavancagem_permitida": alavancagem_permitida,
                "alavancagem_permitida_formatado": f"{alavancagem_permitida:.2f}x",
                "margem_percentual": margem_percentual,
                "margem_percentual_formatado": f"{margem_percentual:.1f}%",
                "acao_simulacao": acao_simulacao,
                "capital_liquido": capital_liquido,
                "capital_liquido_formatado": f"${capital_liquido:,.2f}",
                "divida_total": divida_total,
                "divida_total_formatado": f"${divida_total:,.2f}",
                "posicao_total": posicao_total,
                "posicao_total_formatado": f"${posicao_total:,.2f}"
            },
            "modulo": "alavancagem",
            "fonte": "analise-alavancagem"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro na gestão alavancagem: {str(e)}")
        return {
            "status": "error",
            "erro": str(e),
            "campos": {
                "valor_disponivel": 0.0,
                "valor_a_reduzir": 0.0,
                "status_alavancagem": "erro",
                "alavancagem_atual": 0.0,
                "alavancagem_permitida": 0.0,
                "margem_percentual": 0.0
            }
        }