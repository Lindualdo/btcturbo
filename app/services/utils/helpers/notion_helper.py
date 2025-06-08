# app/services/utils/helpers/notion_helper.py - v5.1.3 COM SOPR - CORRIGIDO

from datetime import datetime
from notion_client import Client
from typing import Dict
from app.config import get_settings
import logging

logger = logging.getLogger(__name__)

def get_ciclo_data_from_notion() -> Dict:
    """
    Busca dados do bloco CICLO do Notion Database
    v5.1.2: INCLUINDO SUPORTE AO INDICADOR NUPL
    """
    try:
        settings = get_settings()
        notion = Client(auth=settings.NOTION_TOKEN)
        database_id = settings.NOTION_DATABASE_ID.strip().replace('"', '')
        
        logger.info(f"🔗 Conectando ao Notion Database v5.1.2: {database_id}")
        
        # Buscar dados da database
        response = notion.databases.query(database_id=database_id)
        
        # Inicializar dados padrão v5.1.2 COM NUPL
        dados_ciclo = {
            "mvrv_z_score": None,
            "realized_ratio": None,
            "puell_multiple": None,
            "nupl": None,  # ← NOVO v5.1.2
            "fonte": "Notion",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Mapeamento FLEXÍVEL v5.1.2 - incluindo NUPL
        indicador_map = {
            # MVRV Z-Score (existente)
            "mvrv_z_score": "mvrv_z_score",      
            "mvrv_z-score": "mvrv_z_score",
            "mvrv": "mvrv_z_score",
            
            # Realized Ratio (existente)
            "realized_ratio": "realized_ratio",   
            "realized": "realized_ratio",
            
            # Puell Multiple (existente)
            "puell_multiple": "puell_multiple",
            "puell": "puell_multiple",
            
            # NUPL - NOVO v5.1.2
            "nupl": "nupl",  # ← NOVO: Campo principal
            "net_unrealized_profit_loss": "nupl",  # ← NOVO: Nome completo
            "net_unrealized": "nupl",  # ← NOVO: Variação
            "unrealized_pnl": "nupl",  # ← NOVO: Alternativa
            "nrpl": "nupl"  # ← NOVO: Possível typo
        }
        
        logger.info(f"📊 Processando {len(response['results'])} registros do Notion v5.1.2...")
        
        # DEBUG: Verificar estrutura da primeira linha
        if response["results"]:
            first_row = response["results"][0]
            logger.info(f"🔍 DEBUG v5.1.2 - Campos disponíveis: {list(first_row['properties'].keys())}")
        
        for row in response["results"]:
            try:
                props = row["properties"]
                
                # MÉTODO 1: Buscar campo "indicador" (várias variações)
                indicador_titulo = None
                possible_indicator_fields = ["indicador", "Indicador", "indicator", "name", "Name"]
                
                for field_name in possible_indicator_fields:
                    if field_name in props:
                        prop_data = props[field_name]
                        if prop_data.get("title"):
                            indicador_titulo = prop_data["title"][0]["plain_text"].strip()
                            logger.info(f"📌 Campo indicador encontrado: '{field_name}' = '{indicador_titulo}'")
                            break
                        elif prop_data.get("rich_text"):
                            indicador_titulo = prop_data["rich_text"][0]["plain_text"].strip()
                            logger.info(f"📌 Campo indicador encontrado: '{field_name}' = '{indicador_titulo}'")
                            break
                
                # MÉTODO 2: Buscar campo "valor" (várias variações)
                valor = None
                possible_value_fields = ["valor", "value", "valor_coleta", "number"]
                
                for field_name in possible_value_fields:
                    if field_name in props and props[field_name].get("number") is not None:
                        valor = props[field_name]["number"]
                        logger.info(f"💰 Campo valor encontrado: '{field_name}' = {valor}")
                        break
                
                # MÉTODO 3: Se não encontrou indicador, tentar mapear direto pelos campos
                if not indicador_titulo:
                    # Buscar diretamente campos conhecidos (incluindo NUPL v5.1.2)
                    for campo_postgres, campo_notion in indicador_map.items():
                        if campo_notion in props and props[campo_notion].get("number") is not None:
                            valor_direto = props[campo_notion]["number"]
                            
                            # VALIDAÇÃO ESPECÍFICA NUPL v5.1.2
                            if campo_postgres == "nupl":
                                if _validate_nupl_notion_value(valor_direto):
                                    dados_ciclo[campo_postgres] = float(valor_direto)
                                    logger.info(f"✅ NUPL mapeamento direto: {campo_postgres} = {valor_direto} ← NOVO v5.1.2")
                                else:
                                    logger.warning(f"⚠️ NUPL inválido ignorado: {valor_direto}")
                            else:
                                dados_ciclo[campo_postgres] = float(valor_direto)
                                logger.info(f"✅ Mapeamento direto: {campo_postgres} = {valor_direto}")
                
                # Mapear indicador se encontrado via método 1
                if indicador_titulo and valor is not None:
                    indicador_key = indicador_titulo.lower().strip()
                    
                    if indicador_key in indicador_map:
                        campo_destino = indicador_map[indicador_key]
                        
                        # VALIDAÇÃO ESPECÍFICA NUPL v5.1.2
                        if campo_destino == "nupl":
                            if _validate_nupl_notion_value(valor):
                                dados_ciclo[campo_destino] = float(valor)
                                logger.info(f"✅ NUPL mapeado: {indicador_titulo} = {valor} ← NOVO v5.1.2")
                            else:
                                logger.warning(f"⚠️ NUPL inválido no Notion: {indicador_titulo} = {valor}")
                        else:
                            dados_ciclo[campo_destino] = float(valor)
                            logger.info(f"✅ {indicador_titulo}: {valor}")
                    else:
                        logger.warning(f"⚠️ Indicador não mapeado: '{indicador_titulo}' (disponível: {list(indicador_map.keys())})")
                
            except Exception as e:
                logger.error(f"❌ Erro processando linha v5.1.2: {str(e)}")
                continue
        
        # Validar se pelo menos um indicador foi encontrado
        indicadores_encontrados = [k for k, v in dados_ciclo.items() 
                                 if k not in ["fonte", "timestamp"] and v is not None]
        
        if not indicadores_encontrados:
            logger.warning("⚠️ Nenhum indicador válido encontrado no Notion v5.1.2")
            return None
        
        # LOG ESPECÍFICO NUPL v5.1.2
        nupl_encontrado = dados_ciclo.get("nupl") is not None
        logger.info(f"✅ Dados v5.1.2 coletados do Notion: {indicadores_encontrados}")
        logger.info(f"📈 NUPL encontrado: {'SIM' if nupl_encontrado else 'NÃO'} ← Novo indicador v5.1.2")
        
        return dados_ciclo
        
    except Exception as e:
        logger.error(f"❌ Erro na conexão com Notion v5.1.2: {str(e)}")
        return None

def get_momentum_data_from_notion() -> Dict:
    """
    Busca dados do bloco MOMENTUM do Notion Database
    v5.1.3: INCLUINDO SUPORTE AO INDICADOR SOPR
    """
    try:
        settings = get_settings()
        notion = Client(auth=settings.NOTION_TOKEN)
        database_id = settings.NOTION_DATABASE_ID.strip().replace('"', '')
        
        logger.info(f"🔗 Conectando ao Notion Database para MOMENTUM v5.1.3: {database_id}")
        
        # Buscar dados da database
        response = notion.databases.query(database_id=database_id)
        
        # Inicializar dados padrão v5.1.3 COM SOPR
        dados_momentum = {
            "rsi_semanal": None,
            "funding_rates": None,
            "exchange_netflow": None,  # Mantido para compatibilidade
            "long_short_ratio": None,
            "sopr": None,  # ← NOVO v5.1.3
            "fonte": "Notion",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Mapeamento FLEXÍVEL v5.1.3 - incluindo SOPR
        indicador_map = {
            # Indicadores existentes
            "rsi_semanal": "rsi_semanal",      
            "funding_rates": "funding_rates",   
            "exchange_netflow": "exchange_netflow",  # Mantido para compatibilidade
            "long_short_ratio": "long_short_ratio",
            
            # NOVO v5.1.3: SOPR
            "sopr": "sopr",  # ← NOVO: Campo principal
            "spent_output_profit_ratio": "sopr",  # ← NOVO: Nome completo
            "spent_output": "sopr",  # ← NOVO: Variação
            "profit_ratio": "sopr",  # ← NOVO: Variação curta
            
            # Variações existentes
            "rsi": "rsi_semanal",
            "funding": "funding_rates",
            "netflow": "exchange_netflow",
            "long_short": "long_short_ratio",
            "l_s_ratio": "long_short_ratio"
        }
        
        logger.info(f"📊 Processando {len(response['results'])} registros do Notion v5.1.3...")
        
        # DEBUG: Verificar estrutura da primeira linha
        if response["results"]:
            first_row = response["results"][0]
            logger.info(f"🔍 DEBUG v5.1.3 - Campos disponíveis: {list(first_row['properties'].keys())}")
        
        for row in response["results"]:
            try:
                props = row["properties"]
                
                # MÉTODO 1: Buscar campo "indicador" (várias variações)
                indicador_titulo = None
                possible_indicator_fields = ["indicador", "Indicador", "indicator", "name", "Name"]
                
                for field_name in possible_indicator_fields:
                    if field_name in props:
                        prop_data = props[field_name]
                        if prop_data.get("title"):
                            indicador_titulo = prop_data["title"][0]["plain_text"].strip()
                            logger.info(f"📌 Campo indicador encontrado: '{field_name}' = '{indicador_titulo}'")
                            break
                        elif prop_data.get("rich_text"):
                            indicador_titulo = prop_data["rich_text"][0]["plain_text"].strip()
                            logger.info(f"📌 Campo indicador encontrado: '{field_name}' = '{indicador_titulo}'")
                            break
                
                # MÉTODO 2: Buscar campo "valor" (várias variações)
                valor = None
                possible_value_fields = ["valor", "value", "valor_coleta", "number"]
                
                for field_name in possible_value_fields:
                    if field_name in props and props[field_name].get("number") is not None:
                        valor = props[field_name]["number"]
                        logger.info(f"💰 Campo valor encontrado: '{field_name}' = {valor}")
                        break
                
                # MÉTODO 3: Se não encontrou indicador, tentar mapear direto pelos campos
                if not indicador_titulo:
                    # Buscar diretamente campos conhecidos (incluindo SOPR v5.1.3)
                    for campo_postgres, campo_notion in indicador_map.items():
                        if campo_notion in props and props[campo_notion].get("number") is not None:
                            valor_direto = props[campo_notion]["number"]
                            
                            # VALIDAÇÃO ESPECÍFICA SOPR v5.1.3
                            if campo_postgres == "sopr":
                                if _validate_sopr_notion_value(valor_direto):
                                    dados_momentum[campo_postgres] = float(valor_direto)
                                    logger.info(f"✅ SOPR mapeamento direto: {campo_postgres} = {valor_direto} ← NOVO v5.1.3")
                                else:
                                    logger.warning(f"⚠️ SOPR inválido ignorado: {valor_direto}")
                            else:
                                dados_momentum[campo_postgres] = float(valor_direto)
                                logger.info(f"✅ Mapeamento direto: {campo_postgres} = {valor_direto}")
                
                # Mapear indicador se encontrado via método 1
                if indicador_titulo and valor is not None:
                    indicador_key = indicador_titulo.lower().strip()
                    
                    if indicador_key in indicador_map:
                        campo_destino = indicador_map[indicador_key]
                        
                        # VALIDAÇÃO ESPECÍFICA SOPR v5.1.3
                        if campo_destino == "sopr":
                            if _validate_sopr_notion_value(valor):
                                dados_momentum[campo_destino] = float(valor)
                                logger.info(f"✅ SOPR mapeado: {indicador_titulo} = {valor} ← NOVO v5.1.3")
                            else:
                                logger.warning(f"⚠️ SOPR inválido no Notion: {indicador_titulo} = {valor}")
                        else:
                            dados_momentum[campo_destino] = float(valor)
                            logger.info(f"✅ {indicador_titulo}: {valor}")
                    else:
                        logger.warning(f"⚠️ Indicador não mapeado: '{indicador_titulo}' (disponível: {list(indicador_map.keys())})")
                
            except Exception as e:
                logger.error(f"❌ Erro processando linha v5.1.3: {str(e)}")
                continue
        
        # Validar se pelo menos um indicador foi encontrado
        indicadores_encontrados = [k for k, v in dados_momentum.items() 
                                 if k not in ["fonte", "timestamp"] and v is not None]
        
        if not indicadores_encontrados:
            logger.warning("⚠️ Nenhum indicador válido encontrado no Notion v5.1.3 para MOMENTUM")
            return None
        
        # LOG ESPECÍFICO SOPR v5.1.3
        sopr_encontrado = dados_momentum.get("sopr") is not None
        logger.info(f"✅ Dados MOMENTUM v5.1.3 coletados do Notion: {indicadores_encontrados}")
        logger.info(f"📈 SOPR encontrado: {'SIM' if sopr_encontrado else 'NÃO'} ← Novo indicador v5.1.3")
        
        return dados_momentum
        
    except Exception as e:
        logger.error(f"❌ Erro na conexão com Notion v5.1.3 para MOMENTUM: {str(e)}")
        return None

def _validate_nupl_notion_value(valor: float) -> bool:
    """
    FUNÇÃO v5.1.2: Valida valor NUPL vindo do Notion
    
    Args:
        valor: Valor numérico do NUPL
        
    Returns:
        bool: True se válido, False se inválido
    """
    try:
        valor_float = float(valor)
        
        # Range NUPL típico: -0.5 a 1.2 (com tolerância para dados históricos)
        if not (-0.6 <= valor_float <= 1.5):
            logger.warning(f"⚠️ NUPL fora do range esperado: {valor_float} (esperado: -0.6 a 1.5)")
            return False
        
        # NUPL válido
        return True
        
    except (ValueError, TypeError):
        logger.error(f"❌ NUPL não é numérico: {valor}")
        return False

def _validate_sopr_notion_value(valor: float) -> bool:
    """
    NOVA FUNÇÃO v5.1.3: Valida valor SOPR vindo do Notion
    
    Args:
        valor: Valor numérico do SOPR
        
    Returns:
        bool: True se válido, False se inválido
    """
    try:
        valor_float = float(valor)
        
        # Range SOPR típico: 0.5 a 1.5 (com tolerância para extremos históricos)
        if not (0.5 <= valor_float <= 1.5):
            logger.warning(f"⚠️ SOPR fora do range esperado: {valor_float} (esperado: 0.5 a 1.5)")
            return False
        
        # SOPR válido
        return True
        
    except (ValueError, TypeError):
        logger.error(f"❌ SOPR não é numérico: {valor}")
        return False

def debug_notion_nupl_mapping():
    """
    FUNÇÃO v5.1.2: Debug específico do mapeamento NUPL
    """
    try:
        logger.info("🔍 DEBUG v5.1.2: Verificando mapeamento NUPL no Notion...")
        
        # Buscar dados para debug
        dados = get_ciclo_data_from_notion()
        
        if dados:
            nupl_valor = dados.get("nupl")
            
            if nupl_valor is not None:
                logger.info(f"✅ NUPL encontrado no Notion: {nupl_valor}")
                
                # Classificar NUPL
                if nupl_valor > 0.75:
                    status = "🔴 EUFORIA/TOPO"
                elif nupl_valor > 0.5:
                    status = "🟡 SOBRECOMPRADO"
                elif nupl_valor > 0.25:
                    status = "⚪ NEUTRO"
                elif nupl_valor > 0:
                    status = "🟢 ACUMULAÇÃO"
                else:
                    status = "💎 OVERSOLD"
                
                logger.info(f"📊 Status NUPL: {status}")
                
                # Validar range
                if _validate_nupl_notion_value(nupl_valor):
                    logger.info("✅ Valor NUPL dentro do range esperado")
                else:
                    logger.warning("⚠️ Valor NUPL fora do range esperado")
                    
            else:
                logger.warning("⚠️ NUPL NÃO encontrado no Notion")
                logger.info("💡 Certifique-se que existe um campo 'nupl' ou 'Net Unrealized Profit/Loss' no Notion")
        else:
            logger.error("❌ Nenhum dado retornado do Notion")
        
        return dados
        
    except Exception as e:
        logger.error(f"❌ Erro no debug NUPL Notion: {str(e)}")
        return None

def debug_notion_sopr_mapping():
    """
    NOVA FUNÇÃO v5.1.3: Debug específico do mapeamento SOPR
    """
    try:
        logger.info("🔍 DEBUG v5.1.3: Verificando mapeamento SOPR no Notion...")
        
        # Buscar dados para debug
        dados = get_momentum_data_from_notion()
        
        if dados:
            sopr_valor = dados.get("sopr")
            
            if sopr_valor is not None:
                logger.info(f"✅ SOPR encontrado no Notion: {sopr_valor}")
                
                # Classificar SOPR conforme tabela do README
                if sopr_valor < 0.90:
                    status = "🔥 CAPITULAÇÃO EXTREMA"
                elif sopr_valor < 0.95:
                    status = "💎 CAPITULAÇÃO"
                elif sopr_valor < 0.99:
                    status = "🟡 PRESSÃO VENDEDORA"
                elif sopr_valor <= 1.01:
                    status = "⚪ NEUTRO"
                elif sopr_valor < 1.05:
                    status = "📈 REALIZAÇÃO"
                elif sopr_valor < 1.08:
                    status = "🔴 GANÂNCIA"
                else:
                    status = "🚨 GANÂNCIA EXTREMA"
                
                logger.info(f"📊 Status SOPR: {status}")
                
                # Validar range
                if _validate_sopr_notion_value(sopr_valor):
                    logger.info("✅ Valor SOPR dentro do range esperado")
                else:
                    logger.warning("⚠️ Valor SOPR fora do range esperado")
                    
            else:
                logger.warning("⚠️ SOPR NÃO encontrado no Notion")
                logger.info("💡 Certifique-se que existe um campo 'sopr' ou 'Spent Output Profit Ratio' no Notion")
        else:
            logger.error("❌ Nenhum dado retornado do Notion")
        
        return dados
        
    except Exception as e:
        logger.error(f"❌ Erro no debug SOPR Notion: {str(e)}")
        return None