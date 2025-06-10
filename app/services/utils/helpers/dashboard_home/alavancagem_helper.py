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
        
        # Extrair campos da situacao_atual (ESTRUTURA CORRETA)
        situacao_atual = dados_alavancagem.get("situacao_atual", {})
        
        # Função para limpar valores monetários
        def limpar_valor_monetario(valor_str):
            if isinstance(valor_str, str):
                return float(valor_str.replace("$", "").replace(",", ""))
            return float(valor_str) if valor_str else 0.0
        
        def limpar_alavancagem(valor_str):
            if isinstance(valor_str, str):
                return float(valor_str.replace("x", ""))
            return float(valor_str) if valor_str else 0.0
        
        # Extrair e limpar campos
        valor_disponivel = limpar_valor_monetario(situacao_atual.get("valor_disponivel", "$0.00"))
        valor_a_reduzir = limpar_valor_monetario(situacao_atual.get("valor_a_reduzir", "$0.00"))
        status = situacao_atual.get("status", "unknown")
        alavancagem_atual = limpar_alavancagem(situacao_atual.get("alavancagem_atual", "0x"))
        alavancagem_permitida = limpar_alavancagem(situacao_atual.get("alavancagem_permitida", "0x"))
        capital_liquido = limpar_valor_monetario(situacao_atual.get("capital_liquido", "$0.00"))
        divida_total = limpar_valor_monetario(situacao_atual.get("divida_total", "$0.00"))
        posicao_total = limpar_valor_monetario(situacao_atual.get("posicao_total", "$0.00"))
        acao_simulacao = situacao_atual.get("acao_simulacao", "unknown")
        
        # Extrair stop loss dos parametros
        parametros = dados_alavancagem.get("parametros", {})
        stop_loss_percentual = float(parametros.get("stop_loss_percent", 10))
        
        # Calcular margem percentual (atual vs permitida)
        margem_percentual = (alavancagem_atual / alavancagem_permitida) * 100 if alavancagem_permitida > 0 else 0
        
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
                "stop_loss_percentual": stop_loss_percentual,
                "stop_loss_formatado": f"-{stop_loss_percentual:.0f}%",
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