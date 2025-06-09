# app/services/indicadores/momentum.py - v5.1.3 COM SOPR (API)

from datetime import datetime
from app.services.utils.helpers.postgres import get_dados_momentum

def obter_indicadores():
    """
    Retorna indicadores do bloco MOMENTUM incluindo SOPR v5.1.3
    ATUALIZADO: Substitui Exchange_Netflow por SOPR na resposta da API
    """
    dados_db = get_dados_momentum()
    
    if dados_db:
        # Extrair SOPR com tratamento específico v5.1.3
        sopr_valor = dados_db.get("sopr")
        sopr_formatado = None
        sopr_classificacao = None
        
        # PROCESSAMENTO ESPECÍFICO SOPR v5.1.3
        if sopr_valor is not None:
            try:
                sopr_float = float(sopr_valor)
                sopr_formatado = sopr_float
                
                # Classificar SOPR conforme tabela README v5.1.3
                if sopr_float < 0.90:
                    sopr_classificacao = "🔥 Capitulação Extrema"
                elif sopr_float < 0.93:
                    sopr_classificacao = "💎 Capitulação Forte"
                elif sopr_float < 0.95:
                    sopr_classificacao = "💎 Capitulação"
                elif sopr_float < 0.97:
                    sopr_classificacao = "🟡 Pressão Alta"
                elif sopr_float < 0.99:
                    sopr_classificacao = "🟡 Pressão Moderada"
                elif sopr_float <= 1.01:
                    sopr_classificacao = "⚪ Neutro"
                elif sopr_float < 1.02:
                    sopr_classificacao = "📈 Realização Leve"
                elif sopr_float < 1.03:
                    sopr_classificacao = "📈 Realização Moderada"
                elif sopr_float < 1.05:
                    sopr_classificacao = "🔴 Realização Alta"
                elif sopr_float < 1.08:
                    sopr_classificacao = "🔴 Ganância"
                else:
                    sopr_classificacao = "🚨 Ganância Extrema"
                    
            except (ValueError, TypeError):
                sopr_formatado = None
                sopr_classificacao = "❌ Valor inválido"
        
        # RESPOSTA v5.1.3 COM SOPR (SUBSTITUINDO EXCHANGE_NETFLOW)
        return {
            "bloco": "momentum",
            "timestamp": dados_db["timestamp"].isoformat() if dados_db["timestamp"] else datetime.utcnow().isoformat(),
            "indicadores": {
                # Indicadores existentes (sem alteração)
                "RSI_Semanal": {
                    "valor": float(dados_db["rsi_semanal"]) if dados_db["rsi_semanal"] else 0.0,
                    "fonte": dados_db["fonte"] or "PostgreSQL"
                },
               "Funding_Rates": {
                    "valor": f"{float(dados_db['funding_rates']):.5f}%" if dados_db["funding_rates"] else "0.00000%",
                    "fonte": dados_db["fonte"] or "PostgreSQL"
                },
                "Long_Short_Ratio": {
                    "valor": float(dados_db["long_short_ratio"]) if dados_db["long_short_ratio"] else 0.0,
                    "fonte": dados_db["fonte"] or "PostgreSQL"
                },
                
                # NOVO v5.1.3: SOPR (SUBSTITUI Exchange_Netflow)
                "SOPR": {
                    "valor": sopr_formatado,
                    "valor_original": sopr_valor,
                    "classificacao": sopr_classificacao,
                    "disponivel": sopr_formatado is not None,
                    "fonte": dados_db["fonte"] or "PostgreSQL" if sopr_formatado is not None else None,
                    "versao_adicionado": "5.1.3",
                    "substitui": "Exchange_Netflow"
                }
            },
            "status": "success",
            "fonte_dados": "PostgreSQL",
            
            # METADADOS v5.1.3
            "versao": "5.1.3",
            "total_indicadores": 4,  # RSI + Funding + L/S + SOPR
            "indicadores_disponiveis": [
                k for k, v in {
                    "RSI_Semanal": dados_db.get("rsi_semanal"),
                    "Funding_Rates": dados_db.get("funding_rates"), 
                    "Long_Short_Ratio": dados_db.get("long_short_ratio"),
                    "SOPR": sopr_formatado
                }.items() if v is not None
            ],
            
            # ALERTAS SOPR v5.1.3
            "alertas_sopr": _gerar_alertas_sopr(sopr_formatado) if sopr_formatado is not None else [],
            
            # COMPATIBILIDADE: Exchange_Netflow ainda existe no DB mas não aparece na API
            "observacoes": {
                "exchange_netflow_descontinuado": "Exchange_Netflow removido da API v5.1.3, substituído por SOPR",
                "compatibilidade_db": "exchange_netflow ainda existe no banco para compatibilidade"
            }
        }
    else:
        # SEM DADOS - Compatibilidade v5.1.3
        return {
            "bloco": "momentum",
            "timestamp": datetime.utcnow().isoformat(),
            "indicadores": {
                "RSI_Semanal": {"valor": None, "fonte": None},
                "Funding_Rates": {"valor": None, "fonte": None},
                "Long_Short_Ratio": {"valor": None, "fonte": None},
                # SOPR ausente também
                "SOPR": {
                    "valor": None,
                    "classificacao": None,
                    "disponivel": False,
                    "fonte": None,
                    "observacao": "Indicador SOPR adicionado na v5.1.3"
                }
            },
            "status": "no_data",
            "fonte_dados": "PostgreSQL",
            "versao": "5.1.3"
        }

def _gerar_alertas_sopr(sopr_valor: float) -> list:
    """
    NOVA FUNÇÃO v5.1.3: Gera alertas específicos baseados no valor SOPR
    
    Args:
        sopr_valor: Valor SOPR validado
        
    Returns:
        list: Lista de alertas formatados
    """
    alertas = []
    
    try:
        if sopr_valor < 0.90:
            alertas.append("🔥 SOPR EXTREMO: Capitulação máxima - oportunidade histórica de compra")
        elif sopr_valor < 0.95:
            alertas.append("💎 SOPR BAIXO: Capitulação ativa - considerar compras")
        elif sopr_valor < 0.99:
            alertas.append("🟡 SOPR PRESSÃO: Vendas com prejuízo - aguardar estabilização")
        elif sopr_valor > 1.08:
            alertas.append("🚨 SOPR EXTREMO: Ganância máxima - considerar saídas")
        elif sopr_valor > 1.05:
            alertas.append("🔴 SOPR ALTO: Realização excessiva - reduzir posições")
        elif sopr_valor > 1.03:
            alertas.append("📈 SOPR ELEVADO: Tomada de lucro ativa - cautela")
        
        # Alertas contextuais
        if 0.99 <= sopr_valor <= 1.01:
            alertas.append("⚪ SOPR NEUTRO: Mercado equilibrado - seguir outras métricas")
            
    except Exception:
        alertas.append("⚠️ Erro ao processar alertas SOPR")
    
    return alertas

def debug_indicadores_momentum_sopr():
    """
    NOVA FUNÇÃO v5.1.3: Debug específico dos indicadores com SOPR
    """
    try:
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info("🔍 DEBUG v5.1.3: Verificando indicadores MOMENTUM com SOPR...")
        
        # 1. Buscar dados direto do banco
        dados_db = get_dados_momentum()
        
        if dados_db:
            logger.info("✅ Dados brutos do PostgreSQL:")
            for campo in ["rsi_semanal", "funding_rates", "long_short_ratio", "exchange_netflow", "sopr"]:
                valor = dados_db.get(campo)
                status = "✅" if valor is not None else "❌"
                logger.info(f"    {status} {campo}: {valor}")
            
            # 2. Testar processamento via API
            resultado_api = obter_indicadores()
            
            logger.info("✅ Resultado da API de indicadores:")
            indicadores = resultado_api.get("indicadores", {})
            
            for nome, dados in indicadores.items():
                valor = dados.get("valor")
                disponivel = dados.get("disponivel", True)
                status = "✅" if valor is not None else "⚠️"
                logger.info(f"    {status} {nome}: {valor} (disponível: {disponivel})")
            
            # 3. Verificar SOPR específico
            sopr_dados = indicadores.get("SOPR", {})
            if sopr_dados.get("disponivel"):
                classificacao = sopr_dados.get("classificacao")
                logger.info(f"📈 SOPR Classificação: {classificacao}")
                
                alertas = resultado_api.get("alertas_sopr", [])
                if alertas:
                    logger.info("🚨 Alertas SOPR:")
                    for alerta in alertas:
                        logger.info(f"    - {alerta}")
            else:
                logger.warning("⚠️ SOPR não disponível neste registro")
            
            # 4. Verificar se Exchange_Netflow foi removido da API
            if "Exchange_Netflow" not in indicadores:
                logger.info("✅ Exchange_Netflow removido da API conforme v5.1.3")
            else:
                logger.warning("⚠️ Exchange_Netflow ainda aparece na API - verificar código")
            
            return resultado_api
        else:
            logger.error("❌ Nenhum dado encontrado no PostgreSQL")
            return None
            
    except Exception as e:
        logger.error(f"❌ Erro no debug: {str(e)}")
        return None

# COMPATIBILIDADE: Manter função original para sistemas legados
def obter_indicadores_legacy():
    """DEPRECATED: Use obter_indicadores() que agora inclui SOPR v5.1.3"""
    import logging
    logging.warning("⚠️ Usando função legacy - obter_indicadores() agora inclui SOPR v5.1.3")
    return obter_indicadores()