#/app/services/alertas.py

from datetime import datetime

def get_alertas():
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "alertas_ativos": [
            {
                "tipo": "Risco",
                "mensagem": "PERIGO: Liquidação próxima (Health Factor < 1.15)",
                "prioridade": "Crítica"
            },
            {
                "tipo": "Mercado",
                "mensagem": "EUFORIA: Funding Rate acima de 0.1%, considerar redução",
                "prioridade": "Alta"
            },
            {
                "tipo": "Técnico",
                "mensagem": "Mudança de tendência principal detectada (preço cruzou EMA200)",
                "prioridade": "Alta"
            },
            {
                "tipo": "Volatilidade",
                "mensagem": "Volatilidade extremamente elevada",
                "prioridade": "Média"
            }
        ]
    }
