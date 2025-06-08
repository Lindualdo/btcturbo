# app/services/indicadores/ciclos.py - v5.1.2 COM NUPL

from datetime import datetime
from app.services.utils.helpers.postgres import get_dados_ciclo

def obter_indicadores():
    """
    Retorna indicadores do bloco CICLO incluindo NUPL v5.1.2
    ATUALIZADO: Agora inclui o novo indicador NUPL quando disponível
    """
    dados_db = get_dados_ciclo()
    
    if dados_db:
        # Extrair NUPL com tratamento específico v5.1.2
        nupl_valor = dados_db.get("nupl")
        nupl_formatado = None
        nupl_classificacao = None
        
        # PROCESSAMENTO ESPECÍFICO NUPL v5.1.2
        if nupl_valor is not None:
            try:
                nupl_float = float(nupl_valor)
                nupl_formatado = nupl_float
                
                # Classificar NUPL para interface
                if nupl_float > 0.75:
                    nupl_classificacao = "🔴 Euforia/Topo"
                elif nupl_float > 0.5:
                    nupl_classificacao = "🟡 Sobrecomprado"
                elif nupl_float > 0.25:
                    nupl_classificacao = "⚪ Neutro"
                elif nupl_float > 0:
                    nupl_classificacao = "🟢 Acumulação"
                else:
                    nupl_classificacao = "💎 Oversold"
                    
            except (ValueError, TypeError):
                nupl_formatado = None
                nupl_classificacao = "❌ Valor inválido"
        
        # RESPOSTA v5.1.2 COM NUPL
        return {
            "bloco": "ciclo",
            "timestamp": dados_db["timestamp"].isoformat() if dados_db["timestamp"] else datetime.utcnow().isoformat(),
            "indicadores": {
                # Indicadores existentes (sem alteração)
                "MVRV_Z": {
                    "valor": float(dados_db["mvrv_z_score"]) if dados_db["mvrv_z_score"] else 0.0,
                    "fonte": dados_db["fonte"] or "PostgreSQL"
                },
                "Realized_Ratio": {
                    "valor": float(dados_db["realized_ratio"]) if dados_db["realized_ratio"] else 0.0,
                    "fonte": dados_db["fonte"] or "PostgreSQL"
                },
                "Puell_Multiple": {
                    "valor": float(dados_db["puell_multiple"]) if dados_db["puell_multiple"] else 0.0,
                    "fonte": dados_db["fonte"] or "PostgreSQL"
                },
                
                # NOVO INDICADOR v5.1.2: NUPL
                "NUPL": {
                    "valor": nupl_formatado,
                    "valor_original": nupl_valor,
                    "classificacao": nupl_classificacao,
                    "disponivel": nupl_formatado is not None,
                    "fonte": dados_db["fonte"] or "PostgreSQL" if nupl_formatado is not None else None,
                    "versao_adicionado": "5.1.2"
                }
            },
            "status": "success",
            "fonte_dados": "PostgreSQL",
            
            # METADADOS v5.1.2
            "versao": "5.1.2",
            "total_indicadores": 4,  # ← ATUALIZADO: agora são 4 (incluindo NUPL)
            "indicadores_disponiveis": [
                k for k, v in {
                    "MVRV_Z": dados_db.get("mvrv_z_score"),
                    "Realized_Ratio": dados_db.get("realized_ratio"), 
                    "Puell_Multiple": dados_db.get("puell_multiple"),
                    "NUPL": nupl_formatado
                }.items() if v is not None
            ],
            
            # ALERTAS NUPL v5.1.2
            "alertas_nupl": _gerar_alertas_nupl(nupl_formatado) if nupl_formatado is not None else []
        }
    else:
        # SEM DADOS - Compatibilidade v5.1.2
        return {
            "bloco": "ciclo",
            "timestamp": datetime.utcnow().isoformat(),
            "indicadores": {
                "MVRV_Z": {"valor": None, "fonte": None},
                "Realized_Ratio": {"valor": None, "fonte": None},
                "Puell_Multiple": {"valor": None, "fonte": None},
                # NUPL ausente também
                "NUPL": {
                    "valor": None,
                    "classificacao": None,
                    "disponivel": False,
                    "fonte": None,
                    "observacao": "Indicador NUPL adicionado na v5.1.2"
                }
            },
            "status": "no_data",
            "fonte_dados": "PostgreSQL",
            "versao": "5.1.2"
        }

def _gerar_alertas_nupl(nupl_valor: float) -> list:
    """
    NOVA FUNÇÃO v5.1.2: Gera alertas específicos baseados no valor NUPL
    
    Args:
        nupl_valor: Valor NUPL validado
        
    Returns:
        list: Lista de alertas formatados
    """
    alertas = []
    
    try:
        if nupl_valor > 0.85:
            alertas.append("🚨 NUPL EXTREMO: Euforia máxima detectada - considerar realizações agressivas")
        elif nupl_valor > 0.75:
            alertas.append("🔴 NUPL ALTO: Território de topo histórico - reduzir alavancagem")
        elif nupl_valor > 0.65:
            alertas.append("🟡 NUPL ELEVADO: Mercado sobrecomprado - cautela recomendada")
        elif nupl_valor < 0:
            alertas.append("💎 NUPL NEGATIVO: Oversold extremo - oportunidade histórica")
        elif nupl_valor < 0.15:
            alertas.append("🟢 NUPL BAIXO: Zona de acumulação - considerar adições")
        
        # Alertas contextuais
        if 0.4 <= nupl_valor <= 0.6:
            alertas.append("⚪ NUPL NEUTRO: Mercado equilibrado - seguir outras métricas")
            
    except Exception:
        alertas.append("⚠️ Erro ao processar alertas NUPL")
    
    return alertas

def debug_indicadores_ciclo_nupl():
    """
    NOVA FUNÇÃO v5.1.2: Debug específico dos indicadores com NUPL
    """
    try:
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info("🔍 DEBUG v5.1.2: Verificando indicadores CICLO com NUPL...")
        
        # 1. Buscar dados direto do banco
        dados_db = get_dados_ciclo()
        
        if dados_db:
            logger.info("✅ Dados brutos do PostgreSQL:")
            for campo in ["mvrv_z_score", "realized_ratio", "puell_multiple", "nupl"]:
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
            
            # 3. Verificar NUPL específico
            nupl_dados = indicadores.get("NUPL", {})
            if nupl_dados.get("disponivel"):
                classificacao = nupl_dados.get("classificacao")
                logger.info(f"📈 NUPL Classificação: {classificacao}")
                
                alertas = resultado_api.get("alertas_nupl", [])
                if alertas:
                    logger.info("🚨 Alertas NUPL:")
                    for alerta in alertas:
                        logger.info(f"    - {alerta}")
            else:
                logger.warning("⚠️ NUPL não disponível neste registro")
            
            return resultado_api
        else:
            logger.error("❌ Nenhum dado encontrado no PostgreSQL")
            return None
            
    except Exception as e:
        logger.error(f"❌ Erro no debug: {str(e)}")
        return None

# COMPATIBILIDADE: Manter função original para sistemas legados
def obter_indicadores_legacy():
    """DEPRECATED: Use obter_indicadores() que agora inclui NUPL"""
    import logging
    logging.warning("⚠️ Usando função legacy - obter_indicadores() agora inclui NUPL v5.1.2")
    return obter_indicadores()