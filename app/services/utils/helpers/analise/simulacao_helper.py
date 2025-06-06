# app/services/utils/helpers/analise/simulacao_helper.py - CORRIGIDO (VALIDAÇÃO RIGOROSA)

import logging

def obter_dados_posicao():
    """
    CORRIGIDO: Busca dados da posição atual com validação rigorosa
    FAIL FAST se dados obrigatórios não disponíveis - SEM FALLBACKS FIXOS
    """
    try:
        from app.services.indicadores import riscos
        dados_riscos = riscos.obter_indicadores()
        
        # Validar status geral
        if dados_riscos.get("status") != "success":
            raise Exception(f"Dados de risco indisponíveis: {dados_riscos.get('erro', 'status não success')}")
        
        # Validar se posicao_atual existe
        posicao_dados = dados_riscos.get("posicao_atual")
        if not posicao_dados:
            raise Exception("Seção 'posicao_atual' não encontrada nos dados de risco")
        
        # Campos obrigatórios para simulação
        campos_obrigatorios = [
            "posicao_total",
            "capital_liquido", 
            "alavancagem_atual",
            "divida_total",
            "btc_price"
        ]
        
        dados_validados = {}
        
        # Validar cada campo obrigatório
        for campo in campos_obrigatorios:
            if campo not in posicao_dados:
                raise Exception(f"Campo obrigatório '{campo}' não encontrado na posição")
            
            campo_data = posicao_dados[campo]
            if not isinstance(campo_data, dict):
                raise Exception(f"Campo '{campo}' deve ser um objeto, recebido: {type(campo_data)}")
            
            # Validar valor_numerico
            if "valor_numerico" not in campo_data:
                raise Exception(f"Campo '{campo}' não contém 'valor_numerico'")
            
            valor = campo_data["valor_numerico"]
            
            # Validar tipo e valor
            if valor is None:
                raise Exception(f"Campo '{campo}' tem valor None")
            
            try:
                valor_float = float(valor)
            except (TypeError, ValueError):
                raise Exception(f"Campo '{campo}' não é numérico: {valor}")
            
            # Validações específicas por campo
            if campo in ["posicao_total", "capital_liquido", "btc_price"] and valor_float <= 0:
                raise Exception(f"Campo '{campo}' deve ser positivo: {valor_float}")
            
            if campo == "alavancagem_atual" and valor_float < 0:
                raise Exception(f"Alavancagem não pode ser negativa: {valor_float}")
            
            # Salvar valor validado
            dados_validados[campo] = valor_float
            logging.debug(f"✅ Campo '{campo}' validado: {valor_float}")
        
        # Validações de consistência
        if dados_validados["posicao_total"] < dados_validados["capital_liquido"]:
            logging.warning(f"⚠️ Posição total ({dados_validados['posicao_total']}) menor que capital líquido ({dados_validados['capital_liquido']})")
        
        if dados_validados["capital_liquido"] > 0:
            alavancagem_calculada = dados_validados["posicao_total"] / dados_validados["capital_liquido"]
            diff_alavancagem = abs(alavancagem_calculada - dados_validados["alavancagem_atual"])
            
            if diff_alavancagem > 0.1:  # Tolerância de 0.1x
                logging.warning(f"⚠️ Divergência alavancagem: calculada={alavancagem_calculada:.2f}x, informada={dados_validados['alavancagem_atual']:.2f}x")
        
        logging.info(f"✅ Dados posição validados: Posição=${dados_validados['posicao_total']:,.2f}, Capital=${dados_validados['capital_liquido']:,.2f}, Alav={dados_validados['alavancagem_atual']:.2f}x")
        
        return {
            "posicao_total": dados_validados["posicao_total"],
            "capital_liquido": dados_validados["capital_liquido"],
            "alavancagem_atual": dados_validados["alavancagem_atual"],
            "divida_total": dados_validados["divida_total"],
            "btc_price": dados_validados["btc_price"],
            "timestamp_coleta": dados_riscos.get("timestamp"),
            "fonte": "indicadores_risco_validado"
        }
        
    except Exception as e:
        logging.error(f"❌ Erro obtendo posição: {str(e)}")
        raise Exception(f"Dados de posição indisponíveis: {str(e)}")

def simular_impacto_posicao(acao: str, tamanho: int, posicao_atual: dict) -> dict:
    """
    CORRIGIDO: Simula impacto da ação na posição atual com validação rigorosa
    """
    try:
        # Validar inputs
        if not posicao_atual:
            raise Exception("Dados de posição atual são obrigatórios")
        
        if acao not in ["ADICIONAR", "REALIZAR", "HOLD"]:
            raise Exception(f"Ação inválida: {acao}. Deve ser ADICIONAR, REALIZAR ou HOLD")
        
        if not isinstance(tamanho, (int, float)) or tamanho < 0 or tamanho > 100:
            raise Exception(f"Tamanho inválido: {tamanho}. Deve ser 0-100")
        
        # Extrair dados validados
        campos_necessarios = ["posicao_total", "capital_liquido", "alavancagem_atual"]
        for campo in campos_necessarios:
            if campo not in posicao_atual:
                raise Exception(f"Campo '{campo}' não encontrado na posição atual")
        
        posicao_total = posicao_atual["posicao_total"]
        capital_liquido = posicao_atual["capital_liquido"]
        alavancagem_atual = posicao_atual["alavancagem_atual"]
        
        # Validar valores
        if capital_liquido <= 0:
            raise Exception(f"Capital líquido inválido: {capital_liquido}")
        
        if posicao_total < 0:
            raise Exception(f"Posição total inválida: {posicao_total}")
        
        # Simular conforme ação
        if acao == "ADICIONAR":
            valor_operacao = (capital_liquido * tamanho) / 100
            nova_posicao = posicao_total + valor_operacao
            nova_alavancagem = nova_posicao / capital_liquido
            
            # Validar se é possível adicionar
            if valor_operacao > capital_liquido * 2:  # Máximo 2x do capital
                logging.warning(f"⚠️ Valor a adicionar muito alto: ${valor_operacao:,.2f}")
            
            return {
                "acao": "adicionar",
                "valor_operacao": valor_operacao,
                "valor_operacao_display": f"${valor_operacao:,.2f}",
                "posicao_antes": posicao_total,
                "posicao_depois": nova_posicao,
                "alavancagem_antes": alavancagem_atual,
                "alavancagem_depois": nova_alavancagem,
                "impacto": f"+{tamanho}% na posição",
                "impacto_alavancagem": nova_alavancagem - alavancagem_atual,
                "status": "simulacao_ok"
            }
            
        elif acao == "REALIZAR":
            valor_operacao = (posicao_total * tamanho) / 100
            nova_posicao = posicao_total - valor_operacao
            
            # Validar se é possível realizar
            if valor_operacao > posicao_total:
                raise Exception(f"Não é possível realizar ${valor_operacao:,.2f} de uma posição de ${posicao_total:,.2f}")
            
            nova_alavancagem = nova_posicao / capital_liquido if capital_liquido > 0 else 0
            
            return {
                "acao": "realizar",
                "valor_operacao": valor_operacao,
                "valor_operacao_display": f"${valor_operacao:,.2f}",
                "posicao_antes": posicao_total,
                "posicao_depois": nova_posicao,
                "alavancagem_antes": alavancagem_atual,
                "alavancagem_depois": nova_alavancagem,
                "impacto": f"-{tamanho}% na posição",
                "impacto_alavancagem": nova_alavancagem - alavancagem_atual,
                "status": "simulacao_ok"
            }
            
        else:  # HOLD
            return {
                "acao": "manter",
                "valor_operacao": 0,
                "valor_operacao_display": "$0.00",
                "posicao_antes": posicao_total,
                "posicao_depois": posicao_total,
                "alavancagem_antes": alavancagem_atual,
                "alavancagem_depois": alavancagem_atual,
                "impacto": "Sem alteração",
                "impacto_alavancagem": 0,
                "status": "sem_mudanca"
            }
            
    except Exception as e:
        logging.error(f"❌ Erro na simulação: {str(e)}")
        return {
            "acao": acao,
            "status": "erro",
            "erro": str(e),
            "valor_operacao": 0,
            "valor_operacao_display": "$0.00"
        }

def validar_posicao_para_operacao(posicao_atual: dict, acao: str, tamanho: int) -> dict:
    """
    NOVA FUNÇÃO: Valida se uma operação é segura antes de executar
    """
    try:
        if not posicao_atual or acao == "HOLD":
            return {"valida": True, "alertas": []}
        
        posicao_total = posicao_atual.get("posicao_total", 0)
        capital_liquido = posicao_atual.get("capital_liquido", 0)
        alavancagem_atual = posicao_atual.get("alavancagem_atual", 0)
        
        alertas = []
        risks = []
        
        if acao == "ADICIONAR":
            valor_a_adicionar = (capital_liquido * tamanho) / 100
            nova_alavancagem = (posicao_total + valor_a_adicionar) / capital_liquido
            
            # Validações de segurança
            if nova_alavancagem > 3.0:
                risks.append(f"🚨 Nova alavancagem {nova_alavancagem:.2f}x > 3.0x (perigoso)")
            elif nova_alavancagem > 2.5:
                alertas.append(f"⚠️ Nova alavancagem {nova_alavancagem:.2f}x > 2.5x (atenção)")
            
            if tamanho > 50:
                alertas.append(f"⚠️ Adição de {tamanho}% é muito agressiva")
                
        elif acao == "REALIZAR":
            valor_a_realizar = (posicao_total * tamanho) / 100
            
            if valor_a_realizar > posicao_total * 0.8:
                alertas.append(f"⚠️ Realização de {tamanho}% pode ser muito agressiva")
            
            if tamanho > 75:
                alertas.append(f"⚠️ Realização de {tamanho}% é muito alta")
        
        # Validações gerais
        if alavancagem_atual > 2.5:
            risks.append(f"🚨 Alavancagem atual {alavancagem_atual:.2f}x já é alta")
        
        return {
            "valida": len(risks) == 0,
            "alertas": alertas,
            "risks": risks,
            "recomendacao": "Proceder com cautela" if alertas else "Operação segura" if len(risks) == 0 else "Não recomendado"
        }
        
    except Exception as e:
        return {
            "valida": False,
            "erro": str(e),
            "alertas": [f"Erro na validação: {str(e)}"]
        }

def debug_dados_posicao():
    """
    FUNÇÃO DEBUG: Para diagnosticar problemas nos dados de posição
    """
    try:
        logging.info("🔍 DEBUG: Analisando estrutura dos dados de posição...")
        
        from app.services.indicadores import riscos
        dados_riscos = riscos.obter_indicadores()
        
        logging.info(f"Status riscos: {dados_riscos.get('status')}")
        logging.info(f"Chaves principais: {list(dados_riscos.keys())}")
        
        if "posicao_atual" in dados_riscos:
            posicao = dados_riscos["posicao_atual"]
            logging.info(f"Chaves posição: {list(posicao.keys()) if isinstance(posicao, dict) else 'não é dict'}")
            
            for campo in ["posicao_total", "capital_liquido", "alavancagem_atual"]:
                if campo in posicao:
                    valor = posicao[campo]
                    logging.info(f"{campo}: {valor} (tipo: {type(valor)})")
                else:
                    logging.warning(f"❌ Campo '{campo}' não encontrado")
        else:
            logging.error("❌ 'posicao_atual' não encontrada")
            
        return True
        
    except Exception as e:
        logging.error(f"❌ Erro no debug: {str(e)}")
        return False