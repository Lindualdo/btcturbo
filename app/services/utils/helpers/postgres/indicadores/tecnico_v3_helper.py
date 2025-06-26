# app/services/utils/helpers/postgres/indicadores/tecnico_v3_helper.py
# ADICIONAR estas funções ao arquivo existente

import json
import logging
from datetime import datetime
from typing import Dict, Optional
from app.services.utils.helpers.postgres.base import execute_query

logger = logging.getLogger(__name__)

def insert_dados_tecnico(dados: Dict) -> bool:
    """
    Insere dados técnico completos com novos campos v3.0
    Mantém compatibilidade com campos existentes
    """
    try:
        logger.info(f"💾 Inserindo dados técnico...")
        
        # Converter JSON para string
        distancias_json_str = json.dumps(dados.get("distancias_emas_json", {}))
        
        query = """
            INSERT INTO indicadores_tecnico (
                -- EMAs Semanal
                ema_17_1w, ema_34_1w, ema_144_1w, ema_305_1w, ema_610_1w,
                -- EMAs Diário
                ema_17_1d, ema_34_1d, ema_144_1d, ema_305_1d, ema_610_1d,
                -- Preço atual
                btc_price_current,
                -- Scores v3.0 (compatibilidade)
                score_consolidado_1w, score_consolidado_1d, score_final_ponderado,
                -- Campos v3.0 auditoria
                score_alinhamento_v3_1w, score_expansao_v3_1w,
                score_alinhamento_v3_1d, score_expansao_v3_1d,
                score_tecnico_v3_final, distancias_emas_json, versao_calculo,
                -- Metadados
                fonte, timestamp
            ) VALUES (
                %s, %s, %s, %s, %s,  -- EMAs 1W
                %s, %s, %s, %s, %s,  -- EMAs 1D
                %s,                  -- BTC Price
                %s, %s, %s,          -- Scores v3.0
                %s, %s, %s, %s, %s, %s, %s,  -- Campos v3.0
                %s, %s               -- Metadados
            )
        """
        
        params = (
            # EMAs Semanal
            dados.get("ema_17_1w"), dados.get("ema_34_1w"), dados.get("ema_144_1w"),
            dados.get("ema_305_1w"), dados.get("ema_610_1w"),
            # EMAs Diário
            dados.get("ema_17_1d"), dados.get("ema_34_1d"), dados.get("ema_144_1d"),
            dados.get("ema_305_1d"), dados.get("ema_610_1d"),
            # Preço atual
            dados.get("btc_price_current"),
            # Scores v3.0 (compatibilidade)
            dados.get("score_consolidado_1w"),
            dados.get("score_consolidado_1d"),
            dados.get("score_final_ponderado"),
            # Campos v3.0 auditoria
            dados.get("score_alinhamento_v3_1w"),
            dados.get("score_expansao_v3_1w"), 
            dados.get("score_alinhamento_v3_1d"),
            dados.get("score_expansao_v3_1d"),
            dados.get("score_tecnico_v3_final"),
            distancias_json_str,
            dados.get("versao_calculo", "v3.0"),
            # Metadados
            dados.get("fonte", "tecnico_v3"),
            dados.get("timestamp", datetime.utcnow())
        )
        
        execute_query(query, params)
        logger.info("✅ Dados técnico v3.0 inseridos com sucesso")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao inserir dados técnico v3.0: {str(e)}")
        return False

def get_dados_tecnico() -> Optional[Dict]:
    """
    Busca dados técnicos v3.0 mais recentes
    """
    try:
        logger.info("🔍 Buscando dados técnico v3.0...")
        
        query = """
            SELECT 
                -- Scores v3.0
                score_final_ponderado,
                score_alinhamento_v3_1w, score_expansao_v3_1w,
                score_alinhamento_v3_1d, score_expansao_v3_1d,
                score_tecnico_v3_final, distancias_emas_json, versao_calculo,
                -- EMAs e dados existentes
                ema_17_1w, ema_34_1w, ema_144_1w, ema_305_1w, ema_610_1w,
                ema_17_1d, ema_34_1d, ema_144_1d, ema_305_1d, ema_610_1d,
                btc_price_current, score_bloco_final, bbw_percentage,
                timestamp, fonte
            FROM indicadores_tecnico 
            WHERE versao_calculo = 'v3.0'
            ORDER BY timestamp DESC 
            LIMIT 1
        """
        
        result = execute_query(query, fetch_one=True)
        
        if result:
            logger.info(f"✅ Dados v3.0 encontrados: score={result.get('score_tecnico_v3_final')}")
            return result
        else:
            logger.warning("⚠️ Nenhum dado v3.0 encontrado")
            return None
            
    except Exception as e:
        logger.error(f"❌ Erro ao buscar dados v3.0: {str(e)}")
        return None

    """
    Migra últimos registros para calcular v3.0 retroativamente
    Útil para comparação e validação
    """
    try:
        logger.info(f"🔄 Migrando últimos {limit} registros para v3.0...")
        
        # Buscar registros sem v3.0
        query = """
            SELECT id, ema_17_1w, ema_34_1w, ema_144_1w, ema_305_1w, ema_610_1w,
                   ema_17_1d, ema_34_1d, ema_144_1d, ema_305_1d, ema_610_1d,
                   timestamp
            FROM indicadores_tecnico 
            WHERE score_tecnico_v3_final IS NULL
            ORDER BY timestamp DESC 
            LIMIT %s
        """
        
        registros = execute_query(query, params=(limit,), fetch_all=True)
        
        if not registros:
            return {"migrados": 0, "erro": "Nenhum registro para migrar"}
        
        migrados = 0
        erros = []
        
        from app.services.scores.tecnico_v3.tecnico import calcular_score_v3
        
        for registro in registros:
            try:
                # Preparar EMAs para cálculo v3.0
                emas_semanal = {
                    17: registro["ema_17_1w"], 34: registro["ema_34_1w"],
                    144: registro["ema_144_1w"], 305: registro["ema_305_1w"],
                    610: registro["ema_610_1w"]
                }
                emas_diario = {
                    17: registro["ema_17_1d"], 34: registro["ema_34_1d"],
                    144: registro["ema_144_1d"], 305: registro["ema_305_1d"],
                    610: registro["ema_610_1d"]
                }
                
                # Calcular v3.0 para este registro
                from app.services.scores.tecnico_v3.utils.score_compositor import calcular_score_tecnico_v3
                resultado_v3 = calcular_score_tecnico_v3(emas_semanal, emas_diario)
                
                if resultado_v3["status"] == "success":
                    # Preparar dados para update
                    dados_v3 = {
                        "score_alinhamento_v3_1w": resultado_v3["timeframes"]["semanal"]["alinhamento"]["score"],
                        "score_expansao_v3_1w": resultado_v3["timeframes"]["semanal"]["expansao"]["score"],
                        "score_alinhamento_v3_1d": resultado_v3["timeframes"]["diario"]["alinhamento"]["score"],
                        "score_expansao_v3_1d": resultado_v3["timeframes"]["diario"]["expansao"]["score"],
                        "score_tecnico_v3_final": resultado_v3["score_final"],
                        "distancias_emas_json": {
                            "semanal": resultado_v3["timeframes"]["semanal"]["expansao"]["distancias"],
                            "diario": resultado_v3["timeframes"]["diario"]["expansao"]["distancias"]
                        }
                    }
                    
                    # Atualizar registro
                    if update_score_v3_existing_record(registro["id"], dados_v3):
                        migrados += 1
                    else:
                        erros.append(f"Falha update registro {registro['id']}")
                else:
                    erros.append(f"Falha cálculo v3.0 registro {registro['id']}")
                    
            except Exception as e:
                erros.append(f"Erro registro {registro['id']}: {str(e)}")
        
        logger.info(f"✅ Migração concluída: {migrados}/{len(registros)} registros")
        
        return {
            "total_registros": len(registros),
            "migrados": migrados,
            "erros": erros,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro migração v3.0: {str(e)}")
        return {
            "migrados": 0,
            "erro": str(e),
            "status": "error"
        }