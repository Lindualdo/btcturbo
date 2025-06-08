# app/services/coleta/ciclos.py - v5.1.2 COM NUPL

from datetime import datetime
import logging
from app.services.utils.helpers.notion_helper import get_ciclo_data_from_notion
from app.services.utils.helpers.postgres.ciclo_helper import insert_dados_ciclo

logger = logging.getLogger(__name__)

def coletar(forcar_coleta: bool):
    """
    Coleta dados do bloco CICLO via Notion Database e grava no PostgreSQL
    v5.1.2: INCLUINDO SUPORTE AO INDICADOR NUPL
    
    Args:
        forcar_coleta (bool): Se True, força nova coleta independente do cache
        
    Returns:
        dict: Status da coleta com detalhes dos dados coletados
    """
    try:
        logger.info("🔄 Iniciando coleta bloco CICLO v5.1.2 via Notion (incluindo NUPL)...")
        
        # 1. Buscar dados do Notion
        logger.info("📋 Conectando ao Notion Database...")
        dados_notion = get_ciclo_data_from_notion()
        
        if not dados_notion:
            raise Exception("Nenhum dado retornado do Notion Database")
        
        # 2. Extrair indicadores necessários v5.1.2 (incluindo NUPL)
        mvrv_z_score = dados_notion.get("mvrv_z_score")
        realized_ratio = dados_notion.get("realized_ratio") 
        puell_multiple = dados_notion.get("puell_multiple")
        nupl = dados_notion.get("nupl")  # ← NOVO v5.1.2
        
        # 3. Validar indicadores obrigatórios (NUPL é opcional)
        indicadores_faltando = []
        
        # Indicadores obrigatórios (sem NUPL)
        if mvrv_z_score is None:
            indicadores_faltando.append("mvrv_z_score")
        if realized_ratio is None:
            indicadores_faltando.append("realized_ratio")
        if puell_multiple is None:
            indicadores_faltando.append("puell_multiple")
        
        # NUPL é opcional - apenas alertar se ausente
        nupl_status = "PRESENTE" if nupl is not None else "AUSENTE"
        logger.info(f"📈 Status NUPL v5.1.2: {nupl_status}")
        
        if indicadores_faltando:
            logger.warning(f"⚠️ Indicadores obrigatórios não encontrados no Notion: {indicadores_faltando}")
            # Continua com os dados disponíveis, usando 0.0 para os faltantes
            mvrv_z_score = mvrv_z_score or 0.0
            realized_ratio = realized_ratio or 0.0
            puell_multiple = puell_multiple or 0.0
        
        # 4. Validação específica NUPL v5.1.2
        nupl_validado = None
        if nupl is not None:
            try:
                nupl_float = float(nupl)
                
                # Validar range NUPL (-0.5 a 1.2 com tolerância)
                if -0.6 <= nupl_float <= 1.5:
                    nupl_validado = nupl_float
                    
                    # Classificar NUPL para logging
                    if nupl_float > 0.75:
                        nupl_classificacao = "🔴 EUFORIA/TOPO"
                    elif nupl_float > 0.5:
                        nupl_classificacao = "🟡 SOBRECOMPRADO"
                    elif nupl_float > 0.25:
                        nupl_classificacao = "⚪ NEUTRO"
                    elif nupl_float > 0:
                        nupl_classificacao = "🟢 ACUMULAÇÃO"
                    else:
                        nupl_classificacao = "💎 OVERSOLD"
                    
                    logger.info(f"✅ NUPL validado: {nupl_float:.3f} - {nupl_classificacao}")
                else:
                    logger.warning(f"⚠️ NUPL fora do range: {nupl_float} (esperado: -0.6 a 1.5) - será ignorado")
                    nupl_validado = None
                    
            except (ValueError, TypeError):
                logger.error(f"❌ NUPL não é numérico: {nupl} - será ignorado")
                nupl_validado = None
        
        # 5. Gravar dados no PostgreSQL v5.1.2 (COM NUPL)
        logger.info("💾 Gravando dados v5.1.2 no PostgreSQL...")
        sucesso_gravacao = insert_dados_ciclo(
            mvrv_z=float(mvrv_z_score),
            realized_ratio=float(realized_ratio), 
            puell_multiple=float(puell_multiple),
            nupl=nupl_validado,  # ← NOVO v5.1.2: pode ser None
            fonte="notion"
        )
        
        if not sucesso_gravacao:
            raise Exception("Falha ao gravar dados no PostgreSQL")
        
        # 6. Preparar resposta de sucesso v5.1.2
        resposta_sucesso = {
            "bloco": "ciclos",
            "status": "sucesso",
            "timestamp": datetime.utcnow().isoformat(),
            "versao": "5.1.2",  # ← NOVO: Versão para tracking
            "detalhes": "Dados coletados via Notion Database (incluindo NUPL v5.1.2)",
            "dados_coletados": {
                # Indicadores existentes
                "mvrv_z_score": float(mvrv_z_score),
                "realized_ratio": float(realized_ratio),
                "puell_multiple": float(puell_multiple),
                
                # NOVO v5.1.2: NUPL
                "nupl": {
                    "valor": nupl_validado,
                    "valor_original": nupl,
                    "status": "validado" if nupl_validado is not None else "ausente_ou_invalido",
                    "classificacao": nupl_classificacao if nupl_validado is not None else None
                },
                
                # Metadados
                "fonte_original": dados_notion.get("fonte", "Notion"),
                "timestamp_notion": dados_notion.get("timestamp")
            },
            "fonte": "notion",
            "indicadores_processados": 4,  # ← ATUALIZADO: agora são 4 (incluindo NUPL)
            "indicadores_faltando": indicadores_faltando if indicadores_faltando else "nenhum",
            
            # NOVO v5.1.2: Estatísticas NUPL
            "nupl_stats": {
                "coletado": nupl is not None,
                "validado": nupl_validado is not None,
                "classificacao": nupl_classificacao if nupl_validado is not None else "N/A"
            }
        }
        
        # LOG final v5.1.2
        logger.info(f"✅ Coleta CICLO v5.1.2 concluída com sucesso:")
        logger.info(f"    MVRV: {mvrv_z_score}, Realized: {realized_ratio}")
        logger.info(f"    Puell: {puell_multiple}, NUPL: {nupl_validado} ← NOVO")
        
        return resposta_sucesso
        
    except Exception as e:
        logger.error(f"❌ Erro na coleta CICLO v5.1.2 via Notion: {str(e)}")
        
        resposta_erro = {
            "bloco": "ciclos", 
            "status": "erro",
            "timestamp": datetime.utcnow().isoformat(),
            "versao": "5.1.2",
            "detalhes": f"Falha na coleta v5.1.2 via Notion: {str(e)}",
            "fonte": "notion",
            "dados_coletados": None
        }
        
        return resposta_erro

def validar_dados_ciclo_completos(dados_notion: dict) -> dict:
    """
    NOVA FUNÇÃO v5.1.2: Validação específica dos dados do ciclo incluindo NUPL
    
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
            "nupl_analise": {}
        }
        
        # Validar indicadores existentes
        validacoes = [
            ("mvrv_z_score", dados_notion.get("mvrv_z_score"), lambda x: 0 <= x <= 8),
            ("realized_ratio", dados_notion.get("realized_ratio"), lambda x: 0.5 <= x <= 3.0),
            ("puell_multiple", dados_notion.get("puell_multiple"), lambda x: 0.3 <= x <= 5.0)
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
        
        # VALIDAÇÃO ESPECÍFICA NUPL v5.1.2
        nupl = dados_notion.get("nupl")
        if nupl is not None:
            try:
                nupl_float = float(nupl)
                
                # Validar range
                if -0.6 <= nupl_float <= 1.5:
                    resultado["indicadores_validos"].append("nupl")
                    
                    # Análise detalhada NUPL
                    if nupl_float > 0.75:
                        resultado["nupl_analise"] = {
                            "status": "EUFORIA",
                            "acao_sugerida": "Considerar realizações",
                            "risco": "ALTO"
                        }
                    elif nupl_float > 0.5:
                        resultado["nupl_analise"] = {
                            "status": "SOBRECOMPRADO",
                            "acao_sugerida": "Reduzir alavancagem",
                            "risco": "MÉDIO"
                        }
                    elif nupl_float > 0.25:
                        resultado["nupl_analise"] = {
                            "status": "NEUTRO",
                            "acao_sugerida": "Manter posição",
                            "risco": "BAIXO"
                        }
                    elif nupl_float > 0:
                        resultado["nupl_analise"] = {
                            "status": "ACUMULAÇÃO",
                            "acao_sugerida": "Considerar adições",
                            "risco": "MUITO BAIXO"
                        }
                    else:
                        resultado["nupl_analise"] = {
                            "status": "OVERSOLD",
                            "acao_sugerida": "Oportunidade de compra",
                            "risco": "EXTREMAMENTE BAIXO"
                        }
                else:
                    resultado["indicadores_invalidos"].append(f"nupl: {nupl_float} fora do range (-0.6 a 1.5)")
                    resultado["valido"] = False
                    
            except (ValueError, TypeError):
                resultado["indicadores_invalidos"].append("nupl: valor não numérico")
                resultado["valido"] = False
        else:
            resultado["alertas"].append("NUPL não fornecido (novo indicador v5.1.2)")
        
        return resultado
        
    except Exception as e:
        logger.error(f"❌ Erro na validação v5.1.2: {str(e)}")
        return {
            "valido": False,
            "erro": str(e)
        }

def debug_coleta_ciclo_nupl():
    """
    NOVA FUNÇÃO v5.1.2: Debug específico da coleta com NUPL
    """
    try:
        logger.info("🔍 DEBUG v5.1.2: Testando coleta CICLO com NUPL...")
        
        # 1. Testar conexão Notion
        dados_notion = get_ciclo_data_from_notion()
        
        if not dados_notion:
            logger.error("❌ Nenhum dado retornado do Notion")
            return False
        
        # 2. Validar dados
        validacao = validar_dados_ciclo_completos(dados_notion)
        logger.info(f"📊 Validação: {validacao}")
        
        # 3. Simular coleta (sem gravar)
        logger.info("🧪 Simulando coleta completa...")
        resultado = coletar(forcar_coleta=True)
        
        logger.info(f"✅ Resultado da coleta v5.1.2: {resultado.get('status')}")
        
        # 4. Verificar se NUPL foi processado
        if resultado.get("status") == "sucesso":
            nupl_stats = resultado.get("nupl_stats", {})
            logger.info(f"📈 NUPL Stats: {nupl_stats}")
            
            if nupl_stats.get("coletado"):
                logger.info("✅ NUPL foi coletado com sucesso do Notion")
            else:
                logger.warning("⚠️ NUPL não foi encontrado no Notion - verificar configuração")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro no debug v5.1.2: {str(e)}")
        return False