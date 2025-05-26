# app/routers/test_notion.py

from fastapi import APIRouter, HTTPException
from datetime import datetime
import logging
from app.services.utils.postgres_helper import get_status_todos_blocos

router = APIRouter()


@router.get("/test-postgres", summary="Teste PostgreSQL", tags=["Debug"])
def test_postgres():
    try:
       
        status = get_status_todos_blocos()
        return {"status": "sucesso", "postgres": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail={"erro": str(e)})


@router.get("/test-notion-ciclo", summary="Teste Notion Ciclo", tags=["Debug"])
def test_notion_ciclo():
    """
    Endpoint para testar a integração completa Notion → PostgreSQL
    """
    try:
        from app.services.integracao.notion_ciclo_reader import update_ciclo_from_notion
        
        # Chama a função que lê Notion E salva no PostgreSQL
        sucesso = update_ciclo_from_notion()
        
        if sucesso:
            return {
                "status": "sucesso",
                "message": "Dados lidos do Notion e salvos no PostgreSQL",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        else:
            raise Exception("Falha ao processar dados")
            
    except Exception as e:
        logging.error(f"Erro no teste Notion→PostgreSQL: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
        
    except Exception as e:
        logging.error(f"Erro no teste Notion: {str(e)}")
        raise HTTPException(status_code=500, detail={
            "status": "erro",
            "erro": str(e),
            "checklist": [
                "Verificar NOTION_TOKEN no .env",
                "Verificar NOTION_DATABASE_ID no .env", 
                "Verificar se tabela tbl_ciclos existe",
                "Verificar permissões do bot",
                "Verificar nomes dos campos na tabela"
            ]
        })

@router.get("/test-notion-individual/{indicador}", summary="Teste Indicador Individual", tags=["Debug"])
def test_notion_individual(indicador: str):
    """
    Testa busca de um indicador específico
    Indicadores válidos: mvrv_z-score, realized_price, puell_multiple
    """
    try:
        from app.services.integracao.notion_ciclo_reader import get_individual_indicator_from_notion
        
        valor = get_individual_indicator_from_notion(indicador)
        
        return {
            "status": "sucesso",
            "indicador": indicador,
            "valor": valor,
            "encontrado": valor is not None,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    except Exception as e:
        logging.error(f"Erro ao buscar indicador {indicador}: {str(e)}")
        raise HTTPException(status_code=500, detail={
            "status": "erro",
            "indicador": indicador,
            "erro": str(e)
        })

@router.get("/test-config", summary="Teste Configurações", tags=["Debug"])
def test_config():
    """
    Verifica se as configurações estão corretas
    """
    try:
        from app.config import get_settings
        settings = get_settings()
        
        return {
            "status": "sucesso",
            "configuracoes": {
                "notion_token_exists": bool(getattr(settings, 'NOTION_TOKEN', None)),
                "notion_token_length": len(getattr(settings, 'NOTION_TOKEN', '')) if getattr(settings, 'NOTION_TOKEN', None) else 0,
                "database_id_exists": bool(getattr(settings, 'NOTION_DATABASE_ID', None)),
                "database_id": getattr(settings, 'NOTION_DATABASE_ID', 'NOT_SET'),
                "app_name": getattr(settings, 'APP_NAME', 'NOT_SET')
            },
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    except Exception as e:
        logging.error(f"Erro ao verificar configurações: {str(e)}")
        raise HTTPException(status_code=500, detail={
            "status": "erro",
            "erro": str(e)
        })