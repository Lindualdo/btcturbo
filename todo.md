FASE1 - Operacional

1 - Revisar funções de setup (Decisões por Ciclo + Setup + Gate System)
- confirmar Hierarquia de Decisão (Timeframe Conflito)
- Testar (Gate System) - REVISADO
2 - rever a quantidde de barras das funções trandview e integridade / confiabilidade
3 - decompor o helper trandiview em arquivos menores cada um para uma finalidade
4 - implementar controle de operações e silenciar os alertas / setups
5 - Registro de operações
6 - Rever Setups de VENDA (quando ciclo sugere)
7 - criar gestão de stops
8 - Trader Jornal
8 - criar dash com métricas de performance

FASE1 - REFACTORE
1 -  *** organizar e limpar o código excluindo apis e funções descontinuadas ***
- Analise Mercado v3 está usando utils do dash-main (avaliar deixar idenpendente)
- Automação das cargas do dash ainda está usando a V2 para carga da analise mercado
- dash já está usando os 2 APIs GETs V3 (dash-main e analise-mercado)

FASE2 - ALERTAS
- Rever os Alertas (criticos, táticos, de oportunidade...)

FASE3 - ANALISE APROFUNDADA
- criar detalhe da analise tecnica (EMAs) no dash detalhe mercado
- Analisar BBW nas metricas e ponderação geral da analise tecnica

FASE4 - BACKTEST
- fazer rotinas de backtest


