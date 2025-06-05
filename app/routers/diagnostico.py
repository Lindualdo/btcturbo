# app/routers/diagnostico.py

from fastapi import APIRouter, HTTPException
from datetime import datetime
from app.services.utils.helpers.postgres import (
    test_connection,
    check_database_health,
    create_tables_if_not_exist,
    insert_dados_exemplo,
    get_all_latest_data
)

router = APIRouter()

@router.get("/health-check")
async def health_check():
    """Verifica saúde geral do sistema"""
    try:
        # Testar conexão básica
        connection_ok = test_connection()
        
        if not connection_ok:
            raise HTTPException(status_code=500, detail="Falha na conexão PostgreSQL")
        
        # Verificar saúde das tabelas
        health_status = check_database_health()
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "system_status": "✅ HEALTHY",
            "postgresql_connection": "✅ CONNECTED",
            "health_details": health_status
        }
        
    except Exception as e:
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "system_status": "❌ ERROR",
            "postgresql_connection": "❌ FAILED",
            "error": str(e)
        }

@router.post("/setup-database")
async def setup_database():
    """Cria tabelas e insere dados de exemplo (desenvolvimento)"""
    try:
        # Criar tabelas se não existirem
        tables_created = create_tables_if_not_exist()
        
        if not tables_created:
            raise HTTPException(status_code=500, detail="Falha ao criar tabelas")
        
        # Inserir dados de exemplo
        dados_inseridos = insert_dados_exemplo()
        
        if not dados_inseridos:
            raise HTTPException(status_code=500, detail="Falha ao inserir dados de exemplo")
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "✅ SUCCESS",
            "message": "Database configurado com sucesso",
            "actions": [
                "Tabelas criadas/verificadas",
                "Dados de exemplo inseridos",
                "Sistema pronto para uso"
            ]
        }
        
    except Exception as e:
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "❌ ERROR",
            "message": "Falha na configuração do database",
            "error": str(e)
        }

@router.get("/test-indicadores")
async def test_indicadores():
    """Testa se todas as APIs de indicadores estão funcionando"""
    try:
        from app.services.indicadores import ciclos, momentum, riscos, tecnico
        
        # Testar todos os blocos
        resultados = {
            "ciclo": ciclos.obter_indicadores(),
            "momentum": momentum.obter_indicadores(),
            "riscos": riscos.obter_indicadores(),
            "tecnico": tecnico.obter_indicadores()
        }
        
        # Verificar status de cada bloco
        status_summary = {}
        for bloco, resultado in resultados.items():
            status_summary[bloco] = {
                "status": resultado.get("status", "unknown"),
                "has_data": resultado.get("status") == "success",
                "timestamp": resultado.get("timestamp")
            }
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "test_status": "✅ COMPLETED",
            "summary": status_summary,
            "detailed_results": resultados
        }
        
    except Exception as e:
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "test_status": "❌ FAILED",
            "error": str(e)
        }

@router.get("/dados-consolidados")
async def dados_consolidados():
    """Retorna todos os dados mais recentes de forma consolidada"""
    try:
        dados = get_all_latest_data()
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "✅ SUCCESS",
            "dados": dados
        }
        
    except Exception as e:
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "❌ ERROR", 
            "error": str(e)
        }