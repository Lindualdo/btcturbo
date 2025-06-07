## Adicione novo bloco indicadores_timing na analise tatica:

```json
{
    "analise": "tatica_completa",
    "versao": "4_camadas_independentes",
    "timestamp": "...",
    "acao_recomendada": "...",
    "cenario_identificado": {...},
    "decisao_final": {...},
    "dados_camadas": {...},
    
    "indicadores_timing": {
        "bbw": {
            "valor": 7.2,
            "classificacao": "normal",
            "dias_comprimido": 0,
            "alerta_ativo": false,
            "threshold_alerta": 5.0
        },
        "mvrv": {
            "valor": 2.24,
            "z_score": 2.5,
            "fase": "bull_medio",
            "percentil_historico": 72
        },
        "funding_rate": {
            "atual": 0.042,
            "media_7d": 0.031,
            "classificacao": "neutro",
            "tendencia": "estavel"
        }
    },
    
    "analise_contextual": {...},
    "comparacao_decisoes": {...},
    "alertas": [...],
    "simulacao": {...},
    "status": "success"
}
```