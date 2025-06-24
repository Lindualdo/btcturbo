
#Busca os dados para teste de setups
#implementar buscar os daos no trandingView helper
def obter_dados_tecnicos():

    rsi_4h = 0
    ema_144_distance = 0
    ema_144_price = 0

    dados_tecnicos = {
        "rsi": rsi_4h,
        "preco_ema144": ema_144_price,
        "ema_144_distance": ema_144_distance
    }
    
    return dados_tecnicos