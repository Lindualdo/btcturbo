from app.services.ciclo import mvrv_z_score, realized_ratio, puell_multiple

def calcular_bloco_ciclo():
    return {
        "score": 5.5,
        "indicadores": {
            "MVRV_Z": mvrv_z_score.calcular_score_mvrv(),
            "Realized_Ratio": realized_ratio.calcular_score_realized(),
            "Puell_Multiple": puell_multiple.calcular_score_puell()
        }
    }