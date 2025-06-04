# 🚨 SISTEMA DE ALERTAS CRÍTICOS (Sem Score)

´´´
ALERTAS SISTÊMICOS - AÇÃO IMEDIATA
├── WBTC DEPEG
│   ├── Trigger: Desconto > 0.5%
│   ├── Check: A cada hora
│   └── Ação: SAIR IMEDIATAMENTE
│
├── ARBITRUM DOWN
│   ├── Trigger: Rede congestionada/parada
│   ├── Check: Status page
│   └── Ação: MIGRAR PARA MAINNET
│
└── AAVE EXPLOIT
    ├── Trigger: TVL cai > 20% em 1h
    ├── Check: DefiLlama alerts
    └── Ação: RETIRAR TUDO

´´´

💻 IMPLEMENTAÇÃO DOS ALERTAS

´´´
# Checagem horária simples
def check_riscos_sistemicos():
    # WBTC Depeg Check
    btc_price = get_btc_price()
    wbtc_price = get_wbtc_price()
    depeg = (btc_price - wbtc_price) / btc_price
    
    if depeg > 0.005:  # 0.5%
        send_alert("🚨 WBTC DEPEG DETECTADO! Ação imediata!")
        return "EMERGENCIA"
    
    # Arbitrum Check
    if not arbitrum_is_healthy():
        send_alert("🚨 PROBLEMA NA ARBITRUM! Verificar posição!")
        return "EMERGENCIA"
    
    # AAVE Check  
    if aave_tvl_drop > 20:
        send_alert("🚨 POSSÍVEL PROBLEMA AAVE! Investigar!")
        return "EMERGENCIA"
    
    return "TUDO_OK"

´´´

## 📱 FONTES PARA MONITORAMENTO

´´´

WBTC PEG
├── CoinGecko: WBTC/BTC pair
├── Dexscreener: WBTC/WETH pools
└── API: (wbtc_price / btc_price) - 1

ARBITRUM STATUS
├── https://status.arbitrum.io/
├── https://arbiscan.io/
└── Gas price spikes

AAVE HEALTH
├── https://app.aave.com/governance
├── Twitter: @AaveAave
└── DefiLlama TVL alerts

´´´

## 🔔 CONFIGURAÇÃO RECOMENDADA

´´´

ALERTAS PRIORITÁRIOS
├── Telegram Bot para notificações
├── Check automático a cada hora
├── Som diferente para sistêmicos
└── Plano de ação pré-definido

´´´

EXEMPLO MENSAGEM:
"🚨 ALERTA SISTÊMICO 🚨
WBTC trading 0.7% abaixo do BTC
Ação: Verificar posição IMEDIATAMENTE
Link: [dashboard AAVE]"


