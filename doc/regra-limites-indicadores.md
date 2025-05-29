# app/services/utils/data_validator.py

class DataValidator:
    
    # ==========================================
    # LIMITES GERAIS POR INDICADOR
    # ==========================================
    
    LIMITS = {
        # BLOCO CICLO
        'mvrv_z_score': (-2.0, 8.0),           # Histórico: -1.5 a 7.2
        'realized_ratio': (0.5, 5.0),          # Típico: 0.7 a 3.0
        'puell_multiple': (0.1, 6.0),          # Histórico: 0.3 a 5.5
        
        # BLOCO MOMENTUM  
        'rsi_semanal': (5, 95),                # RSI válido
        'funding_rate': (-0.5, 0.5),           # % - Extremos históricos
        'oi_change': (-80, 200),               # % - Mudança máxima possível
        'long_short_ratio': (0.2, 5.0),        # Ratio extremos
        
        # BLOCO RISCO
        'dist_liquidacao': (0, 100),           # % - Por definição
        'health_factor': (0.1, 10.0),          # AAVE limits
        'exchange_netflow': (-200000, 200000), # BTC - Extremos históricos
        'stablecoin_ratio': (0, 50),           # % - Máximo teórico
        
        # BLOCO TÉCNICO
        'sistema_emas': (0, 10),               # Score por definição
        'padroes_graficos': (0, 10),           # Score por definição
        
        # SCORES CONSOLIDADOS
        'score_bloco': (0, 10),                # Por definição
        'score_final': (0, 10),                # Por definição
    }
    
    # ==========================================
    # LIMITES DE TEMPO (FRESHNESS)
    # ==========================================
    
    MAX_DATA_AGE = {
        'critical': 1 * 3600,      # 1 hora - Health Factor, Funding
        'high': 6 * 3600,          # 6 horas - RSI, MVRV, Preços
        'medium': 24 * 3600,       # 24 horas - On-chain data
        'low': 72 * 3600           # 72 horas - Dados históricos
    }
    
    # ==========================================
    # CLASSIFICAÇÃO DE PRIORIDADE
    # ==========================================
    
    INDICATOR_PRIORITY = {
        # CRÍTICOS (1h max)
        'critical': ['health_factor', 'dist_liquidacao', 'funding_rate'],
        
        # ALTOS (6h max)  
        'high': ['rsi_semanal', 'mvrv_z_score', 'sistema_emas'],
        
        # MÉDIOS (24h max)
        'medium': ['realized_ratio', 'puell_multiple', 'exchange_netflow'],
        
        # BAIXOS (72h max)
        'low': ['stablecoin_ratio', 'padroes_graficos']
    }

    @staticmethod
    def validate_value(indicator_name: str, value: float) -> dict:
        """
        Valida se valor está dentro dos limites aceitáveis
        Retorna: {"valid": bool, "action": str, "message": str}
        """
        if indicator_name not in DataValidator.LIMITS:
            return {"valid": True, "action": "ACCEPT", "message": "Indicador não mapeado"}
        
        min_val, max_val = DataValidator.LIMITS[indicator_name]
        
        if min_val <= value <= max_val:
            return {"valid": True, "action": "ACCEPT", "message": "Valor válido"}
        
        # VALOR FORA DOS LIMITES
        if value < min_val:
            return {
                "valid": False, 
                "action": "CLAMP_MIN", 
                "message": f"Valor {value} abaixo do mínimo {min_val}. Usando {min_val}."
            }
        
        if value > max_val:
            return {
                "valid": False,
                "action": "CLAMP_MAX", 
                "message": f"Valor {value} acima do máximo {max_val}. Usando {max_val}."
            }

    @staticmethod
    def validate_freshness(indicator_name: str, timestamp: datetime) -> dict:
        """
        Valida se dados estão dentro do prazo aceitável
        """
        now = datetime.utcnow()
        data_age = (now - timestamp).total_seconds()
        
        # Determinar prioridade do indicador
        priority = None
        for prio, indicators in DataValidator.INDICATOR_PRIORITY.items():
            if indicator_name in indicators:
                priority = prio
                break
        
        if not priority:
            priority = 'medium'  # Default
        
        max_age = DataValidator.MAX_DATA_AGE[priority]
        
        if data_age <= max_age:
            return {"fresh": True, "action": "ACCEPT", "age_hours": data_age/3600}
        
        # DADOS ANTIGOS
        if data_age <= DataValidator.MAX_DATA_AGE['low']:
            return {
                "fresh": False,
                "action": "USE_WITH_WARNING", 
                "age_hours": data_age/3600,
                "message": f"Dados antigos ({data_age/3600:.1f}h) mas utilizáveis"
            }
        
        # DADOS MUITO ANTIGOS
        return {
            "fresh": False,
            "action": "REJECT_USE_FALLBACK",
            "age_hours": data_age/3600, 
            "message": f"Dados muito antigos ({data_age/3600:.1f}h). Usar fallback."
        }

    @staticmethod
    def apply_validation_rules(bloco_data: dict) -> dict:
        """
        Aplica regras de validação em um bloco completo
        Retorna dados sanitizados + relatório de validação
        """
        validated_data = bloco_data.copy()
        validation_report = {
            "errors": [],
            "warnings": [],
            "actions_taken": []
        }
        
        # Validar cada indicador
        for indicator_name, indicator_data in bloco_data.get("indicadores", {}).items():
            
            # 1. VALIDAR VALOR
            if "valor" in indicator_data:
                valor = indicator_data["valor"]
                
                # Converter strings para float quando possível
                if isinstance(valor, str):
                    try:
                        # Remove % e converte
                        clean_valor = float(valor.replace('%', '').replace('+', ''))
                        if valor.endswith('%'):
                            clean_valor = clean_valor / 100  # Converter % para decimal
                    except:
                        clean_valor = 0.0
                        validation_report["errors"].append(f"{indicator_name}: Valor não numérico")
                else:
                    clean_valor = float(valor)
                
                # Aplicar validação
                validation = DataValidator.validate_value(indicator_name.lower(), clean_valor)
                
                if not validation["valid"]:
                    if validation["action"] == "CLAMP_MIN":
                        min_val, _ = DataValidator.LIMITS[indicator_name.lower()]
                        validated_data["indicadores"][indicator_name]["valor"] = min_val
                        validation_report["actions_taken"].append(f"{indicator_name}: Clamped to minimum {min_val}")
                    
                    elif validation["action"] == "CLAMP_MAX":
                        _, max_val = DataValidator.LIMITS[indicator_name.lower()]
                        validated_data["indicadores"][indicator_name]["valor"] = max_val
                        validation_report["actions_taken"].append(f"{indicator_name}: Clamped to maximum {max_val}")
            
            # 2. VALIDAR FRESHNESS
            if "timestamp" in bloco_data:
                timestamp = datetime.fromisoformat(bloco_data["timestamp"].replace('Z', '+00:00'))
                freshness = DataValidator.validate_freshness(indicator_name.lower(), timestamp)
                
                if not freshness["fresh"]:
                    if freshness["action"] == "USE_WITH_WARNING":
                        validation_report["warnings"].append(
                            f"{indicator_name}: {freshness['message']}"
                        )
                    elif freshness["action"] == "REJECT_USE_FALLBACK":
                        validation_report["errors"].append(
                            f"{indicator_name}: {freshness['message']}"
                        )
                        # Zerar peso do indicador
                        validated_data["indicadores"][indicator_name]["peso_efetivo"] = "0%"
        
        return {
            "data": validated_data,
            "validation": validation_report
        }

# ==========================================
# INTEGRAÇÃO NO CONSOLIDADOR
# ==========================================

# app/services/scores/consolidador.py (NOVO)

from .data_validator import DataValidator

def consolidar_analise_btc():
    """
    Consolidador principal com validação integrada
    """
    
    # 1. Obter dados brutos de todos os blocos
    dados_ciclo = ciclos.calcular_score()
    dados_momentum = momentum.calcular_score() 
    dados_risco = riscos.calcular_score()
    dados_tecnico = tecnico.calcular_score()
    
    # 2. APLICAR VALIDAÇÃO EM CADA BLOCO
    ciclo_validated = DataValidator.apply_validation_rules(dados_ciclo)
    momentum_validated = DataValidator.apply_validation_rules(dados_momentum)
    risco_validated = DataValidator.apply_validation_rules(dados_risco)
    tecnico_validated = DataValidator.apply_validation_rules(dados_tecnico)
    
    # 3. Compilar relatório de validação
    validation_summary = {
        "total_errors": len(ciclo_validated["validation"]["errors"]) + 
                       len(momentum_validated["validation"]["errors"]) +
                       len(risco_validated["validation"]["errors"]) +
                       len(tecnico_validated["validation"]["errors"]),
        
        "total_warnings": len(ciclo_validated["validation"]["warnings"]) + 
                         len(momentum_validated["validation"]["warnings"]) +
                         len(risco_validated["validation"]["warnings"]) +
                         len(tecnico_validated["validation"]["warnings"]),
        
        "actions_taken": (ciclo_validated["validation"]["actions_taken"] +
                         momentum_validated["validation"]["actions_taken"] +
                         risco_validated["validation"]["actions_taken"] +
                         tecnico_validated["validation"]["actions_taken"])
    }
    
    # 4. CIRCUIT BREAKER - Muitos erros = sistema não confiável
    if validation_summary["total_errors"] > 3:
        return {
            "status": "SYSTEM_UNRELIABLE",
            "message": "Muitos dados inválidos. Sistema em modo seguro.",
            "kelly_allocation": "0%",
            "acao_recomendada": "Aguardar correção dos dados",
            "validation_summary": validation_summary
        }
    
    # 5. Calcular score final com dados validados
    dados_limpos = {
        "ciclo": ciclo_validated["data"],
        "momentum": momentum_validated["data"], 
        "risco": risco_validated["data"],
        "tecnico": tecnico_validated["data"]
    }
    
    # 6. Aplicar pesos e calcular resultado
    score_final = calcular_score_ponderado(dados_limpos)
    
    # 7. Retornar com relatório de validação
    return {
        **score_final,
        "data_quality": {
            "status": "VALIDATED" if validation_summary["total_errors"] == 0 else "SANITIZED",
            "validation_summary": validation_summary
        }
    }