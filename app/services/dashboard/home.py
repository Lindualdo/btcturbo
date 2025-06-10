# app/services/dashboard/home.py - CORRIGIDO

import logging
from datetime import datetime
from app.services.indicadores import riscos
from app.services.utils.helpers.postgres.dashboard_home_helper import (
    insert_dashboard_home_data, get_latest_dashboard_home, get_dashboard_home_stats
)

logger = logging.getLogger(__name__)

def calcular_dashboard_home():
    """
    FASE 1: Calcula e grava dados do dashboard home (apenas cabeçalho)
    
    Fluxo:
    1. Busca dados da API /obter-indicadores/riscos
    2. Extrai campos do cabeçalho 
    3. Calcula position_btc
    4. Monta JSON
    5. Grava no PostgreSQL
    """
    try:
        logger.info("🚀 FASE 1: Calculando dashboard home (cabeçalho)...")
        
        # 1. Buscar dados de risco
        logger.info("📊 Buscando dados de risco...")
        dados_riscos = riscos.obter_indicadores()
        
        if dados_riscos.get("status") != "success":
            raise Exception(f"Dados de risco indisponíveis: {dados_riscos.get('erro', 'status não success')}")
        
        # 2. Validar se posicao_atual existe
        posicao_atual = dados_riscos.get("posicao_atual")
        if not posicao_atual:
            raise Exception("Seção 'posicao_atual' não encontrada nos dados de risco")
        
        # 3. Extrair campos do cabeçalho
        try:
            btc_price = float(posicao_atual["btc_price"]["valor_numerico"])
            position_dolar = float(posicao_atual["posicao_total"]["valor_numerico"])
            alavancagem_atual = float(posicao_atual["alavancagem_atual"]["valor_numerico"])
            
            # Calcular position_btc
            position_btc = position_dolar / btc_price
            
            logger.info(f"✅ Dados extraídos:")
            logger.info(f"    BTC Price: ${btc_price:,.2f}")
            logger.info(f"    Position USD: ${position_dolar:,.2f}")
            logger.info(f"    Position BTC: {position_btc:.6f}")
            logger.info(f"    Alavancagem: {alavancagem_atual:.2f}x")
            
        except (KeyError, TypeError, ValueError) as e:
            raise Exception(f"Erro ao extrair campos da posição: {str(e)}")
        
        # 4. Montar JSON do dashboard (FASE 1)
        dashboard_json = {
            "fase": "1_cabecalho_apenas",
            "timestamp": datetime.utcnow().isoformat(),
            "cabecalho": {
                "btc_price": btc_price,
                "btc_price_formatado": f"${btc_price:,.0f}",
                "position_dolar": position_dolar,
                "position_dolar_formatado": f"${position_dolar:,.2f}",
                "position_btc": position_btc,
                "position_btc_formatado": f"{position_btc:.6f} BTC",
                "alavancagem_atual": alavancagem_atual,
                "alavancagem_formatado": f"{alavancagem_atual:.2f}x"
            },
            "metadata": {
                "fonte_dados": "obter-indicadores/riscos",
                "timestamp_fonte": dados_riscos.get("timestamp"),
                "versao": "fase_1"
            }
        }
        
        # 5. Gravar no PostgreSQL
        logger.info("💾 Gravando no PostgreSQL...")
        sucesso = insert_dashboard_home_data(
            btc_price=btc_price,
            position_dolar=position_dolar,
            position_btc=position_btc,
            alavancagem_atual=alavancagem_atual,
            dashboard_json=dashboard_json
        )
        
        if not sucesso:
            raise Exception("Falha ao gravar no PostgreSQL")
        
        # 6. Resposta de sucesso
        return {
            "status": "success",
            "fase": "1_cabecalho",
            "timestamp": datetime.utcnow().isoformat(),
            "dados_gravados": {
                "btc_price": btc_price,
                "position_dolar": position_dolar,
                "position_btc": position_btc,
                "alavancagem_atual": alavancagem_atual
            },
            "message": "Dashboard home FASE 1 calculado e gravado com sucesso"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro no cálculo dashboard home: {str(e)}")
        return {
            "status": "error",
            "fase": "1_cabecalho",
            "timestamp": datetime.utcnow().isoformat(),
            "erro": str(e),
            "message": "Falha no cálculo do dashboard home"
        }

def obter_dashboard_home():
    """
    FASE 1: Obtém dados do dashboard home do PostgreSQL
    
    Retorna JSON pronto para o frontend
    """
    try:
        logger.info("🔍 FASE 1: Obtendo dashboard home...")
        
        # Buscar último registro
        dados = get_latest_dashboard_home()
        
        if not dados:
            return {
                "status": "error",
                "erro": "Nenhum dado encontrado",
                "message": "Execute POST /dashboard-home primeiro"
            }
        
        # Retornar JSON do dashboard
        dashboard_json = dados["dashboard_json"]
        
        # Se dashboard_json é string, converter para dict
        if isinstance(dashboard_json, str):
            import json
            dashboard_json = json.loads(dashboard_json)
        
        logger.info(f"✅ Dashboard home obtido: {dados['created_at']}")
        
        return {
            "status": "success",
            "data": dashboard_json,
            "metadata": {
                "id": dados["id"],
                "created_at": dados["created_at"].isoformat(),
                "age_minutes": (datetime.utcnow() - dados["created_at"]).total_seconds() / 60
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter dashboard home: {str(e)}")
        return {
            "status": "error",
            "erro": str(e),
            "message": "Falha ao obter dashboard home"
        }

def debug_dashboard_home():
    """
    FASE 1: Debug/estatísticas do dashboard home
    """
    try:
        logger.info("🔍 Debug dashboard home...")
        
        # Buscar estatísticas
        stats = get_dashboard_home_stats()
        
        # Buscar último registro
        ultimo = get_latest_dashboard_home()
        
        return {
            "status": "success",
            "fase": "1_cabecalho",
            "estatisticas": stats,
            "ultimo_registro": {
                "id": ultimo["id"] if ultimo else None,
                "created_at": ultimo["created_at"].isoformat() if ultimo else None,
                "btc_price": ultimo["btc_price"] if ultimo else None,
                "alavancagem": ultimo["alavancagem_atual"] if ultimo else None
            } if ultimo else None,
            "tabela_existe": stats.get("total_registros", 0) >= 0
        }
        
    except Exception as e:
        logger.error(f"❌ Erro no debug: {str(e)}")
        return {
            "status": "error",
            "erro": str(e)
        }