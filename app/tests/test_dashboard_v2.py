# app/tests/test_dashboard_v2.py

import pytest
from unittest.mock import patch, MagicMock
from app.services.v2.dashboard_home_service import (
    calcular_dashboard_v2, 
    obter_dashboard_v2
)

class TestDashboardV2:
    """Testes para Dashboard V2"""
    
    def test_calcular_dashboard_v2_success(self):
        """Teste cálculo dashboard V2 com sucesso"""
        
        # Mock dos dados coletados
        mock_data = {
            "btc_price": 65000.0,
            "score_mercado": 67.5,
            "score_risco": 75.2,
            "mvrv": 1.85,
            "health_factor": 1.92,
            "alavancagem_atual": 1.8,
            "alavancagem_permitida": 2.5,
            "ema_distance": 8.5,
            "rsi_diario": 52.3
        }
        
        with patch('app.services.utils.helpers.v2.dashboard_home.data_collector.collect_all_data') as mock_collect:
            mock_collect.return_value = mock_data
            
            with patch('app.services.utils.helpers.v2.dashboard_home.database_v2_helper.save_dashboard_v2') as mock_save:
                mock_save.return_value = True
                
                result = calcular_dashboard_v2()
                
                assert result["status"] == "success"
                assert result["versao"] == "v2_otimizado"
                assert "data" in result
    
    def test_obter_dashboard_v2_found(self):
        """Teste obtenção dashboard V2 encontrado"""
        
        mock_dashboard = {
            "id": 1,
            "created_at": "2025-06-13T10:30:00",
            "dashboard_json": '{"timestamp": "2025-06-13T10:30:00Z"}'
        }
        
        with patch('app.services.utils.helpers.v2.dashboard_home.database_v2_helper.get_latest_dashboard_v2') as mock_get:
            mock_get.return_value = mock_dashboard
            
            result = obter_dashboard_v2()
            
            assert result["status"] == "success"
            assert "data" in result
            assert "metadata" in result
    
    def test_obter_dashboard_v2_not_found(self):
        """Teste obtenção dashboard V2 não encontrado"""
        
        with patch('app.services.utils.helpers.v2.dashboard_home.database_v2_helper.get_latest_dashboard_v2') as mock_get:
            mock_get.return_value = None
            
            result = obter_dashboard_v2()
            
            assert result["status"] == "error"
            assert "Nenhum dashboard V2 encontrado" in result["erro"]

# Exemplo de uso dos endpoints
"""
# EXEMPLOS DE USO DOS ENDPOINTS V2

## 1. Calcular Dashboard V2
POST /api/v2/dashboard-home

Response:
{
  "status": "success",
  "versao": "v2_otimizado",
  "timestamp": "2025-06-13T10:30:00Z",
  "data": {
    "timestamp": "2025-06-13T10:30:00Z",
    "versao": "v2_dashboard",
    "header": {
      "btc_price": 65000.0,
      "alavancagem_atual": 1.8,
      "status": "operacional"
    },
    "scores": {
      "mercado": 67.5,
      "risco": 75.2,
      "mvrv": 1.85,
      "health_factor": 1.92
    },
    "estrategia": {
      "decisao": "COMPRAR_25%",
      "ciclo": "BULL_INICIAL",
      "setup_4h": "PULLBACK_TENDENCIA",
      "justificativa": "Ciclo permite compras com setup favorável. Tamanho: 25%",
      "urgencia": "media"
    },
    "tecnicos": {
      "ema_distance": 8.5,
      "rsi_diario": 52.3,
      "preco_ema144": 59800.0
    },
    "alavancagem": {
      "atual": 1.8,
      "permitida": 2.5,
      "valor_disponivel": 15000.0,
      "dist_liquidacao": 45.2
    }
  },
  "message": "Dashboard V2 calculado com sucesso"
}

## 2. Obter Dashboard V2
GET /api/v2/dashboard-home

Response:
{
  "status": "success",
  "data": { ... },  // Mesmo JSON acima
  "metadata": {
    "id": 123,
    "created_at": "2025-06-13T10:30:00Z",
    "age_minutes": 2.5,
    "versao": "v2_otimizado"
  }
}

## 3. Debug Dashboard V2
GET /api/v2/dashboard-home/debug

Response:
{
  "status": "success",
  "versao": "v2_otimizado",
  "ultimo_registro": {
    "id": 123,
    "created_at": "2025-06-13T10:30:00Z",
    "tem_dados": true
  },
  "arquitetura": {
    "collectors": ["data_collector"],
    "processors": ["cycle_analyzer", "setup_detector", "validation_gates", "decision_matrix"],
    "database": "database_v2_helper"
  }
}
"""