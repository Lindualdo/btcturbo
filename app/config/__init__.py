# app/config/__init__.py

# Configurações existentes
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List, Optional
from functools import lru_cache

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "BTC TURBO"
    APP_VERSION: str = "1.0.1"
    HOST: str = Field("0.0.0.0", description="Host address for Uvicorn")
    PORT: int = Field(8000, description="Port for Uvicorn server")

    # TradingView credentials (tvdatafeed)
    TV_USERNAME: str = Field(..., env="TV_USERNAME")
    TV_PASSWORD: str = Field(..., env="TV_PASSWORD")

    # Notion integration
    NOTION_TOKEN: str = Field(..., env="NOTION_TOKEN")
    NOTION_DATABASE_ID: str = Field(..., env="NOTION_DATABASE_ID")

    # PostgreSQL connection
    DB_HOST: str = Field(..., env="DB_HOST")
    DB_NAME: str = Field(..., env="DB_NAME") 
    DB_USER: str = Field(..., env="DB_USER")
    DB_PASSWORD: str = Field(..., env="DB_PASSWORD")
    DB_PORT: int = Field(5432, env="DB_PORT")
    
    DATABASE_URL: Optional[str] = Field(None, env="DATABASE_URL")

    # Google Cloud BigQuery
    GOOGLE_APPLICATION_CREDENTIALS_JSON: str = Field(..., env="GOOGLE_APPLICATION_CREDENTIALS_JSON")
    GOOGLE_CLOUD_PROJECT: str = Field(..., env="GOOGLE_CLOUD_PROJECT")

    # APIs Externas
    GLASSNODE_API_KEY: Optional[str] = Field(None, env="GLASSNODE_API_KEY")
    COINGLASS_API_KEY: Optional[str] = Field(None, env="COINGLASS_API_KEY")
    AAVE_RPC_URL: Optional[str] = Field(None, env="AAVE_RPC_URL")

    # Indicator weights and thresholds
    WEIGHT_EMA_200: float = Field(0.25, description="Peso para BTC vs 200D EMA")
    WEIGHT_REALIZED_PRICE: float = Field(0.25, description="Peso para Realized Price")
    WEIGHT_PUELL_MULTIPLE: float = Field(0.20, description="Peso para Puell Multiple")
    WEIGHT_BTC_DOMINANCE: float = Field(0.20, description="Peso para BTC Dominance")
    WEIGHT_MACRO_M2: float = Field(0.60, description="Peso para Macro M2 global")
    WEIGHT_MACRO_US10Y: float = Field(0.40, description="Peso para Macro US10Y yield")

    # Cache settings
    CACHE_EXPIRATION_SECONDS: int = Field(300, description="Tempo de expiração do cache em segundos")

    # TradingView default symbol
    TV_SYMBOL: str = Field("BTCUSDT", description="Símbolo usado nas chamadas ao TradingView")
    TV_EXCHANGE: str = Field("BINANCE", description="Exchange para consulta de dados")

    WALLET_ADDRESS: str = Field(..., env="WALLET_ADDRESS")
    AAVE_RPC_URL: str = Field(..., env="AAVE_RPC_URL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> Settings:
    """Retorna uma instância singleton das configurações carregadas do .env"""
    return Settings()

# Dashboard config (novo)
from .dashboard_config import DASHBOARD_CONFIG

__all__ = ["get_settings", "Settings", "DASHBOARD_CONFIG"]