# app/services/v3/dash_main/__init__.py

"""
Dashboard Main V3 - Execução Tática Implementada

Estrutura Camada 4:
├── execucao_tatica_service.py     # Serviço principal
├── utils/
│   ├── gate_system_utils.py       # 4 validações + overrides
│   ├── setup_detector_utils.py    # Matriz setups 4H
│   └── tecnicos_utils.py          # RSI + EMA144 4H
└── helpers/
    ├── comprar_helper.py          # Estratégia compra ✅
    ├── vender_helper.py           # Estratégia venda 🔄 mock
    └── stop_helper.py             # Stop loss 🔄 mock

Fluxo Camada 4:
1. Gate System (4 validações + overrides especiais)
2. Dados Técnicos 4H (RSI, EMA144, distância)  
3. Identificação Setup (PULLBACK, TESTE_SUPORTE, ROMPIMENTO, OVERSOLD)
4. Decisão Estratégica (COMPRAR, AJUSTAR_ALAVANCAGEM, BLOQUEADO, AGUARDAR)

Status:
- ✅ Gate System implementado
- ✅ Setup Detection implementado  
- ✅ Estratégia Compra implementada
- 🔄 Estratégia Venda mockada (futura)
- 🔄 Stop Loss mockado (futura)
"""

#from .execucao_tatica_service import executar_execucao_tatica
#from .utils.gate_system_utils import aplicar_gate_system
#from .utils.setup_detector_utils import identificar_setup_4h
#from .utils.tecnicos_utils import obter_dados_tecnicos_4h
#from .utils.helpers.comprar_helper import processar_estrategia_compra
#from .utils.helpers.vender_helper import processar_estrategia_venda
#from .utils.helpers.stop_helper import processar_estrategia_stop