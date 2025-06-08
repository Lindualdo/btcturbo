# app/services/coleta/momentum.py - v5.1.3 COM SOPR

from datetime import datetime
import logging
from app.services.utils.helpers.notion_helper import get_momentum_data_from_notion
from app.services.utils.helpers.postgres.momentum_helper import insert_dados_momentum

logger = logging.getLogger(__name__)

def coletar(forcar_coleta: bool):
    """
    Coleta dados do bloco MOMENTUM via Notion Database e grava no PostgreSQL
    v5.1.3: INCLUINDO SUPORTE AO INDICADOR SOPR
    
    Args:
        forcar_coleta (bool): Se True, força nova coleta independente do cache
        
    Returns:
        dict: Status da coleta com detalhes dos dados coletados
    """
    try:
        logger.info("🔄 Iniciando coleta bloco MOMENTUM v5.1.3 via Notion (incluindo SOPR)...")
        
        # 1. Buscar dados do Notion
        logger.info("📋 Conectando ao Notion Database...")
        dados_notion = get_momentum_data_from_notion()
        
        if not dados_notion:
            raise Exception("Nenhum dado retornado do Notion Database")
        
        # 2. Extrair indicadores necessários v5.1.3 (incluindo SOPR)
        rsi_semanal = dados_notion.get("rsi_semanal")
        funding_rates = dados_notion.get("funding_rates") 
        exchange_netflow = dados_notion.get("exchange_netflow")  # Mantido para compatibilidade
        long_short_ratio = dados_notion.get("long_short_ratio")
        sopr = dados_notion.get("sopr")  # ← NOVO v5.1.3
        
        # 3. Validar indicadores obrigatórios (SOPR é opcional por enquanto)
        indicadores_faltando = []
        if rsi_semanal is None:
            indicadores_faltando.append("rsi_semanal")
        if funding_rates is None:
            indicadores_faltando.append("funding_rates")
        if exchange_netflow is None:
            indicadores_faltando.append("exchange_netflow")
        if long_short_ratio is None:
            indicadores_faltando.append("long_short_ratio")
            
        # SOPR é opcional - apenas alertar se ausente
        sopr_status = "PRESENTE" if sopr is not None else "AUSENTE"
        logger.info(f"📈 Status SOPR v5.1.3: {sopr_status}")
        
        if indicadores_faltando:
            logger.warning(f"⚠️ Indicadores obrigatórios não encontrados no Notion: {indicadores_faltando}")
            # Continua com os dados disponíveis, usando 0.0 para os faltantes
            rsi_semanal = rsi_semanal or 0.0
            funding_rates = funding_rates or 0.0
            exchange_netflow = exchange_netflow or 0.0
            long_short_ratio = long_short_ratio or 0.0
        
        # 4. Validação específica SOPR v5.1.3
        sopr_validado = None
        if sopr is not None:
            try:
                sopr_float = float(sopr)
                
                # Validar range SOPR (0.5 a 1.5 com tolerância)
                if 0.5 <= sopr_float <= 1.5:
                    sopr_validado = sopr_float
                    
                    # Classificar SOPR para logging conforme tabela README
                    if sopr_float < 0.90:
                        sopr_classificacao = "🔥 CAPITULAÇÃO EXTREMA"
                    elif sopr_float < 0.95:
                        sopr_classificacao = "💎 CAPITULAÇÃO"
                    elif sopr_float < 0.99:
                        sopr_classificacao = "🟡 PRESSÃO VENDEDORA"
                    elif sopr_float <= 1.01:
                        sopr_classificacao = "⚪ NEUTRO"
                    elif sopr_float < 1.05:
                        sopr_classificacao = "📈 REALIZAÇÃO"
                    elif sopr_float < 1.08:
                        sopr_classificacao = "🔴 GANÂNCIA"
                    else:
                        sopr_classificacao = "🚨 GANÂNCIA EXTREMA"
                    
                    logger.info(f"✅ SOPR validado: {sopr_float:.3f} - {sopr_classificacao}")
                else:
                    logger.warning(f"⚠️ SOPR fora do range: {sopr_float} (esperado: 0.5 a 1.5) - será ignorado")
                    sopr_validado = None
                    
            except (ValueError, TypeError):
                logger.error(f"❌ SOPR não é numérico: {sopr} - será ignorado")
                sopr_validado = None
        
        # 5. Gravar dados no PostgreSQL v5.1.3 (COM SOPR)
        logger.info("💾 Gravando dados v5.1.3 no PostgreSQL...")
        sucesso_gravacao = insert_dados_momentum(
            rsi=float(rsi_semanal),
            funding=float(funding_rates),
            netflow=float(exchange_netflow),  # Mantido para compatibilidade
            ls_ratio=float(long_short_ratio),
            sopr=sopr_validado,  # ← NOVO v5.1.3: pode ser None
            fonte="notion"
        )
        
        if not sucesso_gravacao:
            raise Exception("Falha ao gravar dados no PostgreSQL")
        
        # 6. Preparar resposta de sucesso v5.1.3
        resposta_sucesso = {
            "bloco": "momentum",
            "status": "sucesso",
            "timestamp": datetime.utcnow().isoformat(),
            "versao": "5.1.3",  # ← NOVO: Versão para tracking
            "detalhes": "Dados coletados via Notion Database (incluindo SOPR v5.1.3)",
            "dados_coletados": {
                # Indicadores existentes
                "rsi_semanal": float(rsi_semanal),
                "funding_rates": float(funding_rates),
                "exchange_netflow": float(exchange_netflow),  # Mantido para compatibilidade
                "long_short_ratio": float(long_short_ratio),
                
                # NOVO v5.1.3: SOPR
                "sopr": {
                    "valor": sopr_validado,
                    "valor_original": sopr,
                    "status": "validado" if sopr_validado is not None else "ausente_ou_invalido",
                    "classificacao": sopr_classificacao if sopr_validado is not None else None
                },
                
                # Metadados
                "fonte_original": dados_notion.get("fonte", "Notion"),
                "timestamp_notion": dados_notion.get("timestamp")
            },
            "fonte": "notion",
            "indicadores_processados": 5,  # ← ATUALIZADO: agora são 5 (incluindo SOPR)
            "indicadores_faltando": indicadores_faltando if indicadores_faltando else "nenhum",
            
            # NOVO v5.1.3: Estatísticas SOPR
            "sopr_stats": {
                "coletado": sopr is not None,
                "validado": sopr_validado is not None,
                "classificacao": sopr_classificacao if sopr_validado is not None else "N/A"
            }
        }
        
        # LOG final v5.1.3
        logger.info(f"✅ Coleta MOMENTUM v5.1.3 concluída com sucesso:")
        logger.info(f"    RSI: {rsi_semanal}, Funding: {funding_rates}")
        logger.info(f"    Netflow: {exchange_netflow} (compatibilidade), L/S: {long_short_ratio}")
        logger.info(f"    SOPR: {sopr_validado} ← NOVO")
        
        return resposta_sucesso
        
    except Exception as e:
        logger.error(f"❌ Erro na coleta MOMENTUM v5.1.3 via Notion: {str(e)}")
        
        resposta_erro = {
            "bloco": "momentum", 
            "status": "erro",
            "timestamp": datetime.utcnow().isoformat(),
            "versao": "5.1.3",
            "detalhes": f"Falha na coleta v5.1.3 via Notion: {str(e)}",
            "fonte": "notion",
            "dados_coletados": None
        }
        
        return resposta_erro

def validar_dados_momentum_completos(dados_notion: dict) -> dict:
    """
    NOVA FUNÇÃO v5.1.3: Validação específica dos dados do momentum incluindo SOPR
    
    Args:
        dados_notion: Dados brutos do Notion
        
    Returns:
        dict: Resultado da validação com detalhes
    """
    try:
        resultado = {
            "valido": True,
            "indicadores_validos": [],
            "indicadores_invalidos": [],
            "alertas": [],
            "sopr_analise": {}
        }
        
        # Validar indicadores existentes
        validacoes = [
            ("rsi_semanal", dados_notion.get("rsi_semanal"), lambda x: 0 <= x <= 100),
            ("funding_rates", dados_notion.get("funding_rates"), lambda x: -0.1 <= x <= 0.1),
            ("exchange_netflow", dados_notion.get("exchange_netflow"), lambda x: -100000 <= x <= 100000),
            ("long_short_ratio", dados_notion.get("long_short_ratio"), lambda x: 0.5 <= x <= 2.0)
        ]
        
        for nome, valor, validador in validacoes:
            if valor is not None:
                try:
                    valor_float = float(valor)
                    if validador(valor_float):
                        resultado["indicadores_validos"].append(nome)
                    else:
                        resultado["indicadores_invalidos"].append(f"{nome}: {valor} fora do range")
                        resultado["valido"] = False
                except (ValueError, TypeError):
                    resultado["indicadores_invalidos"].append(f"{nome}: valor não numérico")
                    resultado["valido"] = False
            else:
                resultado["alertas"].append(f"{nome} não fornecido")
        
        # VALIDAÇÃO ESPECÍFICA SOPR v5.1.3
        sopr = dados_notion.get("sopr")
        if sopr is not None:
            try:
                sopr_float = float(sopr)
                
                # Validar range
                if 0.5 <= sopr_float <= 1.5:
                    resultado["indicadores_validos"].append("sopr")
                    
                    # Análise detalhada SOPR conforme tabela README
                    if sopr_float < 0.90:
                        resultado["sopr_analise"] = {
                            "status": "CAPITULAÇÃO EXTREMA",
                            "acao_sugerida": "Compra agressiva",
                            "score_esperado": 10,
                            "risco": "MUITO BAIXO"
                        }
                    elif sopr_float < 0.95:
                        resultado["sopr_analise"] = {
                            "status": "CAPITULAÇÃO",
                            "acao_sugerida": "Compra moderada",
                            "score_esperado": "8-9",
                            "risco": "BAIXO"
                        }
                    elif sopr_float < 0.99:
                        resultado["sopr_analise"] = {
                            "status": "PRESSÃO VENDEDORA",
                            "acao_sugerida": "Aguardar",
                            "score_esperado": "6-7",
                            "risco": "MÉDIO"
                        }
                    elif sopr_float <= 1.01:
                        resultado["sopr_analise"] = {
                            "status": "NEUTRO",
                            "acao_sugerida": "Manter posição",
                            "score_esperado": 5,
                            "risco": "NEUTRO"
                        }
                    elif sopr_float < 1.05:
                        resultado["sopr_analise"] = {
                            "status": "REALIZAÇÃO",
                            "acao_sugerida": "Considerar redução",
                            "score_esperado": "2-4",
                            "risco": "MÉDIO"
                        }
                    elif sopr_float < 1.08:
                        resultado["sopr_analise"] = {
                            "status": "GANÂNCIA",
                            "acao_sugerida": "Reduzir posição",
                            "score_esperado": 1,
                            "risco": "ALTO"
                        }
                    else:
                        resultado["sopr_analise"] = {
                            "status": "GANÂNCIA EXTREMA",
                            "acao_sugerida": "Sair da posição",
                            "score_esperado": 0,
                            "risco": "EXTREMO"
                        }
                else:
                    resultado["indicadores_invalidos"].append(f"sopr: {sopr_float} fora do range (0.5 a 1.5)")
                    resultado["valido"] = False
                    
            except (ValueError, TypeError):
                resultado["indicadores_invalidos"].append("sopr: valor não numérico")
                resultado["valido"] = False
        else:
            resultado["alertas"].append("SOPR não fornecido (novo indicador v5.1.3)")
        
        return resultado
        
    except Exception as e:
        logger.error(f"❌ Erro na validação v5.1.3: {str(e)}")
        return {
            "valido": False,
            "erro": str(e)
        }

def debug_coleta_momentum_sopr():
    """
    NOVA FUNÇÃO v5.1.3: Debug específico da coleta com SOPR
    """
    try:
        logger.info("🔍 DEBUG v5.1.3: Testando coleta MOMENTUM com SOPR...")
        
        # 1. Testar conexão Notion
        dados_notion = get_momentum_data_from_notion()
        
        if not dados_notion:
            logger.error("❌ Nenhum dado retornado do Notion")
            return False
        
        # 2. Validar dados
        validacao = validar_dados_momentum_completos(dados_notion)
        logger.info(f"📊 Validação: {validacao}")
        
        # 3. Simular coleta (sem gravar)
        logger.info("🧪 Simulando coleta completa...")
        resultado = coletar(forcar_coleta=True)
        
        logger.info(f"✅ Resultado da coleta v5.1.3: {resultado.get('status')}")
        
        # 4. Verificar se SOPR foi processado
        if resultado.get("status") == "sucesso":
            sopr_stats = resultado.get("sopr_stats", {})
            logger.info(f"📈 SOPR Stats: {sopr_stats}")
            
            if sopr_stats.get("coletado"):
                logger.info("✅ SOPR foi coletado com sucesso do Notion")
            else:
                logger.warning("⚠️ SOPR não foi encontrado no Notion - verificar configuração")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro no debug v5.1.3: {str(e)}")
        return False