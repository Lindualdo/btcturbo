## Matriz de Setups (Timeframe 4H)

### Setups de COMPRA
| Setup                   | Condições 4H            | Confirmação       | Ação | Tamanho |
|-------                  |--------------           |-------------      |------|---------|
| **Pullback Tendência**  | RSI < 45 + EMA144 ±3%   | Volume médio+     | COMPRAR | 30% |
| **Teste Suporte**       | Toca EMA144 + Bounce    | Martelo/Doji      | COMPRAR | 25% |
| **Rompimento**          | Fecha acima resistência | Volume alto       | COMPRAR | 20% |
| **Oversold Extremo**    | RSI < 30 | Divergência+ |                   | COMPRAR | 40% |


## Arquitetura de arquivos e suas funções
´´´
dashboards/dash_main/analise_tatica/
├── setups/                                 # 📁 Detectores específicos
│   ├── pullback_tendencia.py               # ✅ Implementado
│   ├── oversold_extremo.py                 # 🔄 Mock
│   ├── teste_suporte.py                    # 🔄 Mock
│   └── rompimento_resistencia.py           # 🔄 Mock
├── analise_tatica_service.py               # 🎯 Controlador principal
├── setup_detector_utils.py                 # 🔄 Orquestrador
├── gate_system_utils.py                    # 🚪 Validações (mock)
├── comprar_helper.py                       # 💰 Formatador decisões
├── vender_helper.py                        # 💸 Mock
└── stop_helper.py                          # 🛡️ Mock
´´´