# app/services/utils/helpers/simulacao_helper.py

# Simula a posição atual e o impacto de ações de compra ou venda

import logging

def obter_dados_posicao():
    """Busca dados da posição atual"""
    try:
        from app.services.indicadores import riscos
        dados_riscos = riscos.obter_indicadores()
        if dados_riscos.get("status") == "success":
            posicao_dados = dados_riscos.get("posicao_atual", {})
            return {
                "posicao_total": posicao_dados.get("posicao_total", {}).get("valor_numerico", 0),
                "capital_liquido": posicao_dados.get("capital_liquido", {}).get("valor_numerico", 0),
                "alavancagem_atual": posicao_dados.get("alavancagem_atual", {}).get("valor_numerico", 0)
            }
        return None
    except Exception as e:
        logging.error(f"❌ Erro obtendo posição: {str(e)}")
        return None

def simular_impacto_posicao(acao: str, tamanho: int, posicao_atual: dict) -> dict:
    """Simula impacto da ação na posição atual"""
    if not posicao_atual:
        return {"erro": "Dados de posição não disponíveis"}
    
    try:
        posicao_total = posicao_atual.get("posicao_total", 0)
        capital_liquido = posicao_atual.get("capital_liquido", 0)
        alavancagem_atual = posicao_atual.get("alavancagem_atual", 0)
        
        if acao == "ADICIONAR":
            valor_adicionar = (capital_liquido * tamanho) / 100
            nova_posicao = posicao_total + valor_adicionar
            nova_alavancagem = nova_posicao / capital_liquido if capital_liquido > 0 else 0
            
            return {
                "acao": "adicionar",
                "valor_operacao": f"${valor_adicionar:,.2f}",
                "posicao_antes": f"${posicao_total:,.2f}",
                "posicao_depois": f"${nova_posicao:,.2f}",
                "alavancagem_antes": f"{alavancagem_atual:.2f}x",
                "alavancagem_depois": f"{nova_alavancagem:.2f}x",
                "impacto": f"+{tamanho}% na posição"
            }
            
        elif acao == "REALIZAR":
            valor_realizar = (posicao_total * tamanho) / 100
            nova_posicao = posicao_total - valor_realizar
            nova_alavancagem = nova_posicao / capital_liquido if capital_liquido > 0 else 0
            
            return {
                "acao": "realizar",
                "valor_operacao": f"${valor_realizar:,.2f}",
                "posicao_antes": f"${posicao_total:,.2f}",
                "posicao_depois": f"${nova_posicao:,.2f}",
                "alavancagem_antes": f"{alavancagem_atual:.2f}x",
                "alavancagem_depois": f"{nova_alavancagem:.2f}x",
                "impacto": f"-{tamanho}% na posição"
            }
        else:
            return {
                "acao": "manter",
                "valor_operacao": "$0.00",
                "posicao_antes": f"${posicao_total:,.2f}",
                "posicao_depois": f"${posicao_total:,.2f}",
                "alavancagem_antes": f"{alavancagem_atual:.2f}x",
                "alavancagem_depois": f"{alavancagem_atual:.2f}x",
                "impacto": "Sem alteração"
            }
            
    except Exception as e:
        return {"erro": str(e)}