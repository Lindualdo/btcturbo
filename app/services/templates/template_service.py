# app/services/template_service.py

import os
import json
from pathlib import Path
from typing import Dict, Any

class TemplateService:
    """Serviço para gerenciar templates HTML dos dashboards"""
    
    def __init__(self):
        self.templates_dir = Path(__file__).parent.parent / "templates"
        
    def load_template(self, template_name: str) -> str:
        """Carrega template HTML do arquivo"""
        template_path = self.templates_dir / f"{template_name}.html"
        
        if not template_path.exists():
            raise FileNotFoundError(f"Template {template_name} não encontrado")
            
        with open(template_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    def render_dashboard(self, template_name: str, data: Dict[str, Any]) -> str:
        """Renderiza dashboard com dados específicos"""
        template = self.load_template(f"dashboards/{template_name}")
        
        # Substituições específicas para o bloco riscos
        if template_name == "riscos":
            return self._render_riscos(template, data)
        
        # Para outros templates, usar lógica genérica
        html = template.replace("{{DATA_JSON}}", json.dumps(data, ensure_ascii=False))
        
        # Substituições específicas para compatibilidade N8N
        for key, value in self._flatten_data(data).items():
            placeholder = f"{{{{ {key} }}}}"
            html = html.replace(placeholder, str(value))
            
        return html
    
    def _render_riscos(self, template: str, data: Dict[str, Any]) -> str:
        """Renderiza template específico do bloco riscos"""
        # Dados consolidados
        score_consolidado = int(data.get("score_consolidado", 0) * 10)
        classificacao_consolidada = data.get("classificacao_consolidada", "N/A")
        
        # Dados dos indicadores
        indicadores = data.get("indicadores", {})
        dist_data = indicadores.get("Dist_Liquidacao", {})
        health_data = indicadores.get("Health_Factor", {})
        
        # Substituições
        replacements = {
            "##SCORE_CONSOLIDADO##": str(score_consolidado),
            "##CLASSIFICACAO_CONSOLIDADA##": classificacao_consolidada,
            "##JS_SCORE_CONSOLIDADO##": str(score_consolidado),
            
            "##SCORE_DIST##": str(int(dist_data.get("score", 0) * 10)),
            "##CLASSIFICACAO_DIST##": dist_data.get("classificacao", "N/A"),
            "##JS_SCORE_DIST##": str(int(dist_data.get("score", 0) * 10)),
            "##VALOR_DIST##": str(dist_data.get("valor", "N/A")),
            "##PESO_DIST##": str(dist_data.get("peso", "N/A")),
            "##FONTE_DIST##": str(dist_data.get("fonte", "N/A")),
            
            "##SCORE_HEALTH##": str(int(health_data.get("score", 0) * 10)),
            "##CLASSIFICACAO_HEALTH##": health_data.get("classificacao", "N/A"),
            "##JS_SCORE_HEALTH##": str(int(health_data.get("score", 0) * 10)),
            "##VALOR_HEALTH##": str(health_data.get("valor", "N/A")),
            "##PESO_HEALTH##": str(health_data.get("peso", "N/A")),
            "##FONTE_HEALTH##": str(health_data.get("fonte", "N/A"))
        }
        
        # Aplicar todas as substituições
        html = template
        for placeholder, value in replacements.items():
            html = html.replace(placeholder, value)
            
        return html
    
    def _flatten_data(self, data: Dict[str, Any], prefix: str = "$json") -> Dict[str, Any]:
        """Converte estrutura aninhada para placeholders N8N"""
        flattened = {}
        
        for key, value in data.items():
            new_key = f"{prefix}.{key}" if prefix != "$json" else f"$json.{key}"
            
            if isinstance(value, dict):
                flattened.update(self._flatten_data(value, new_key))
            elif isinstance(value, list):
                flattened[new_key] = json.dumps(value)
            else:
                flattened[new_key] = value
                
        return flattened

# Instância global
template_service = TemplateService()