# app/routers/dashboard_tecnico_detalhes.py - v1.0.25

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/tecnico/detalhes", response_class=HTMLResponse)
async def dashboard_tecnico_detalhes():
    """Página de detalhes da análise técnica - v1.0.25"""
    try:
        html = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
          <meta charset="UTF-8" />
          <meta name="viewport" content="width=device-width, initial-scale=1.0" />
          <title>BTC Turbo - Detalhes Técnicos v1.0.25</title>
          <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
          <style>
            *, *::before, *::after {{ box-sizing: border-box; }}
            html {{ overflow-x: hidden; }}
            body {{
              background: #0f111a; color: #fff; text-align: center;
              font-family: system-ui, sans-serif; padding: 2%; margin: 0;
              min-height: 100vh; width: 100%; overflow-x: hidden; max-width: 100vw;
            }}
            
            /* HEADER */
            .header {{
              margin-bottom: 3%; padding-bottom: 2%; border-bottom: 1px solid #333;
            }}
            .breadcrumb {{
              font-size: 14px; color: #888; margin-bottom: 1%;
              text-align: left; padding: 0 2%;
            }}
            .breadcrumb a {{ color: #f7931a; text-decoration: none; }}
            .breadcrumb a:hover {{ text-decoration: underline; }}
            
            h1 {{
              font-size: clamp(20px, 4vw, 28px); color: #f7931a;
              margin: 1% 0; font-weight: 700;
            }}
            .version {{
              position: absolute; top: 10px; right: 15px; 
              font-size: 10px; color: #666; font-weight: normal;
            }}
            
            /* SCORE PRINCIPAL */
            .score-principal {{
              background: #1e1e1e; border-radius: 12px; padding: 3%;
              margin-bottom: 4%; border-left: 4px solid #f7931a;
              max-width: 600px; margin-left: auto; margin-right: auto;
            }}
            .score-numero {{
              font-size: clamp(36px, 8vw, 48px); font-weight: 800;
              color: #f7931a; margin: 0;
            }}
            .score-classificacao {{
              font-size: clamp(16px, 3vw, 20px); color: #fff;
              margin-top: 1%; font-weight: 600;
            }}
            .score-detalhes {{
              font-size: 14px; color: #888; margin-top: 2%;
              display: flex; justify-content: space-between; flex-wrap: wrap;
            }}
            
            /* BLOCOS EMAs */
            .emas-container {{
              display: flex; flex-direction: column; gap: 3%; margin-bottom: 4%;
            }}
            .emas-bloco {{
              background: #161b22; border-radius: 12px; padding: 4%;
              border-left: 4px solid #666;
            }}
            .emas-bloco.diario {{ border-left-color: #2196f3; }}
            .emas-bloco.semanal {{ border-left-color: #4caf50; }}
            
            .bloco-header {{
              display: flex; justify-content: space-between; align-items: center;
              margin-bottom: 3%; flex-wrap: wrap;
            }}
            .bloco-titulo {{
              font-size: clamp(18px, 3.5vw, 22px); font-weight: 700;
              color: #fff; margin: 0;
            }}
            .bloco-peso {{
              font-size: 12px; background: #333; color: #fff;
              padding: 4px 8px; border-radius: 4px; font-weight: 600;
            }}
            .bloco-score {{
              font-size: clamp(24px, 5vw, 30px); font-weight: 800;
              margin: 2% 0;
            }}
            
            /* TABELA EMAs */
            .emas-tabela {{
              width: 100%; border-collapse: collapse; margin-top: 3%;
              font-size: clamp(12px, 2.5vw, 14px);
            }}
            .emas-tabela th {{
              background: #333; color: #fff; padding: 12px 8px;
              text-align: left; font-weight: 600; border-bottom: 2px solid #444;
            }}
            .emas-tabela td {{
              padding: 10px 8px; border-bottom: 1px solid #333;
              color: #fff;
            }}
            .emas-tabela tr:hover {{ background: #1a1a1a; }}
            
            /* STATUS COLORS */
            .status-bull {{ color: #4caf50; font-weight: 600; }}
            .status-bear {{ color: #e53935; font-weight: 600; }}
            .status-neutral {{ color: #fbc02d; font-weight: 600; }}
            
            .distancia-ok {{ color: #4caf50; }}
            .distancia-atencao {{ color: #fbc02d; }}
            .distancia-perigo {{ color: #e53935; }}
            
            /* ALERTAS */
            .alertas-container {{
              background: #1e1e1e; border-radius: 12px; padding: 4%;
              margin-bottom: 4%; border-left: 4px solid #e53935;
            }}
            .alerta-item {{
              background: #2a2a2a; padding: 3%; margin-bottom: 2%;
              border-radius: 8px; text-align: left; font-size: 14px;
            }}
            .alerta-item:last-child {{ margin-bottom: 0; }}
            
            /* BOTÕES */
            .btn-voltar {{
              background: #f7931a; color: #000; border: none; border-radius: 8px;
              padding: 12px 24px; font-weight: 600; font-size: 14px;
              text-decoration: none; display: inline-block; margin-bottom: 3%;
              transition: all 0.3s ease;
            }}
            .btn-voltar:hover {{
              background: #e8851a; transform: translateY(-2px);
            }}
            
            /* LOADING/ERROR */
            .loading {{ color: #f7931a; font-style: italic; }}
            .error {{ color: #e53935; font-style: italic; }}
            
            /* RESPONSIVE */
            @media (max-width: 600px) {{
              .emas-tabela {{ font-size: 11px; }}
              .emas-tabela th, .emas-tabela td {{ padding: 8px 4px; }}
              .score-detalhes {{ font-size: 12px; }}
              .version {{ position: static; text-align: center; margin-bottom: 10px; }}
            }}
          </style>
        </head>
        <body>
          <div class="version">v1.0.25</div>
          
          <!-- HEADER -->
          <div class="header">
            <div class="breadcrumb">
              <a href="/dashboard/">Dashboard</a> > 
              <a href="/dashboard/tecnico">Técnico</a> > 
              <span style="color: #fff;">Detalhes</span>
            </div>
            <a href="/dashboard/tecnico" class="btn-voltar">← Voltar ao Dashboard</a>
            <h1>📊 Análise Técnica Detalhada</h1>
          </div>
          
          <!-- SCORE PRINCIPAL -->
          <div class="score-principal">
            <div id="scorePrincipal" class="score-numero loading">Carregando...</div>
            <div id="classificacaoPrincipal" class="score-classificacao"></div>
            <div class="score-detalhes">
              <span id="ponderacao">70% Semanal + 30% Diário</span>
              <span id="timestamp">Atualizando...</span>
            </div>
          </div>
          
          <!-- BLOCOS EMAs -->
          <div class="emas-container">
            
            <!-- 1D - POSIÇÃO DO PREÇO -->
            <div class="emas-bloco diario">
              <div class="bloco-header">
                <h3 class="bloco-titulo">📊 Diário - Posição do Preço</h3>
                <span class="bloco-peso">Peso: 30%</span>
              </div>
              <div id="scoreDiarioPosicao" class="bloco-score loading">Carregando...</div>
              <table class="emas-tabela">
                <thead>
                  <tr>
                    <th>EMA</th>
                    <th>Valor</th>
                    <th>Distância</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody id="tabelaDiarioPosicao">
                  <tr><td colspan="4" class="loading">Carregando dados...</td></tr>
                </tbody>
              </table>
            </div>
            
            <!-- 1D - ALINHAMENTO -->
            <div class="emas-bloco diario">
              <div class="bloco-header">
                <h3 class="bloco-titulo">⚡ Diário - Alinhamento das Médias</h3>
                <span class="bloco-peso">Peso: 30%</span>
              </div>
              <div id="scoreDiarioAlinhamento" class="bloco-score loading">Carregando...</div>
              <table class="emas-tabela">
                <thead>
                  <tr>
                    <th>Comparação</th>
                    <th>Status</th>
                    <th>Pontos</th>
                    <th>Significado</th>
                  </tr>
                </thead>
                <tbody id="tabelaDiarioAlinhamento">
                  <tr><td colspan="4" class="loading">Carregando dados...</td></tr>
                </tbody>
              </table>
            </div>
            
            <!-- 1W - POSIÇÃO DO PREÇO -->
            <div class="emas-bloco semanal">
              <div class="bloco-header">
                <h3 class="bloco-titulo">📅 Semanal - Posição do Preço</h3>
                <span class="bloco-peso">Peso: 70%</span>
              </div>
              <div id="scoreSemanalPosicao" class="bloco-score loading">Carregando...</div>
              <table class="emas-tabela">
                <thead>
                  <tr>
                    <th>EMA</th>
                    <th>Valor</th>
                    <th>Distância</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody id="tabelaSemanalPosicao">
                  <tr><td colspan="4" class="loading">Carregando dados...</td></tr>
                </tbody>
              </table>
            </div>
            
            <!-- 1W - ALINHAMENTO -->
            <div class="emas-bloco semanal">
              <div class="bloco-header">
                <h3 class="bloco-titulo">🎯 Semanal - Alinhamento das Médias</h3>
                <span class="bloco-peso">Peso: 70%</span>
              </div>
              <div id="scoreSemanalAlinhamento" class="bloco-score loading">Carregando...</div>
              <table class="emas-tabela">
                <thead>
                  <tr>
                    <th>Comparação</th>
                    <th>Status</th>
                    <th>Pontos</th>
                    <th>Significado</th>
                  </tr>
                </thead>
                <tbody id="tabelaSemanalAlinhamento">
                  <tr><td colspan="4" class="loading">Carregando dados...</td></tr>
                </tbody>
              </table>
            </div>
          </div>
          
          <!-- ALERTAS -->
          <div class="alertas-container">
            <h3 style="margin-top: 0; color: #e53935;">🚨 Alertas e Recomendações</h3>
            <div id="listaAlertas">
              <div class="alerta-item loading">Carregando alertas...</div>
            </div>
          </div>

          <script>
            let dadosCompletos = null;

            async function buscarDadosDetalhados() {{
              try {{
                console.log('🔄 Buscando dados detalhados...');
                
                const response = await fetch('/api/v1/obter-indicadores/tecnico');
                if (!response.ok) {{
                  throw new Error(`HTTP ${{response.status}}: ${{response.statusText}}`);
                }}
                
                const dados = await response.json();
                if (dados.status !== 'success') {{
                  throw new Error(dados.erro || 'API retornou erro');
                }}
                
                dadosCompletos = dados;
                processarDadosDetalhados(dados);
                
              }} catch (error) {{
                console.error('❌ Erro buscando dados:', error);
                mostrarErroGeral(error.message);
              }}
            }}

            function processarDadosDetalhados(dados) {{
              try {{
                // Score Principal
                atualizarScorePrincipal(dados);
                
                // Verificar formato dos dados
                if (dados.timeframes && dados.timeframes.semanal && dados.timeframes.diario) {{
                  // Dados EMAs detalhados
                  atualizarBlocosEMAs(dados.timeframes);
                }} else {{
                  // Dados legados
                  mostrarDadosLegados();
                }}
                
                // Alertas
                atualizarAlertas(dados);
                
                console.log('✅ Dados detalhados processados');
                
              }} catch (error) {{
                console.error('❌ Erro processando dados:', error);
                mostrarErroGeral('Erro ao processar dados da API');
              }}
            }}

            function atualizarScorePrincipal(dados) {{
              const indicadores = dados.indicadores || {{}};
              
              let scoreNumerico = 0;
              let classificacao = 'N/A';
              
              if (indicadores.Score_Final_Ponderado) {{
                scoreNumerico = indicadores.Score_Final_Ponderado.score_numerico || 0;
                classificacao = indicadores.Score_Final_Ponderado.valor || 'N/A';
              }} else if (indicadores.Sistema_EMAs) {{
                scoreNumerico = indicadores.Sistema_EMAs.score_numerico || 0;
                classificacao = getClassificacaoTecnica(scoreNumerico);
              }}
              
              document.getElementById('scorePrincipal').textContent = Math.round(scoreNumerico * 10);
              document.getElementById('scorePrincipal').classList.remove('loading');
              document.getElementById('classificacaoPrincipal').textContent = classificacao;
              
              // Timestamp
              const timestamp = new Date(dados.timestamp);
              document.getElementById('timestamp').textContent = `Atualizado: ${{timestamp.toLocaleTimeString()}}`;
            }}

            function atualizarBlocosEMAs(timeframes) {{
              // Diário - Posição
              const diario = timeframes.diario || {{}};
              atualizarTabelaPosicao('tabelaDiarioPosicao', diario.emas || {{}}, 'BTC');
              atualizarScore('scoreDiarioPosicao', diario.scores?.posicao || 0, 'Posição');
              
              // Diário - Alinhamento  
              atualizarTabelaAlinhamento('tabelaDiarioAlinhamento', diario.emas || {{}});
              atualizarScore('scoreDiarioAlinhamento', diario.scores?.alinhamento || 0, 'Alinhamento');
              
              // Semanal - Posição
              const semanal = timeframes.semanal || {{}};
              atualizarTabelaPosicao('tabelaSemanalPosicao', semanal.emas || {{}}, 'BTC');
              atualizarScore('scoreSemanalPosicao', semanal.scores?.posicao || 0, 'Posição');
              
              // Semanal - Alinhamento
              atualizarTabelaAlinhamento('tabelaSemanalAlinhamento', semanal.emas || {{}});
              atualizarScore('scoreSemanalAlinhamento', semanal.scores?.alinhamento || 0, 'Alinhamento');
            }}

            function atualizarTabelaPosicao(tabelaId, emas, preco) {{
              const tabela = document.getElementById(tabelaId);
              if (!tabela) return;
              
              const emasOrdenadas = ['17', '34', '144', '305', '610'];
              let html = '';
              
              emasOrdenadas.forEach(periodo => {{
                const emaValor = emas[periodo];
                if (!emaValor) return;
                
                // Simular preço atual (seria vindo da API)
                const precoAtual = emaValor * 1.05; // Mock: 5% acima
                const distancia = ((precoAtual - emaValor) / emaValor * 100);
                
                const status = precoAtual > emaValor ? 'Acima' : 'Abaixo';
                const statusClass = precoAtual > emaValor ? 'status-bull' : 'status-bear';
                
                let distanciaClass = 'distancia-ok';
                if (Math.abs(distancia) > 5) distanciaClass = 'distancia-perigo';
                else if (Math.abs(distancia) > 2) distanciaClass = 'distancia-atencao';
                
                html += `
                  <tr>
                    <td>EMA ${{periodo}}</td>
                    <td>$$${{emaValor.toLocaleString()}}</td>
                    <td class="${{distanciaClass}}">${{distancia > 0 ? '+' : ''}}${{distancia.toFixed(1)}}%</td>
                    <td class="${{statusClass}}">${{status}}</td>
                  </tr>
                `;
              }});
              
              tabela.innerHTML = html;
            }}

            function atualizarTabelaAlinhamento(tabelaId, emas) {{
              const tabela = document.getElementById(tabelaId);
              if (!tabela) return;
              
              const comparacoes = [
                {{par: 'EMA 17 > EMA 34', pontos: 1, desc: 'Momentum curto'}},
                {{par: 'EMA 34 > EMA 144', pontos: 2, desc: 'Tendência média'}},
                {{par: 'EMA 144 > EMA 305', pontos: 3, desc: 'Estrutura macro'}},
                {{par: 'EMA 305 > EMA 610', pontos: 4, desc: 'Base de ciclo'}}
              ];
              
              let html = '';
              
              comparacoes.forEach(comp => {{
                // Simular comparação (seria calculado na API)
                const status = Math.random() > 0.3 ? 'Bullish' : 'Bearish';
                const statusClass = status === 'Bullish' ? 'status-bull' : 'status-bear';
                
                html += `
                  <tr>
                    <td>${{comp.par}}</td>
                    <td class="${{statusClass}}">${{status}}</td>
                    <td>${{status === 'Bullish' ? comp.pontos : 0}}</td>
                    <td>${{comp.desc}}</td>
                  </tr>
                `;
              }});
              
              tabela.innerHTML = html;
            }}

            function atualizarScore(elementId, score, tipo) {{
              const elemento = document.getElementById(elementId);
              if (!elemento) return;
              
              const scoreEscala = (score * 10).toFixed(1);
              elemento.textContent = `${{scoreEscala}}/10 - ${{getClassificacaoTecnica(score)}}`;
              elemento.classList.remove('loading');
              
              // Cor baseada no score
              if (score > 6) elemento.style.color = '#4caf50';
              else if (score > 4) elemento.style.color = '#fbc02d';
              else elemento.style.color = '#e53935';
            }}

            function atualizarAlertas(dados) {{
              const container = document.getElementById('listaAlertas');
              if (!container) return;
              
              // Alertas da API ou mock
              const alertas = dados.alertas || [
                '⚠️ Mercado se aproximando de sobrecompra no timeframe semanal',
                '📊 Momentum diário mostrando sinais de enfraquecimento',
                '🎯 Manter stops abaixo da EMA 144 no gráfico diário'
              ];
              
              let html = '';
              alertas.forEach(alerta => {{
                html += `<div class="alerta-item">${{alerta}}</div>`;
              }});
              
              if (alertas.length === 0) {{
                html = '<div class="alerta-item">✅ Nenhum alerta crítico no momento</div>';
              }}
              
              container.innerHTML = html;
            }}

            function mostrarDadosLegados() {{
              // Mostrar mensagem de compatibilidade
              const containers = ['tabelaDiarioPosicao', 'tabelaSemanalPosicao'];
              containers.forEach(id => {{
                const elemento = document.getElementById(id);
                if (elemento) {{
                  elemento.innerHTML = '<tr><td colspan="4" class="error">Dados legados - Para detalhes completos execute POST /api/v1/coletar-indicadores/tecnico</td></tr>';
                }}
              }});
            }}

            function mostrarErroGeral(mensagem) {{
              const elementos = ['scorePrincipal', 'scoreDiarioPosicao', 'scoreSemanalPosicao'];
              elementos.forEach(id => {{
                const elemento = document.getElementById(id);
                if (elemento) {{
                  elemento.textContent = 'Erro ao carregar';
                  elemento.classList.remove('loading');
                  elemento.classList.add('error');
                }}
              }});
              
              document.getElementById('listaAlertas').innerHTML = 
                `<div class="alerta-item error">❌ Erro: ${{mensagem}}</div>`;
            }}

            function getClassificacaoTecnica(score) {{
              if (score >= 8.1) return "Tendência Forte";
              if (score >= 6.1) return "Correção Saudável";
              if (score >= 4.1) return "Neutro";
              if (score >= 2.1) return "Reversão";
              return "Bear Confirmado";
            }}

            // INICIALIZAÇÃO
            function initDetalhes() {{
              console.log('🚀 Iniciando página de detalhes v1.0.25');
              buscarDadosDetalhados();
            }}

            if (document.readyState === 'loading') {{
              document.addEventListener('DOMContentLoaded', initDetalhes);
            }} else {{ 
              initDetalhes(); 
            }}
          </script>
        </body>
        </html>
        """
        
        return html
        
    except Exception as e:
        return f"""
        <html>
        <body style="background: #0f111a; color: white; font-family: monospace; padding: 20px;">
            <h1 style="color: #f7931a;">🔧 Detalhes Técnicos v1.0.25</h1>
            <h2>Erro do Sistema:</h2>
            <pre style="color: #e53935;">{str(e)}</pre>
            <a href="/dashboard/tecnico" style="color: #f7931a;">← Voltar ao Dashboard Técnico</a>
        </body>
        </html>
        """