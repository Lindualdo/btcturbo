# app/services/utils/postgres_helper.py

import logging
from datetime import datetime
from typing import Dict, Optional

def save_dados_ciclo(dados: Dict):
    """
    Mock da função para salvar dados do ciclo no PostgreSQL.
    Por enquanto só loga os dados recebidos.
    """
    logging.info(f"[MOCK] Salvando dados no PostgreSQL: {dados}")
    # TODO: Implementar conexão real com PostgreSQL
    return True

def get_dados_ciclo() -> Optional[Dict]:
    """
    Mock da função para buscar dados do ciclo no PostgreSQL.
    Por enquanto retorna None.
    """
    logging.info("[MOCK] Buscando dados do PostgreSQL")
    # TODO: Implementar consulta real ao PostgreSQL
    return None

def is_ciclo_outdated(hours: int = 8) -> bool:
    """
    Mock da função para verificar se dados estão desatualizados.
    Por enquanto sempre retorna True para forçar atualização.
    """
    logging.info(f"[MOCK] Verificando se dados estão desatualizados (>{hours}h)")
    # TODO: Implementar verificação real no PostgreSQL
    return True