#/utils/helpers/tradingview_helper.py

from tvDatafeed import TvDatafeed
import logging

class TradingViewSession:
    _instance = None

    @classmethod
    def get_session(cls):
        if cls._instance is None:
            try:
                logging.info("Criando nova sessão TradingView...")
                cls._instance = TvDatafeed(auto_login=True)
                logging.info("Sessão TradingView criada com sucesso.")
            except Exception as e:
                logging.error(f"Erro ao criar sessão TradingView: {str(e)}")
                raise e
        return cls._instance

def get_tv_datafeed():
    return TradingViewSession.get_session()
