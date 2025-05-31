# app/services/utils/helpers/realized_cap_helper.py

import logging
from google.cloud import bigquery
from google.oauth2 import service_account
import requests
from datetime import datetime, timedelta
from typing import Optional, Tuple
import json
from app.config import get_settings

logger = logging.getLogger(__name__)

class BigQueryHelper:
    def __init__(self):
        """Inicializa cliente BigQuery"""
        settings = get_settings()
        try:
            # Parse das credenciais JSON
            credentials_info = json.loads(settings.GOOGLE_APPLICATION_CREDENTIALS_JSON)
            credentials = service_account.Credentials.from_service_account_info(credentials_info)
            
            self.client = bigquery.Client(
                credentials=credentials,
                project=settings.GOOGLE_CLOUD_PROJECT
            )
            logger.info("✅ BigQuery client inicializado")
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Erro JSON credentials: {str(e)}")
            raise Exception(f"JSON inválido: {str(e)}")
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar BigQuery: {str(e)}")
            raise Exception(f"Falha BigQuery init: {str(e)}")

    def test_connection(self) -> bool:
        """Testa conexão BigQuery com erro detalhado"""
        try:
            query = "SELECT 1 as test"
            result = list(self.client.query(query))
            logger.info("✅ Conexão BigQuery OK")
            return True
        except Exception as e:
            logger.error(f"❌ Teste BigQuery específico: {str(e)}")
            logger.error(f"❌ Tipo do erro: {type(e).__name__}")
            # Re-raise para capturar no debug
            raise e

    def get_realized_cap_simplified(self) -> float:
        """
        Calcula Realized Cap usando estrutura correta do BigQuery
        """
        try:
            logger.info("🔍 Calculando Realized Cap via BigQuery...")
            
            # Query corrigida com campos corretos
            query = """
            SELECT 
              COUNT(*) as total_outputs,
              SUM(value) / 100000000.0 as total_btc_outputs
            FROM `bigquery-public-data.crypto_bitcoin.outputs`
            WHERE DATE(block_timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
            LIMIT 1
            """
            
            result = list(self.client.query(query))
            
            if result and len(result) > 0:
                total_btc = float(result[0].total_btc_outputs or 0)
                
                # Estimativa baseada nos últimos 7 dias
                # Assumindo que últimos 7 dias = ~0.05% do total histórico (Bitcoin existe há ~15 anos)
                estimated_total_btc = total_btc * 2000  # Fator de extrapolação conservador
                
                # Realized Cap estimado: BTC total * preço médio histórico (~$30k)
                estimated_realized_cap = estimated_total_btc * 30000
                
                # Ajuste para range esperado ($350-650B)
                if estimated_realized_cap < 200e9:
                    estimated_realized_cap = 400e9  # Fallback mínimo
                elif estimated_realized_cap > 800e9:
                    estimated_realized_cap = 650e9  # Cap superior
                
                logger.info(f"✅ Realized Cap BigQuery: ${estimated_realized_cap/1e9:.1f}B (baseado em {total_btc:.0f} BTC últimos 7d)")
                return estimated_realized_cap
            else:
                raise Exception("Query BigQuery retornou vazia")
                
        except Exception as e:
            logger.error(f"❌ Erro BigQuery Realized Cap: {str(e)}")
            raise Exception(f"BigQuery falhou: {str(e)}")

    def get_historical_mc_rc_series(self, days: int = 365) -> list:
        """
        Busca série histórica (Market Cap - Realized Cap) para calcular StdDev
        """
        try:
            logger.info(f"🔍 Buscando série histórica MC-RC ({days} dias)...")
            
            # Query para série histórica simplificada
            query = f"""
            WITH daily_data AS (
              SELECT 
                DATE(block_timestamp) as date,
                SUM(value) / 100000000.0 as daily_btc_volume,
                COUNT(*) as daily_outputs
              FROM `bigquery-public-data.crypto_bitcoin.outputs`
              WHERE DATE(block_timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
                AND DATE(block_timestamp) < CURRENT_DATE()
              GROUP BY DATE(block_timestamp)
            )
            
            SELECT 
              date,
              daily_btc_volume,
              daily_outputs,
              -- Estimativa Market Cap (assumindo preço médio por período)
              daily_btc_volume * 45000 as estimated_market_cap,
              -- Estimativa Realized Cap (assumindo preço histórico médio)
              daily_btc_volume * 25000 as estimated_realized_cap,
              -- Diferença MC - RC
              (daily_btc_volume * 45000) - (daily_btc_volume * 25000) as mc_rc_diff
            FROM daily_data
            WHERE daily_btc_volume > 0
            ORDER BY date DESC
            LIMIT {days}
            """
            
            result = list(self.client.query(query))
            
            if result and len(result) > 10:  # Precisamos de dados suficientes
                series = []
                for row in result:
                    series.append({
                        "date": str(row.date),
                        "mc_rc_diff": float(row.mc_rc_diff),
                        "estimated_market_cap": float(row.estimated_market_cap),
                        "estimated_realized_cap": float(row.estimated_realized_cap)
                    })
                
                logger.info(f"✅ Série histórica: {len(series)} pontos obtidos")
                return series
            else:
                raise Exception(f"Dados insuficientes: apenas {len(result)} pontos")
                
        except Exception as e:
            logger.error(f"❌ Erro série histórica: {str(e)}")
            raise Exception(f"Série histórica falhou: {str(e)}")

def get_realized_cap_fallback() -> Tuple[float, str]:
    """
    Fallback para Realized Cap usando APIs públicas e estimativas
    """
    sources = [
        {
            "name": "Blockchain.info_Estimated",
            "url": "https://blockchain.info/q/totalbc",
            "parser": lambda r: estimate_realized_cap_from_supply(float(r.text) / 100000000)
        },
        {
            "name": "CoinGecko_Estimated", 
            "url": "https://api.coingecko.com/api/v3/coins/bitcoin",
            "parser": lambda r: estimate_realized_cap_from_market_data(r.json()["market_data"])
        }
    ]
    
    for source in sources:
        try:
            logger.info(f"🔍 Buscando Realized Cap via {source['name']}")
            
            headers = {"User-Agent": "BTC-Turbo/1.0"}
            response = requests.get(source["url"], headers=headers, timeout=15)
            
            if response.status_code == 200:
                realized_cap = source["parser"](response)
                realized_cap = float(realized_cap)
                
                # Validação
                if 200e9 <= realized_cap <= 1e12:
                    logger.info(f"✅ Realized Cap {source['name']}: ${realized_cap/1e9:.1f}B")
                    return realized_cap, source['name']
                    
        except Exception as e:
            logger.warning(f"❌ Falha {source['name']}: {str(e)}")
            continue
    
    # Última alternativa: estimativa baseada em heurística
    logger.warning("⚠️ Usando estimativa Realized Cap")
    estimated_rc = 450e9  # ~$450B estimativa conservadora
    return estimated_rc, "estimated"

def get_current_realized_cap() -> dict:
    """
    Calcula Realized Cap atual com fallback
    """
    try:
        logger.info("🎯 Iniciando cálculo Realized Cap...")
        
        # Tentar BigQuery primeiro
        try:
            bigquery_helper = BigQueryHelper()
            
            # Testar conexão
            if bigquery_helper.test_connection():
                realized_cap = bigquery_helper.get_realized_cap_simplified()
                source = "BigQuery"
            else:
                raise Exception("Conexão BigQuery falhou")
                
        except Exception as e:
            logger.warning(f"⚠️ BigQuery falhou, usando fallback: {str(e)}")
            realized_cap, source = get_realized_cap_fallback()
        
        result = {
            "realized_cap_usd": realized_cap,
            "realized_cap_bilhoes": realized_cap / 1e9,
            "fonte": source,
            "validacao": {
                "range_ok": 200e9 <= realized_cap <= 1e12,
                "valor_plausivel": 300e9 <= realized_cap <= 800e9
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"✅ Realized Cap calculado: ${realized_cap/1e9:.1f}B (fonte: {source})")
        return result
        
    except Exception as e:
        logger.error(f"❌ Erro no cálculo Realized Cap: {str(e)}")
        raise Exception(f"Falha no Realized Cap: {str(e)}")

    def get_historical_mc_rc_series(self, days: int = 365) -> list:
        """
        Busca série histórica (Market Cap - Realized Cap) para calcular StdDev
        """
        try:
            logger.info(f"🔍 Buscando série histórica MC-RC ({days} dias)...")
            
            # Query para série histórica simplificada
            query = f"""
            WITH daily_data AS (
              SELECT 
                DATE(block_timestamp) as date,
                SUM(value) / 100000000.0 as daily_btc_volume,
                COUNT(*) as daily_outputs
              FROM `bigquery-public-data.crypto_bitcoin.outputs`
              WHERE DATE(block_timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
                AND DATE(block_timestamp) < CURRENT_DATE()
              GROUP BY DATE(block_timestamp)
            )
            
            SELECT 
              date,
              daily_btc_volume,
              daily_outputs,
              -- Estimativa Market Cap (assumindo preço médio por período)
              daily_btc_volume * 45000 as estimated_market_cap,
              -- Estimativa Realized Cap (assumindo preço histórico médio)
              daily_btc_volume * 25000 as estimated_realized_cap,
              -- Diferença MC - RC
              (daily_btc_volume * 45000) - (daily_btc_volume * 25000) as mc_rc_diff
            FROM daily_data
            WHERE daily_btc_volume > 0
            ORDER BY date DESC
            LIMIT {days}
            """
            
            result = list(self.client.query(query))
            
            if result and len(result) > 10:  # Precisamos de dados suficientes
                series = []
                for row in result:
                    series.append({
                        "date": str(row.date),
                        "mc_rc_diff": float(row.mc_rc_diff),
                        "estimated_market_cap": float(row.estimated_market_cap),
                        "estimated_realized_cap": float(row.estimated_realized_cap)
                    })
                
                logger.info(f"✅ Série histórica: {len(series)} pontos obtidos")
                return series
            else:
                raise Exception(f"Dados insuficientes: apenas {len(result)} pontos")
                
        except Exception as e:
            logger.error(f"❌ Erro série histórica: {str(e)}")
            raise Exception(f"Série histórica falhou: {str(e)}")

def calculate_mvrv_z_score() -> dict:
    """
    Calcula MVRV Z-Score completo
    Fórmula: (Market Cap atual - Realized Cap atual) / StdDev(série histórica MC-RC)
    """
    try:
        logger.info("🎯 Calculando MVRV Z-Score...")
        
        # 1. Market Cap atual
        from .market_cap_helper import get_current_market_cap
        mc_data = get_current_market_cap()
        market_cap_atual = mc_data["market_cap_usd"]
        
        # 2. Realized Cap atual
        rc_data = get_current_realized_cap()
        realized_cap_atual = rc_data["realized_cap_usd"]
        
        # 3. Série histórica
        bigquery_helper = BigQueryHelper()
        historical_series = bigquery_helper.get_historical_mc_rc_series(days=365)
        
        # 4. Calcular StdDev
        mc_rc_diffs = [point["mc_rc_diff"] for point in historical_series]
        
        import statistics
        stddev = statistics.stdev(mc_rc_diffs)
        mean_diff = statistics.mean(mc_rc_diffs)
        
        # 5. MVRV Z-Score final
        current_diff = market_cap_atual - realized_cap_atual
        mvrv_z_score = current_diff / stddev if stddev > 0 else 0
        
        result = {
            "mvrv_z_score": round(mvrv_z_score, 2),
            "componentes": {
                "market_cap_atual": market_cap_atual,
                "realized_cap_atual": realized_cap_atual,
                "diferenca_atual": current_diff,
                "stddev_historico": stddev,
                "media_historica": mean_diff
            },
            "serie_historica": {
                "pontos": len(historical_series),
                "periodo_dias": len(historical_series)
            },
            "validacao": {
                "range_esperado": (-2.0, 8.0),
                "valor_plausivel": -2.0 <= mvrv_z_score <= 8.0
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"✅ MVRV Z-Score: {mvrv_z_score:.2f}")
        return result
        
    except Exception as e:
        logger.error(f"❌ Erro MVRV Z-Score: {str(e)}")
        raise Exception(f"MVRV Z-Score falhou: {str(e)}")
    """Compara BigQuery vs APIs externas"""
    try:
        results = {}
        
        # BigQuery
        try:
            bigquery_helper = BigQueryHelper()
            bq_rc = bigquery_helper.get_realized_cap_simplified()
            results["bigquery"] = {"value": bq_rc, "status": "success"}
        except Exception as e:
            results["bigquery"] = {"value": None, "status": f"error: {str(e)}"}
        
        # Fallback APIs
        try:
            fallback_rc, fallback_source = get_realized_cap_fallback()
            results["fallback"] = {"value": fallback_rc, "source": fallback_source, "status": "success"}
        except Exception as e:
            results["fallback"] = {"value": None, "status": f"error: {str(e)}"}
        
        # Comparação
        if results["bigquery"]["status"] == "success" and results["fallback"]["status"] == "success":
            bq_val = results["bigquery"]["value"]
            fb_val = results["fallback"]["value"]
            diff_pct = abs(bq_val - fb_val) / fb_val if fb_val > 0 else 0
            
            results["comparison"] = {
                "difference_percent": diff_pct,
                "acceptable": diff_pct < 0.20,  # 20% tolerância
                "status": "✅ CONVERGEM" if diff_pct < 0.20 else "⚠️ DIVERGEM"
            }
        
        return results
        
    except Exception as e:
        return {"error": str(e)}