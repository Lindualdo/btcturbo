FASE1 - REFACTORE - feito
1 -  *** organizar e limpar o código excluindo apis e funções descontinuadas *** - feito
- Analise Mercado v3 está usando utils do dash-main (avaliar deixar idenpendente) - feito
- Automação das cargas do dash ainda está usando a V2 para carga da analise mercado -feito
- dash já está usando os 2 APIs GETs V3 (dash-main e analise-mercado) -feito
- coleta de indicadores (tecnico e riscos) no N8N estão usando versão antiga do btcturbo e não v5 -feito
- retirar a v3 do dash e organizar melhor dentro do services - feito
- retirar o v5 do btcturbo deixando apenas btcturbo - alterar em todos os lugares necessários - feito
- iremos iniciar as próximas tags como v 1.5.0 - feito
- https://colintalkscrypto.com/cbbi/ (referencia inspiração para score do ciclo)
- analisar EMA 200 semanal X topo anterior

FASE1 - Operacional

0 - criar  documentação tecnica resumida - todo o projeto - pastas e arquivos + obj - feito
1 - Revisar funções de setup - feito
2 - rever a quantidde de barras das funções trandview e integridade / confiabilidade - feito
4 - implementar controle de operações e silenciar os alertas / setups
5 - Registro de operações
6 - Rever Setups de VENDA (quando ciclo sugere)
7 - criar gestão de stops
8 - Trader Jornal
8 - criar dash com métricas de performance
9 - implementar regras adicionais de proteção alavancagem
10 - implemenra gate system de forma simplificada
11 - confirmar Hierarquia de Decisão (Timeframe Conflito)
12 - BTC Core está hard coded na API financeira patrimonio


FASE2 - ALERTAS
- desenv. de forma mais simples - simplificar tudo

FASE3 - ANALISE TECNICA
-  *** analisar obter e calcluar score da analise tecnico está uma confusão impossível evoluir ou manter**
- criar detalhe da analise tecnica (EMAs) no dash detalhe mercado
- Analisar BBW nas metricas e ponderação geral da analise tecnica

FASE4 - BACKTEST
- fazer rotinas de backtest
- decompor o helper trandiview em arquivos menores cada um para uma finalidade


---

## todo: 
- incluir indicador de price action no score tecnico
- rever nivel de alavancagem - proximo a topos (validar nos cenários da camada 1)
- avaliar peso do RSI semanal no bloco momentum (Reduzir para 30% e adicionar ATR avaliar migrar para blco técnico)
- avaliar utilização de EMAs mais flexíveis para ajustes de alavancagem (já previsto na v1.8)
- incluir gatilhos de volume onchain (Incorporar Whale Transaction ao bloco Momentum, peso de 10-15%)
- incluir outros indicadores de risco sistemicos (BVOL, juros mercado, WBTC paridade, plataforma AAVE)
- rever ranges do MVRV e NUPL - ajustar para realidade atual do mercado (menor volatilidade)
- rever dependência da AAVE,  WBTC e Arbitrum