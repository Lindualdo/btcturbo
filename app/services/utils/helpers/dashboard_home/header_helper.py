# app/services/utils/helpers/dashboard_home/header_helper.py

import logging
from app.services.indicadores import riscos

logger = logging.getLogger(__name__)

def get_header_data() -> dict:
    """
    Coleta dados do cabeçalho: BTC price, posição, alavancagem
    
    Returns:
        dict com campos do cabeçalho ou erro
    """
    try:
        logger.info("📊 Coletando dados do cabeçalho...")
        
        # Buscar dados de risco
        dados_riscos = riscos.obter_indicadores()
        
        if dados_riscos.get("status") != "success":
            raise Exception(f"Dados de risco indisponíveis: {dados_riscos.get('erro')}")
        
        # Validar posicao_atual
        posicao_atual = dados_riscos.get("posicao_atual")
        if not posicao_atual:
            raise Exception("Seção 'posicao_atual' não encontrada")
        
        # Extrair campos
        btc_price = float(posicao_atual["btc_price"]["valor_numerico"])
        position_dolar = float(posicao_atual["posicao_total"]["valor_numerico"])
        alavancagem_atual = float(posicao_atual["alavancagem_atual"]["valor_numerico"])
        
        # Calcular position_btc
        position_btc = position_dolar / btc_price
        
        logger.info(f"✅ Cabeçalho: BTC=${btc_price:,.0f}, Pos=${position_dolar:,.0f}, Alav={alavancagem_atual:.2f}x")
        
        return {
            "status": "success",
            "campos": {
                "btc_price": btc_price,
                "position_dolar": position_dolar,
                "position_btc": position_btc,
                "alavancagem_atual": alavancagem_atual
            },
            "json": {
                "btc_price": btc_price,
                "btc_price_formatado": f"${btc_price:,.0f}",
                "position_dolar": position_dolar,
                "position_dolar_formatado": f"${position_dolar:,.2f}",
                "position_btc": position_btc,
                "position_btc_formatado": f"{position_btc:.6f} BTC",
                "alavancagem_atual": alavancagem_atual,
                "alavancagem_formatado": f"{alavancagem_atual:.2f}x"
            },
            "modulo": "header",
            "fonte": "obter-indicadores/riscos"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro no cabeçalho: {str(e)}")
        return {
            "status": "error",
            "erro": str(e),
            "campos": {
                "btc_price": 0.0,
                "position_dolar": 0.0,
                "position_btc": 0.0,
                "alavancagem_atual": 0.0
            }
        }