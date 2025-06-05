# app/dependencies.py

from fastapi import Depends
from tvDatafeed import TvDatafeed
from notion_client import Client as NotionClient
from google.cloud import bigquery
from google.oauth2 import service_account
import requests

from app.config import get_settings, Settings


def get_tv_client(settings: Settings = Depends(get_settings)) -> TvDatafeed:
    """Instância autenticada do tvDatafeed (TradingView)."""
    return TvDatafeed(
        username=settings.TV_USERNAME,
        password=settings.TV_PASSWORD
    )


def get_notion_client(settings: Settings = Depends(get_settings)) -> NotionClient:
    """Instância autenticada do Notion."""
    return NotionClient(auth=settings.NOTION_TOKEN)


def get_bigquery_client(settings: Settings = Depends(get_settings)) -> bigquery.Client:
    """Instância autenticada do BigQuery (opcional)."""
    credentials = service_account.Credentials.from_service_account_info(
        settings.GCP_CREDENTIALS
    )
    return bigquery.Client(credentials=credentials, project=settings.GCP_PROJECT_ID)


def get_glassnode_key(settings: Settings = Depends(get_settings)) -> str:
    """Chave da API Glassnode."""
    return settings.GLASSNODE_API_KEY


def get_coinglass_key(settings: Settings = Depends(get_settings)) -> str:
    """Chave da API Coinglass."""
    return settings.COINGLASS_API_KEY


def get_aave_rpc_endpoint(settings: Settings = Depends(get_settings)) -> str:
    """Endpoint RPC para acessar contratos da AAVE."""
    return settings.AAVE_RPC_URL


def get_http_session() -> requests.Session:
    """Sessão HTTP genérica para requisições reutilizáveis."""
    return requests.Session()
