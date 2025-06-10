# app/services/dashboard/home.py - CORRIGIDO

import logging
from datetime import datetime
from app.services.indicadores import riscos, ciclos
from app.services.analises.analise_mercado import calcular_analise_mercado
from app.services.utils.helpers.postgres.dashboard_home_helper import (
    insert_dashboard_home_data, get_latest_dashboard_home
)

logger = logging.getLogger(__name__)

def calcular_dashboard_home():
    """
    FASE 2: Calcula e grava dados do dashboard home (cabeçalho + score mercado)
    
    Fluxo:
    1. Busca dados da API /obter-indicadores/riscos
    2. Busca dados da API /analise-mercado
    3. Busca dados da API /obter-indicadores/ciclos
    4. Extrai campos do cabeçalho + score mercado
    5. Monta JSON
    6. Grava no PostgreSQL
    """
    try:
        logger.info("🚀 FASE 2: Calculando dashboard home (cabeçalho + score mercado)...")
        
        # 1. Buscar dados de risco
        logger.info("📊 Buscando dados de risco...")
        dados_riscos = riscos.obter_indicadores()
        
        if dados_riscos.get("status") != "success":
            raise Exception(f"Dados de risco indisponíveis: {dados_riscos.get('erro', 'status não success')}")
        
        # 2. Buscar dados de score mercado
        logger.info("📊 Buscando dados de score mercado...")
        dados_mercado = calcular_analise_mercado()
        
        if dados_mercado.get("status") != "success":
            raise Exception(f"Dados de mercado indisponíveis: {dados_mercado.get('erro', 'status não success')}")
        
        # 3. Buscar dados de ciclos para MVRV e NUPL
        logger.info("📊 Buscando dados de ciclos...")
        dados_ciclos = ciclos.obter_indicadores()
        
        if dados_ciclos.get("status") != "success":
            raise Exception(f"Dados de ciclos indisponíveis: {dados_ciclos.get('erro', 'status não success')}")
        
        # 4. Validar se posicao_atual existe
        posicao_atual = dados_riscos.get("posicao_atual")
        if not posicao_atual:
            raise Exception("Seção 'posicao_atual' não encontrada nos dados de risco")
        
        # 5. Extrair campos do cabeçalho
        try:
            btc_price = float(posicao_atual["btc_price"]["valor_numerico"])
            position_dolar = float(posicao_atual["posicao_total"]["valor_numerico"])
            alavancagem_atual = float(posicao_atual["alavancagem_atual"]["valor_numerico"])
            
            # Calcular position_btc
            position_btc = position_dolar / btc_price
            
            # Extrair campos score mercado
            score_mercado = float(dados_mercado["score_consolidado"])
            score_mercado_classificacao = dados_mercado["classificacao"]
            
            # Extrair MVRV e NUPL dos ciclos
            mvrv_valor = float(dados_ciclos["indicadores"]["MVRV_Z"]["valor"])
            nupl_valor = float(dados_ciclos["indicadores"]["NUPL"]["valor"]) if dados_ciclos["indicadores"]["NUPL"]["valor"] is not None else 0.0
            
            logger.info(f"✅ Dados extraídos:")
            logger.info(f"    BTC Price: ${btc_price:,.2f}")
            logger.info(f"    Position USD: ${position_dolar:,.2f}")
            logger.info(f"    Position BTC: {position_btc:.6f}")
            logger.info(f"    Alavancagem: {alavancagem_atual:.2f}x")
            logger.info(f"    Score Mercado: {score_mercado} ({score_mercado_classificacao})")
            logger.info(f"    MVRV: {mvrv_valor}")
            logger.info(f"    NUPL: {nupl_valor}")
            
        except (KeyError, TypeError, ValueError) as e:
            raise Exception(f"Erro ao extrair campos: {str(e)}")
        
        # 6. Montar JSON do dashboard (FASE 2)
        dashboard_json = {
            "fase": "2_cabecalho_score_mercado",
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
            "score_mercado": {
                "score": score_mercado,
                "score_formatado": f"{score_mercado:.1f}",
                "classificacao": score_mercado_classificacao,
                "mvrv": mvrv_valor,
                "mvrv_formatado": f"{mvrv_valor:.2f}",
                "nupl": nupl_valor,
                "nupl_formatado": f"{nupl_valor:.3f}"
            },
            "metadata": {
                "fonte_risco": "obter-indicadores/riscos",
                "fonte_mercado": "analise-mercado",
                "fonte_ciclos": "obter-indicadores/ciclos",
                "timestamp_fonte": dados_riscos.get("timestamp"),
                "versao": "fase_2"
            }
        }
        
        # 7. Gravar no PostgreSQL
        logger.info("💾 Gravando no PostgreSQL...")
        sucesso = insert_dashboard_home_data(
            btc_price=btc_price,
            position_dolar=position_dolar,
            position_btc=position_btc,
            alavancagem_atual=alavancagem_atual,
            score_mercado=score_mercado,
            score_mercado_classificacao=score_mercado_classificacao,
            mvrv_valor=mvrv_valor,
            nupl_valor=nupl_valor,
            dashboard_json=dashboard_json
        )
        
        if not sucesso:
            raise Exception("Falha ao gravar no PostgreSQL")
        
        # 8. Resposta de sucesso
        return {
            "status": "success",
            "fase": "2_cabecalho_score_mercado",
            "timestamp": datetime.utcnow().isoformat(),
            "dados_gravados": {
                "btc_price": btc_price,
                "position_dolar": position_dolar,
                "position_btc": position_btc,
                "alavancagem_atual": alavancagem_atual,
                "score_mercado": score_mercado,
                "score_mercado_classificacao": score_mercado_classificacao,
                "mvrv_valor": mvrv_valor,
                "nupl_valor": nupl_valor
            },
            "message": "Dashboard home FASE 2 calculado e gravado com sucesso"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro no cálculo dashboard home: {str(e)}")
        return {
            "status": "error",
            "fase": "2_cabecalho_score_mercado",
            "timestamp": datetime.utcnow().isoformat(),
            "erro": str(e),
            "message": "Falha no cálculo do dashboard home FASE 2"
        }

def obter_dashboard_home():
    """
    FASE 1: Obtém dados do dashboard home do PostgreSQL
    
    Retorna JSON pronto para o frontend
    """
    try:
        logger.info("🔍 FASE 2: Obtendo dashboard home...")
        
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
    FASE 2: Debug simples do dashboard home
    """
    try:
        logger.info("🔍 Debug dashboard home...")
        
        # Buscar último registro
        ultimo = get_latest_dashboard_home()
        
        return {
            "status": "success",
            "ultimo_registro": {
                "id": ultimo["id"] if ultimo else None,
                "created_at": ultimo["created_at"].isoformat() if ultimo else None,
                "btc_price": ultimo["btc_price"] if ultimo else None,
                "alavancagem": ultimo["alavancagem_atual"] if ultimo else None,
                "score_mercado": ultimo.get("score_mercado") if ultimo else None
            } if ultimo else None,
            "tem_dados": ultimo is not None
        }
        
    except Exception as e:
        logger.error(f"❌ Erro no debug: {str(e)}")
        return {
            "status": "error",
            "erro": str(e)
        }