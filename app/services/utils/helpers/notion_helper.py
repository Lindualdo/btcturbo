from datetime import datetime
from notion_client import Client
from typing import Dict
from app.config import get_settings
import logging

def get_ciclo_data_from_notion() -> Dict:
    settings = get_settings()
    notion = Client(auth=settings.NOTION_TOKEN)
    database_id = settings.NOTION_DATABASE_ID.strip().replace('"', '')

    response = notion.databases.query(database_id=database_id)

    dados_ciclo = {
        "mvrv_z_score": None,
        "realized_ratio": None,
        "puell_multiple": None,
        "fonte": "Notion",
        "timestamp": datetime.utcnow().isoformat()
    }

    indicador_map = {
        "mvrv_z-score": "mvrv_z_score",
        "realized_price": "realized_ratio",
        "puell_multiple": "puell_multiple"
    }

    for row in response["results"]:
        props = row["properties"]
        indicador = props["Indicador"]["title"]
        valor = props.get("valor_coleta", {}).get("number")

        if indicador and valor is not None:
            nome = indicador[0]["plain_text"].strip().lower()
            if nome in indicador_map:
                dados_ciclo[indicador_map[nome]] = float(valor)
                logging.info(f"{nome} coletado: {valor}")

    return dados_ciclo
