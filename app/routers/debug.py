# Adicionar em app/routers/debug.py

@router.get("/test-ema-calculation")
async def debug_test_ema_calculation():
    """Testa cálculo completo EMAs e scores"""
    try:
        from app.services.utils.helpers.ema_calculator import get_complete_ema_analysis
        
        result = get_complete_ema_analysis()
        
        return {
            "status": "success" if result.get("status") == "success" else "error",
            "data": result,
            "note": "Teste do cálculo completo EMAs com scores"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.post("/test-coleta-tecnico")
async def debug_test_coleta_tecnico(forcar_coleta: bool = True):
    """Testa coleta completa técnico com gravação no PostgreSQL"""
    try:
        from app.services.coleta.tecnico import coletar
        
        result = coletar(forcar_coleta)
        
        return {
            "status": "success" if result.get("status") == "sucesso" else "error", 
            "data": result,
            "note": "Teste da coleta técnico com gravação PostgreSQL"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/test-dados-tecnico-db")
async def debug_test_dados_tecnico_db():
    """Testa leitura dos dados técnicos do PostgreSQL"""
    try:
        from app.services.utils.helpers.postgres.tecnico_helper import get_dados_tecnico, get_emas_detalhadas
        
        # Dados básicos
        dados_basicos = get_dados_tecnico()
        
        # EMAs detalhadas
        emas_detalhadas = get_emas_detalhadas()
        
        return {
            "status": "success",
            "data": {
                "dados_basicos": dados_basicos,
                "emas_detalhadas": emas_detalhadas,
                "tem_dados": dados_basicos is not None,
                "tem_emas": emas_detalhadas is not None
            },
            "note": "Teste de leitura dados técnicos PostgreSQL"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }