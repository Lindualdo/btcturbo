# app/routers/debug.py

from fastapi import APIRouter
from datetime import datetime
from app.services.utils.helpers.market_cap_helper import (
    get_current_market_cap, compare_with_reference, get_btc_price, get_btc_supply
)
from app.services.utils.helpers.realized_cap_helper import (
    get_current_realized_cap, compare_realized_cap_sources, BigQueryHelper
)

router = APIRouter()

@router.get("/market-cap")
async def debug_market_cap():
    """Debug endpoint para testar cálculo de Market Cap"""
    try:
        result = get_current_market_cap()
        result["timestamp"] = datetime.utcnow().isoformat()
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/market-cap-comparison")
async def debug_market_cap_comparison():
    """Compara nosso Market Cap com referência CoinGecko"""
    try:
        comparison = compare_with_reference()
        return {
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
            "comparison": comparison
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/btc-price")
async def debug_btc_price():
    """Testa apenas a coleta de preço BTC"""
    try:
        price, source = get_btc_price()
        return {
            "status": "success",
            "price": price,
            "source": source,
            "formatted": f"${price:,.2f}",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/btc-supply")
async def debug_btc_supply():
    """Testa apenas a coleta de supply BTC"""
    try:
        supply, source = get_btc_supply()
        return {
            "status": "success",
            "supply": supply,
            "source": source,
            "formatted": f"{supply:,.0f} BTC",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/realized-cap")
async def debug_realized_cap():
    """Testa cálculo de Realized Cap"""
    try:
        result = get_current_realized_cap()
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/realized-cap-comparison")
async def debug_realized_cap_comparison():
    """Compara BigQuery vs APIs para Realized Cap"""
    try:
        comparison = compare_realized_cap_sources()
        return {
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
            "sources": comparison
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/bigquery-detailed-test")
async def debug_bigquery_detailed():
    """Teste BigQuery com máximo detalhe possível"""
    try:
        from app.config import get_settings
        import json
        from google.oauth2 import service_account
        from google.cloud import bigquery
        
        settings = get_settings()
        
        # 1. Parse credenciais
        try:
            cred_info = json.loads(settings.GOOGLE_APPLICATION_CREDENTIALS_JSON)
            service_email = cred_info.get('client_email', 'NOT_FOUND')
            project_from_json = cred_info.get('project_id', 'NOT_FOUND')
        except Exception as e:
            return {"error": f"JSON parse failed: {str(e)}"}
        
        # 2. Verificar dados básicos
        config_details = {
            "project_from_settings": settings.GOOGLE_CLOUD_PROJECT,
            "project_from_json": project_from_json,
            "service_account_email": service_email,
            "projects_match": settings.GOOGLE_CLOUD_PROJECT == project_from_json
        }
        
        # 3. Tentar criar credentials
        try:
            credentials = service_account.Credentials.from_service_account_info(cred_info)
            cred_status = "✅ Credentials criadas"
        except Exception as e:
            return {
                "status": "error",
                "error": f"Credentials creation failed: {str(e)}",
                "config": config_details
            }
        
        # 4. Tentar criar client
        try:
            client = bigquery.Client(
                credentials=credentials,
                project=settings.GOOGLE_CLOUD_PROJECT
            )
            client_status = "✅ Client criado"
        except Exception as e:
            return {
                "status": "error", 
                "error": f"Client creation failed: {str(e)}",
                "config": config_details,
                "credentials_status": cred_status
            }
        
        # 5. Tentar query mais simples possível
        try:
            # Query que não acessa dados externos - só sistema
            simple_query = "SELECT 1 as test_number"
            job = client.query(simple_query)
            results = list(job)
            query_status = f"✅ Query OK - resultado: {results[0]['test_number']}"
        except Exception as e:
            return {
                "status": "error",
                "error": f"Simple query failed: {str(e)}",
                "error_details": {
                    "type": type(e).__name__,
                    "message": str(e)
                },
                "config": config_details,
                "credentials_status": cred_status,
                "client_status": client_status
            }
        
        # 6. Tentar acessar dataset público
        try:
            public_query = "SELECT COUNT(*) as total FROM `bigquery-public-data.crypto_bitcoin.transactions` LIMIT 1"
            job2 = client.query(public_query)
            results2 = list(job2)
            public_access = f"✅ Acesso público OK - total: {results2[0]['total']}"
        except Exception as e:
            public_access = f"❌ Acesso público falhou: {str(e)}"
        
        return {
            "status": "success",
            "config": config_details,
            "credentials_status": cred_status,
            "client_status": client_status,
            "simple_query_status": query_status,
            "public_data_access": public_access,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": f"Unexpected error: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        }