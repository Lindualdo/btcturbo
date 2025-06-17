# app/services/v3/dash_main/utils/analise/1-mercado/define_ciclo.py

import logging
import json
from typing import Dict, Tuple

logger = logging.getLogger(__name__)

def executar_analise_mercado() -> dict:
    """
    Executa análise completa de mercado (Camada 1)
    
    Fluxo:
    1. Busca dados de mercado (database_helper existente)
    2. Define ciclo baseado na matriz (score + MVRV + NUPL)
    3. Retorna dados para substituir mock no service principal
    
    Returns:
        dict: Dados da análise de mercado para Dashboard V3
    """
    try:
        logger.info("📊 Executando Análise Mercado - Camada 1")
        
        # 1. Buscar dados do banco (reutiliza função existente)
        dados_mercado = _get_dados_mercado_db()
        
        if not dados_mercado:
            raise Exception("Nenhum dado de mercado encontrado")
        
        # 2. Extrair indicadores chave
        score_mercado = float(dados_mercado["score_consolidado"])
        indicadores = json.loads(dados_mercado["indicadores_json"])
        
        mvrv = indicadores["ciclo"]["mvrv"]["valor"]
        nupl = indicadores["ciclo"]["nupl"]["valor"]
        
        # 3. Determinar ciclo usando matriz definitiva
        ciclo_definido = definir_ciclo_mercado(score_mercado, mvrv, nupl)
        
        # 4. Determinar posicionamento e tamanho baseado no ciclo
        estrategia_posicao = definir_estrategia_posicionamento(ciclo_definido)
        
        # 5. Retornar dados formatados para Dashboard V3
        resultado = {
            "timestamp": dados_mercado["timestamp"].isoformat(),
            "score_mercado": score_mercado,
            "classificacao_mercado": dados_mercado["classificacao_consolidada"],
            "ciclo": ciclo_definido["nome"],
            "ciclo_detalhes": ciclo_definido,
            "estrategia": estrategia_posicao,
            "indicadores": {
                "mvrv": mvrv,
                "nupl": nupl,
                "score_ciclo": float(dados_mercado["score_ciclo"]),
                "score_momentum": float(dados_mercado["score_momentum"]),
                "score_tecnico": float(dados_mercado["score_tecnico"])
            }
        }
        
        logger.info(f"✅ Mercado analisado: {ciclo_definido['nome']} - Score {score_mercado}")
        return resultado
        
    except Exception as e:
        logger.error(f"❌ Erro análise mercado: {str(e)}")
        raise Exception(f"Falha na análise de mercado: {str(e)}")

def definir_ciclo_mercado(score: float, mvrv: float, nupl: float) -> dict:
    """
    Define ciclo baseado na matriz definitiva de ciclos
    
    Regras de prevalência:
    1. NUPL < 0 sempre indica zona de compra (override tudo)
    2. MVRV > 4 sempre indica topo (override tudo exceto NUPL < 0)
    3. Score extremos (0-20 ou 90-100) prevalecem sobre faixas intermediárias
    """
    
    # Regra 1: NUPL < 0 - ZONA DE COMPRA EXTREMA
    if nupl < 0:
        if score <= 20:
            return {
                "nome": "CAPITULAÇÃO",
                "caracteristicas": "Pânico total, fundos fechando",
                "estrategia": "All-in histórico",
                "confianca": 95,
                "override": "NUPL_NEGATIVO"
            }
        else:
            return {
                "nome": "BEAR PROFUNDO", 
                "caracteristicas": "Desespero, mídia negativa",
                "estrategia": "Acumular forte",
                "confianca": 90,
                "override": "NUPL_NEGATIVO"
            }
    
    # Regra 2: MVRV > 4 - ZONA DE TOPO
    if mvrv > 4.0:
        return {
            "nome": "TOPO MANIA",
            "caracteristicas": "Euforia extrema, notícias mainstream",
            "estrategia": "Sair 80-100%",
            "confianca": 95,
            "override": "MVRV_EXTREMO"
        }
    
    # Regra 3: Scores extremos
    if score >= 90:
        if mvrv < 0.8:
            return {
                "nome": "REVERSÃO ÉPICA",
                "caracteristicas": "V-bottom histórico", 
                "estrategia": "Compra máxima",
                "confianca": 95,
                "override": "SCORE_EXTREMO"
            }
        else:
            return {
                "nome": "EUFORIA",
                "caracteristicas": "Parabólico, retail all-in",
                "estrategia": "Sair 50-80%",
                "confianca": 90,
                "override": "SCORE_EXTREMO"
            }
    
    if score <= 20:
        if mvrv < 1.0:
            return {
                "nome": "CAPITULAÇÃO",
                "caracteristicas": "Pânico total, fundos fechando",
                "estrategia": "All-in histórico", 
                "confianca": 90,
                "override": "SCORE_EXTREMO"
            }
        else:
            return {
                "nome": "TOPO MANIA",
                "caracteristicas": "Euforia extrema, notícias mainstream",
                "estrategia": "Sair 80-100%",
                "confianca": 85,
                "override": "SCORE_EXTREMO"
            }
    
    # Matriz normal - sem overrides
    return _aplicar_matriz_normal(score, mvrv, nupl)

def _aplicar_matriz_normal(score: float, mvrv: float, nupl: float) -> dict:
    """
    Aplica matriz normal quando não há overrides
    """
    
    # Faixa 80-90: BULL FORTE
    if 80 <= score < 90:
        if mvrv < 1.0:
            return {
                "nome": "OPORTUNIDADE GERACIONAL",
                "caracteristicas": "Capitulação com reversão técnica",
                "estrategia": "All-in + Alavancagem",
                "confianca": 85
            }
        else:
            return {
                "nome": "BULL FORTE",
                "caracteristicas": "Momentum poderoso, notícias positivas", 
                "estrategia": "Hold + Stops",
                "confianca": 80
            }
    
    # Faixa 70-80: BULL CONFIRMADO
    if 70 <= score < 80:
        if mvrv < 1.2:
            return {
                "nome": "NOVO CICLO",
                "caracteristicas": "Saindo de bear, reversão confirmada",
                "estrategia": "Alavancagem máxima",
                "confianca": 85
            }
        else:
            return {
                "nome": "BULL CONFIRMADO",
                "caracteristicas": "Tendência clara, FOMO inicial",
                "estrategia": "Hold + Comprar dips", 
                "confianca": 80
            }
    
    # Faixa 60-70: BULL INICIAL
    if 60 <= score < 70:
        if mvrv < 1.8:
            return {
                "nome": "SAÍDA ACUMULAÇÃO",
                "caracteristicas": "Volume crescente, breakouts",
                "estrategia": "Posição completa",
                "confianca": 75
            }
        else:
            return {
                "nome": "BULL INICIAL",
                "caracteristicas": "Rompimentos, otimismo crescente",
                "estrategia": "Comprar rallies",
                "confianca": 75
            }
    
    # Faixa 50-60: NEUTRO
    if 50 <= score < 60:
        if mvrv < 2.0:
            return {
                "nome": "NEUTRO",
                "caracteristicas": "Consolidação, baixa volatilidade",
                "estrategia": "Aguardar sinal",
                "confianca": 65
            }
        else:
            return {
                "nome": "NEUTRO ALTA",
                "caracteristicas": "Indecisão com viés positivo",
                "estrategia": "Posição base",
                "confianca": 70
            }
    
    # Faixa 40-50: ACUMULAÇÃO/CORREÇÃO
    if 40 <= score < 50:
        if mvrv < 2.0:
            return {
                "nome": "ACUMULAÇÃO",
                "caracteristicas": "Lateralização, volume baixo",
                "estrategia": "Pequenas entradas",
                "confianca": 70
            }
        else:
            return {
                "nome": "CORREÇÃO BULL",
                "caracteristicas": "Pullback em tendência alta", 
                "estrategia": "Comprar correção",
                "confianca": 75
            }
    
    # Faixa 30-40: RECUPERAÇÃO/BULL TARDIO
    if 30 <= score < 40:
        if mvrv < 1.5:
            return {
                "nome": "RECUPERAÇÃO",
                "caracteristicas": "Bear acabando, sentimento melhorando",
                "estrategia": "DCA conservador",
                "confianca": 70
            }
        else:
            return {
                "nome": "BULL TARDIO",
                "caracteristicas": "Ganância crescente, leverage alta",
                "estrategia": "Realizar gradual",
                "confianca": 75
            }
    
    # Faixa 20-30: BEAR PROFUNDO/DISTRIBUIÇÃO
    if 20 <= score < 30:
        if mvrv < 1.2:
            return {
                "nome": "BEAR PROFUNDO",
                "caracteristicas": "Desespero, mídia negativa",
                "estrategia": "Acumular forte",
                "confianca": 75
            }
        else:
            return {
                "nome": "DISTRIBUIÇÃO",
                "caracteristicas": "Smart money vendendo, retail comprando",
                "estrategia": "Realizar 60%+",
                "confianca": 80
            }
    
    # Default: Score muito baixo
    return {
        "nome": "INDEFINIDO",
        "caracteristicas": "Condições atípicas",
        "estrategia": "Aguardar clareza",
        "confianca": 30
    }

def definir_estrategia_posicionamento(ciclo: dict) -> dict:
    """
    Define estratégia de posicionamento baseada no ciclo identificado
    """
    
    estrategias = {
        "CAPITULAÇÃO": {
            "posicionamento": "COMPRA_MAXIMA",
            "tamanho_posicao": "50-75%",
            "alavancagem_sugerida": "3.0x",
            "urgencia": "extrema"
        },
        "BEAR PROFUNDO": {
            "posicionamento": "ACUMULAR",
            "tamanho_posicao": "30-40%", 
            "alavancagem_sugerida": "2.5x",
            "urgencia": "alta"
        },
        "RECUPERAÇÃO": {
            "posicionamento": "DCA_CONSERVADOR",
            "tamanho_posicao": "20-30%",
            "alavancagem_sugerida": "2.0x", 
            "urgencia": "media"
        },
        "ACUMULAÇÃO": {
            "posicionamento": "ENTRADAS_PEQUENAS",
            "tamanho_posicao": "10-20%",
            "alavancagem_sugerida": "2.0x",
            "urgencia": "baixa"
        },
        "NEUTRO": {
            "posicionamento": "AGUARDAR", 
            "tamanho_posicao": "10-15%",
            "alavancagem_sugerida": "1.5x",
            "urgencia": "baixa"
        },
        "BULL INICIAL": {
            "posicionamento": "COMPRAR_RALLIES",
            "tamanho_posicao": "25-35%",
            "alavancagem_sugerida": "2.5x",
            "urgencia": "media"
        },
        "BULL CONFIRMADO": {
            "posicionamento": "HOLD_E_COMPRAR_DIPS",
            "tamanho_posicao": "20-30%", 
            "alavancagem_sugerida": "2.0x",
            "urgencia": "media"
        },
        "BULL FORTE": {
            "posicionamento": "HOLD_COM_STOPS",
            "tamanho_posicao": "10-20%",
            "alavancagem_sugerida": "1.5x",
            "urgencia": "baixa"
        },
        "EUFORIA": {
            "posicionamento": "REALIZAR_LUCROS",
            "tamanho_posicao": "REDUZIR_50-80%",
            "alavancagem_sugerida": "1.0x",
            "urgencia": "alta"
        },
        "TOPO MANIA": {
            "posicionamento": "SAIR_POSICAO",
            "tamanho_posicao": "REDUZIR_80-100%", 
            "alavancagem_sugerida": "0x",
            "urgencia": "extrema"
        }
    }
    
    nome_ciclo = ciclo["nome"]
    estrategia_base = estrategias.get(nome_ciclo, estrategias["NEUTRO"])
    
    return {
        **estrategia_base,
        "ciclo_base": nome_ciclo,
        "confianca_ciclo": ciclo.get("confianca", 50)
    }

def _get_dados_mercado_db() -> dict:
    """
    Busca dados de mercado usando função existente do database_helper
    """
    try:
        from app.services.v3.dash_mercado.utils.database_helper import get_latest_scores_from_db
        
        dados = get_latest_scores_from_db()
        
        if dados:
            logger.info(f"✅ Dados mercado obtidos - ID: {dados['id']}")
            return dados
        else:
            logger.warning("⚠️ Nenhum dado de mercado encontrado")
            return None
            
    except Exception as e:
        logger.error(f"❌ Erro buscar dados mercado: {str(e)}")
        return None