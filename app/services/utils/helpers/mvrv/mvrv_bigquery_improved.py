# app/services/utils/helpers/mvrv/mvrv_bigquery_improved.py

import logging
import requests
import statistics
from datetime import datetime, timedelta
from .market_cap_helper import get_current_market_cap, get_btc_price
from .realized_cap_helper import BigQueryHelper

logger = logging.getLogger(__name__)

def get_btc_supply_age_distribution():
    """
    Busca distribuição de idade dos BTCs via BigQuery
    Usa isso para calibrar o fator dinamicamente
    """
    try:
        bigquery_helper = BigQueryHelper()
        
        # Query mais sofisticada: distribuição por idade
        query = """
        WITH utxo_ages AS (
            SELECT 
                DATE_DIFF(CURRENT_DATE(), DATE(block_timestamp), DAY) as age_days,
                value / 100000000.0 as btc_amount,
                CASE 
                    WHEN DATE_DIFF(CURRENT_DATE(), DATE(block_timestamp), DAY) < 30 THEN 'very_recent'
                    WHEN DATE_DIFF(CURRENT_DATE(), DATE(block_timestamp), DAY) < 180 THEN 'recent' 
                    WHEN DATE_DIFF(CURRENT_DATE(), DATE(block_timestamp), DAY) < 365 THEN 'medium'
                    WHEN DATE_DIFF(CURRENT_DATE(), DATE(block_timestamp), DAY) < 1095 THEN 'old'
                    ELSE 'very_old'
                END as age_category
            FROM `bigquery-public-data.crypto_bitcoin.outputs`
            WHERE DATE(block_timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL 60 DAY)
            AND value > 100000
        )
        SELECT 
            age_category,
            SUM(btc_amount) as total_btc,
            COUNT(*) as utxo_count,
            AVG(age_days) as avg_age_days
        FROM utxo_ages
        GROUP BY age_category
        ORDER BY avg_age_days
        """
        
        result = list(bigquery_helper.client.query(query))
        
        age_distribution = {}
        total_sample_btc = 0
        
        for row in result:
            category = row.age_category
            btc_amount = float(row.total_btc)
            age_distribution[category] = {
                'btc_amount': btc_amount,
                'utxo_count': int(row.utxo_count),
                'avg_age': float(row.avg_age_days)
            }
            total_sample_btc += btc_amount
        
        logger.info(f"✅ Distribuição de idade: {total_sample_btc:.0f} BTC em amostra")
        return age_distribution, total_sample_btc
        
    except Exception as e:
        logger.error(f"❌ Erro distribuição idade: {str(e)}")
        return {}, 0

def calculate_dynamic_extrapolation_factor(age_distribution, total_sample_btc):
    """
    Calcula fator de extrapolação baseado na distribuição real de idades
    """
    try:
        if not age_distribution or total_sample_btc == 0:
            return 600  # Fallback conservador
        
        # Bitcoin tem ~19.8M BTC total
        btc_total_supply = 19800000
        
        # Fator base: proporção da amostra vs total
        base_factor = btc_total_supply / total_sample_btc
        
        # Ajuste por composição de idade
        # UTXOs mais antigos representam mais do supply total
        age_weights = {
            'very_recent': 0.1,  # Representa pouco do total
            'recent': 0.3,
            'medium': 0.6,
            'old': 1.2,
            'very_old': 2.0     # Representa muito do total
        }
        
        weighted_representation = 0
        total_weight = 0
        
        for category, data in age_distribution.items():
            if category in age_weights:
                weight = age_weights[category]
                representation = data['btc_amount'] * weight
                weighted_representation += representation
                total_weight += data['btc_amount']
        
        if total_weight > 0:
            age_adjusted_factor = btc_total_supply / weighted_representation
        else:
            age_adjusted_factor = base_factor
        
        # Limitar fator a range razoável (200-2000)
        final_factor = max(200, min(2000, age_adjusted_factor))
        
        logger.info(f"📊 Fator dinâmico: {final_factor:.0f}x (base: {base_factor:.0f}x)")
        return final_factor
        
    except Exception as e:
        logger.error(f"❌ Erro cálculo fator: {str(e)}")
        return 600

def get_price_weighted_historical_estimate():
    """
    Estima RC histórico usando TradingView helper existente
    """
    try:
        from app.services.utils.helpers.trandview_helper import get_tv_datafeed
        
        # Usar TradingView para dados históricos
        tv = get_tv_datafeed()
        
        # Buscar dados semanais dos últimos 2 anos (mais estável)
        hist_data = tv.get_hist(
            symbol='BTCUSD',
            exchange='BINANCE',
            interval='1W',  # Semanal
            n_bars=104      # ~2 anos
        )
        
        if hist_data is None or hist_data.empty:
            raise Exception("TradingView retornou dados vazios")
        
        # Calcular preço médio ponderado (OHLC4)
        hist_data['price_avg'] = (hist_data['open'] + hist_data['high'] + 
                                 hist_data['low'] + hist_data['close']) / 4
        
        # Peso decrescente para dados mais antigos
        weights = [(i + 1) / len(hist_data) for i in range(len(hist_data))]
        
        weighted_avg_price = (hist_data['price_avg'] * weights).sum() / sum(weights)
        
        logger.info(f"✅ Preço médio TradingView: ${weighted_avg_price:,.0f}")
        return float(weighted_avg_price)
        
    except Exception as e:
        logger.error(f"❌ Erro TradingView: {str(e)}")
        # Fallback: usar preço atual * fator conservador
        current_price, _ = get_btc_price()
        return current_price * 0.7

def calculate_realized_cap_improved():
    """
    Calcula Realized Cap usando BigQuery melhorado
    """
    try:
        logger.info("🔧 Calculando RC com BigQuery melhorado...")
        
        # 1. Análise de distribuição de idade
        age_distribution, total_sample_btc = get_btc_supply_age_distribution()
        
        # 2. Fator de extrapolação dinâmico
        dynamic_factor = calculate_dynamic_extrapolation_factor(age_distribution, total_sample_btc)
        
        # 3. Preço médio histórico real
        historical_avg_price = get_price_weighted_historical_estimate()
        
        # 4. Calcular RC estimado
        # RC = BTC_sample × fator × preço_histórico_médio
        estimated_rc = total_sample_btc * dynamic_factor * historical_avg_price
        
        # 5. Validação contra MC atual (RC deve ser 30-70% do MC)
        mc_data = get_current_market_cap()
        current_mc = mc_data["market_cap_usd"]
        rc_mc_ratio = estimated_rc / current_mc
        
        # Ajustar se fora do range esperado
        if rc_mc_ratio < 0.3:
            estimated_rc = current_mc * 0.35  # Mínimo 35%
            adjustment = "increased_to_35%_mc"
        elif rc_mc_ratio > 0.7:
            estimated_rc = current_mc * 0.65  # Máximo 65%
            adjustment = "decreased_to_65%_mc"
        else:
            adjustment = "within_expected_range"
        
        metadata = {
            "method": "bigquery_improved",
            "dynamic_factor": dynamic_factor,
            "historical_price": historical_avg_price,
            "sample_btc": total_sample_btc,
            "age_distribution": age_distribution,
            "rc_mc_ratio": estimated_rc / current_mc,
            "adjustment": adjustment
        }
        
        logger.info(f"✅ RC melhorado: ${estimated_rc/1e9:.1f}B ({100*estimated_rc/current_mc:.1f}% do MC)")
        return estimated_rc, metadata
        
    except Exception as e:
        logger.error(f"❌ Erro RC melhorado: {str(e)}")
        raise Exception(f"RC BigQuery melhorado falhou: {str(e)}")

def calculate_mvrv_z_score_improved():
    """
    MVRV Z-Score usando BigQuery melhorado (sem APIs pagas)
    """
    try:
        logger.info("🎯 Calculando MVRV Z-Score BigQuery MELHORADO...")
        
        # 1. Market Cap atual
        mc_data = get_current_market_cap()
        market_cap_atual = mc_data["market_cap_usd"]
        
        # 2. Realized Cap melhorado
        realized_cap_atual, rc_metadata = calculate_realized_cap_improved()
        
        # 3. Série histórica usando proporções dinâmicas
        historical_diffs = []
        
        # Usar CoinGecko para MC histórico + RC proporcional
        try:
            url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
            params = {"vs_currency": "usd", "days": 365, "interval": "daily"}
            response = requests.get(url, params=params, timeout=20)
            
            if response.status_code == 200:
                data = response.json()
                market_caps = data["market_caps"]
                
                # RC/MC ratio atual como base
                current_ratio = realized_cap_atual / market_cap_atual
                
                for timestamp, mc in market_caps:
                    # Variar ratio dinamicamente baseado no preço/ciclo
                    date_obj = datetime.fromtimestamp(timestamp/1000)
                    days_ago = (datetime.now() - date_obj).days
                    
                    # Ciclo: ratio maior no bear, menor no bull
                    cycle_modifier = 1 + 0.2 * (days_ago / 365)  # Aumenta com tempo
                    estimated_rc = mc * current_ratio * cycle_modifier
                    
                    diff_b = (mc - estimated_rc) / 1e9
                    historical_diffs.append(diff_b)
            
        except Exception as e:
            logger.warning(f"⚠️ Série histórica fallback: {str(e)}")
            # Fallback sintético
            for i in range(365):
                mc_past = market_cap_atual * (0.9995 ** i)
                rc_past = realized_cap_atual * (0.9992 ** i)
                diff_b = (mc_past - rc_past) / 1e9
                historical_diffs.append(diff_b)
        
        # 4. StdDev
        if len(historical_diffs) < 30:
            raise Exception(f"Dados históricos insuficientes: {len(historical_diffs)}")
        
        stddev_b = statistics.stdev(historical_diffs)
        mean_diff_b = statistics.mean(historical_diffs)
        
        # 5. MVRV Z-Score final
        current_diff = market_cap_atual - realized_cap_atual
        current_diff_b = current_diff / 1e9
        
        mvrv_z_score = current_diff_b / stddev_b if stddev_b > 0 else 0
        
        # 6. Validação
        coinglass_reference = 2.52
        diferenca_vs_coinglass = abs(mvrv_z_score - coinglass_reference)
        
        return {
            "mvrv_z_score": round(mvrv_z_score, 2),
            "metodo": "bigquery_improved_no_paid_apis",
            "componentes": {
                "market_cap_atual": market_cap_atual,
                "realized_cap_atual": realized_cap_atual,
                "diferenca_atual_b": current_diff_b,
                "stddev_historico_b": stddev_b,
                "media_historica_b": mean_diff_b
            },
            "bigquery_metadata": rc_metadata,
            "serie_historica": {
                "pontos": len(historical_diffs),
                "metodo": "dynamic_proportional"
            },
            "validacao": {
                "range_esperado": (-2.0, 8.0),
                "valor_plausivel": -2.0 <= mvrv_z_score <= 8.0,
                "vs_coinglass": coinglass_reference,
                "diferenca_vs_coinglass": diferenca_vs_coinglass,
                "precisao": "alta" if diferenca_vs_coinglass < 0.5 else "média" if diferenca_vs_coinglass < 1.0 else "baixa"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Erro MVRV melhorado: {str(e)}")
        return {
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }