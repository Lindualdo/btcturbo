# app/routers/dashboard_tecnico.py - CORRIGIDO v1.0.20

from fastapi import APIRouter
from fastapi.responses import HTMLResponse
import requests
import logging

router = APIRouter()

@router.get("/tecnico", response_class=HTMLResponse)
async def dashboard_tecnico():
    """Dashboard de análise técnica - API INTERNA v1.0.20"""
    try:
        html = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
          <meta charset="UTF-8" />
          <meta name="viewport" content="width=device-width, initial-scale=1.0" />
          <title>BTC Turbo - Análise Técnica v1.0.20</title>
          <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
          <style>
            *, *::before, *::after {{ box-sizing: border-box; }}
            html {{ overflow-x: hidden; }}
            body {{
              background: #0f111a; color: #fff; text-align: center;
              font-family: system-ui, sans-serif; padding: 2%; margin: 0;
              min-height: 100vh; width: 100%; overflow-x: hidden; max-width: 100vw;
            }}
            h1 {{
              font-size: clamp(20px, 4vw, 28px); color: #f7931a;
              margin-bottom: 3%; padding: 0 2%; font-weight: 700;
            }}
            .version {{
              position: absolute; top: 10px; right: 15px; 
              font-size: 10px; color: #666; font-weight: normal;
            }}
            .menu-scroll {{
              display: flex; justify-content: center; gap: clamp(8px, 1.5vw, 24px);
              margin-bottom: 4%; padding: 1.5%; border-bottom: 1px solid #333;
              overflow-x: auto; -ms-overflow-style: none; scrollbar-width: none;
            }}
            .menu-scroll a {{
              color: #888; font-weight: 600; text-decoration: none;
              padding: clamp(8px, 1.5vw, 12px) clamp(12px, 2vw, 20px);
              border-bottom: 3px solid transparent; transition: 0.3s;
              font-size: clamp(14px, 1.6vw, 16px); border-radius: 8px;
            }}
            .menu-scroll a:hover {{ color: #f7931a; border-bottom: 3px solid #f7931a; }}
            .menu-scroll a.ativo {{ color: #f7931a; border-bottom: 3px solid #f7931a; background-color: #1e1e1e; }}
            .status-api {{
              background: #1e1e1e; padding: 1rem; border-radius: 8px; margin-bottom: 2rem;
              max-width: 800px; margin-left: auto; margin-right: auto;
              border-left: 4px solid #f7931a; text-align: left;
            }}
            .dashboard-grid {{
              display: flex; flex-wrap: wrap; justify-content: center;
              gap: 2%; margin-bottom: 4%; width: 100%; max-width: 100%;
            }}
            .grafico {{
              width: clamp(200px, 30%, 280px); background: #161b22; border-radius: 4%;
              padding: 3% 2%; box-shadow: 0 0 10px rgba(0,0,0,0.6);
              display: flex; flex-direction: column; align-items: center; margin-bottom: 2%;
            }}
            .classificacao {{
              font-size: clamp(12px, 2.2vw, 16px); margin-top: 2%; font-weight: 600;
            }}
            .info-text {{ 
              font-size: 12px; color: #888; margin-top: 10px; text-align: center;
            }}
            .detalhes-btn {{
              background: #f7931a; color: #000; border: none; border-radius: 6px;
              padding: 8px 16px; margin-top: 12px; cursor: pointer; font-weight: 600;
              font-size: 12px; transition: all 0.3s ease; text-decoration: none;
              display: inline-block;
            }}
            .detalhes-btn:hover {{
              background: #e8851a; transform: translateY(-2px);
            }}
            .loading {{ color: #f7931a; font-style: italic; }}
            .error {{ color: #e53935; font-style: italic; }}
            canvas {{ max-width: 100%; height: auto; }}
            @media (max-width: 600px) {{
              .grafico {{ width: calc(100% - 2px); padding: 4% 3%; }}
              .dashboard-grid {{ flex-direction: column; align-items: center; gap: 0; }}
              .version {{ position: static; text-align: center; margin-bottom: 10px; }}
            }}
          </style>
        </head>
        <body>
          <div class="version">v1.0.20</div>
          <h1>📈 BTC Turbo - Análise Técnica</h1>
          
          <div class="menu-scroll">
            <a href="/dashboard/">Home</a>
            <a href="/dashboard/riscos">Riscos</a>
            <a href="/dashboard/momentum">Momentum</a>
            <a href="/dashboard/ciclos">Ciclos</a>
            <a href="/dashboard/tecnico" class="ativo">Técnica</a>
          </div>

          <!-- Alertas Relevantes (só mostra se houver) -->
          <div class="status-api" id="statusApi" style="display: none;">
            <!-- Alertas dinâmicos -->
          </div>
          
          <div class="dashboard-grid">
            <!-- Score Final Ponderado -->
            <div class="grafico">
              <h3>🎯 Score Final</h3>
              <canvas id="gauge_final" width="200" height="180"></canvas>
              <div id="class_final" class="classificacao loading">Carregando...</div>
              <div class="info-text">70% Semanal + 30% Diário</div>
              <a href="/dashboard/tecnico/detalhes" class="detalhes-btn">📊 Ver Detalhes</a>
            </div>
                    
            <!-- EMAs Semanal -->
            <div class="grafico">
              <h3>📅 Semanal (1W)</h3>
              <canvas id="gauge_semanal" width="200" height="180"></canvas>
              <div id="class_semanal" class="classificacao loading">Carregando...</div>
              <div class="info-text">Peso: 70% do total</div>
            </div>
                    
            <!-- EMAs Diário -->
            <div class="grafico">
              <h3>📊 Diário (1D)</h3>
              <canvas id="gauge_diario" width="200" height="180"></canvas>
              <div id="class_diario" class="classificacao loading">Carregando...</div>
              <div class="info-text">Peso: 30% do total</div>
            </div>
          </div>

          <script>
            let dadosAtuais = null;

            async function buscarDadosApiInterna() {{
              try {{
                atualizarStatus('🔄 Buscando dados da API interna...', 'GET /api/v1/obter-indicadores/tecnico');

                const response = await fetch('/api/v1/obter-indicadores/tecnico');
                
                if (!response.ok) {{
                  throw new Error(`HTTP ${{response.status}}: ${{response.statusText}}`);
                }}
                
                const dados = await response.json();
                
                if (dados.status !== 'success') {{
                  throw new Error(dados.erro || `API retornou status: ${{dados.status}}`);
                }}
                
                dadosAtuais = dados;
                processarDadosApiInterna(dados);
                
              }} catch (error) {{
                console.error('❌ Erro API interna:', error);
                mostrarErroApi(error.message);
              }}
            }}

            function processarDadosApiInterna(dados) {{
              try {{
                atualizarStatus('✅ API interna conectada', 
                  `Fonte: ${{dados.fonte_dados || 'PostgreSQL'}} | ${{new Date(dados.timestamp).toLocaleTimeString()}}`);

                const indicadores = dados.indicadores || {{}};

                // Verificar se temos dados EMAs detalhados (v1.0.19+)
                if (indicadores.Score_Final_Ponderado) {{
                  exibirEMAsDetalhadas(dados);
                }} else {{
                  exibirDadosLegados(dados);
                }}

              }} catch (error) {{
                console.error('❌ Erro processando dados:', error);
                mostrarErroApi('Erro ao processar dados da API interna');
              }}
            }}

            function exibirEMAsDetalhadas(dados) {{
              const indicadores = dados.indicadores;
              const timeframes = dados.timeframes || {{}};

              // Score Final Ponderado
              const scoreFinal = indicadores.Score_Final_Ponderado?.score_numerico || 0;
              const scoreFinalEscala = Math.round(scoreFinal * 10);
              
              atualizarGrafico('gauge_final', scoreFinalEscala, 'class_final', 
                              indicadores.Score_Final_Ponderado?.valor || 'N/A');

              // Timeframes específicos
              const semanal = timeframes.semanal || {{}};
              const diario = timeframes.diario || {{}};

              const scoreSemanal = Math.round((semanal.scores?.consolidado || 0) * 10);
              const scoreDiario = Math.round((diario.scores?.consolidado || 0) * 10);

              atualizarGrafico('gauge_semanal', scoreSemanal, 'class_semanal', 
                              getClassificacaoTecnica(scoreSemanal / 10));
              atualizarGrafico('gauge_diario', scoreDiario, 'class_diario', 
                              getClassificacaoTecnica(scoreDiario / 10));

              console.log('✅ Dados EMAs detalhados exibidos');
            }}

            function exibirDadosLegados(dados) {{
              const indicadores = dados.indicadores;
              
              // Mostrar gráfico legado
              document.getElementById('grafico_legado').style.display = 'flex';
              
              const scoreEmas = indicadores.Sistema_EMAs?.score_numerico || 0;
              const scoreEmasEscala = Math.round(scoreEmas * 10);
              
              atualizarGrafico('gauge_legado', scoreEmasEscala, 'class_legado', 
                              indicadores.Sistema_EMAs?.valor || 'N/A');

              // Usar mesmo score para final (compatibilidade)
              atualizarGrafico('gauge_final', scoreEmasEscala, 'class_final', 
                              getClassificacaoTecnica(scoreEmas));

              atualizarStatus('⚠️ Usando dados legados', 
                'Para dados completos: POST /api/v1/coletar-indicadores/tecnico');

              console.log('📄 Dados legados exibidos');
            }}

            function getClassificacaoTecnica(score) {{
              if (score >= 8.1) return "Tendência Forte";
              if (score >= 6.1) return "Correção Saudável";
              if (score >= 4.1) return "Neutro";
              if (score >= 2.1) return "Reversão";
              return "Bear Confirmado";
            }}

            function atualizarGrafico(canvasId, score, classId, classificacao) {{
              const element = document.getElementById(classId);
              if (element) {{
                element.textContent = `Score: ${{score}} - ${{classificacao}}`;
                element.classList.remove('loading', 'error');
              }}
              
              renderGauge(canvasId, score);
            }}

            function atualizarStatus(titulo, detalhes) {{
              document.getElementById('statusApi').innerHTML = `
                <strong>${{titulo}}</strong>
                <div style="font-size: 12px; margin-top: 4px; color: #888;">
                  ${{detalhes}}
                </div>
              `;
            }}

            function mostrarErroApi(mensagem) {{
              atualizarStatus('❌ Erro na API interna', mensagem);
              
              ['class_final', 'class_semanal', 'class_diario', 'class_legado'].forEach(id => {{
                const element = document.getElementById(id);
                if (element) {{
                  element.textContent = 'Erro ao carregar';
                  element.classList.remove('loading');
                  element.classList.add('error');
                }}
              }});
            }}

            function renderGauge(canvasId, score) {{
              const canvas = document.getElementById(canvasId);
              if (!canvas) return;
              
              const ctx = canvas.getContext('2d');
              const existingChart = Chart.getChart(canvas);
              if (existingChart) existingChart.destroy();

              try {{
                new Chart(ctx, {{
                  type: 'doughnut',
                  data: {{ datasets: [{{ data: [100], backgroundColor: ['#0000'], borderWidth: 0, cutout: '80%' }}] }},
                  options: {{
                    responsive: false, rotation: -Math.PI, circumference: Math.PI,
                    plugins: {{ tooltip: {{ enabled: false }}, legend: {{ display: false }} }}
                  }},
                  plugins: [{{
                    afterDraw: (chart) => {{
                      const ctx = chart.ctx;
                      const angle = (score / 100) * Math.PI;
                      const cx = chart.width / 2;
                      const cy = chart.height - 42;
                      const r = chart.width / 2.4;

                      ctx.save();
                      const drawArc = (start, end, color) => {{
                        ctx.beginPath(); ctx.arc(cx, cy, r, start, end);
                        ctx.strokeStyle = color; ctx.lineWidth = 16; ctx.stroke();
                      }};

                      drawArc(Math.PI, Math.PI + Math.PI * 0.2, "#e53935");
                      drawArc(Math.PI + Math.PI * 0.2, Math.PI + Math.PI * 0.4, "#f57c00");
                      drawArc(Math.PI + Math.PI * 0.4, Math.PI + Math.PI * 0.6, "#fbc02d");
                      drawArc(Math.PI + Math.PI * 0.6, Math.PI + Math.PI * 0.8, "#9acb82");
                      drawArc(Math.PI + Math.PI * 0.8, 2 * Math.PI, "#4caf50");

                      const angleRadians = Math.PI + angle;
                      const pointerLength = r * 0.9;
                      ctx.beginPath();
                      ctx.moveTo(cx + pointerLength * Math.cos(angleRadians), cy + pointerLength * Math.sin(angleRadians));
                      ctx.lineTo(cx + 6 * Math.cos(angleRadians + Math.PI / 2), cy + 6 * Math.sin(angleRadians + Math.PI / 2));
                      ctx.lineTo(cx + 6 * Math.cos(angleRadians - Math.PI / 2), cy + 6 * Math.sin(angleRadians - Math.PI / 2));
                      ctx.fillStyle = "#444"; ctx.fill();
                      
                      ctx.beginPath(); ctx.arc(cx, cy, 6, 0, 2 * Math.PI);
                      ctx.fillStyle = "#888"; ctx.fill();
                      ctx.restore();
                    }}
                  }}]
                }});
              }} catch (error) {{ 
                console.error('Erro gráfico:', error); 
              }}
            }}

            // INICIALIZAÇÃO
            function initDashboard() {{
              if (typeof Chart === 'undefined') {{ 
                setTimeout(initDashboard, 100); 
                return; 
              }}
              
              console.log('🚀 Iniciando dashboard técnico v1.0.20');
              buscarDadosApiInterna();
            }}

            if (document.readyState === 'loading') {{
              document.addEventListener('DOMContentLoaded', initDashboard);
            }} else {{ 
              initDashboard(); 
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
            <h1 style="color: #f7931a;">🔧 Dashboard Técnico v1.0.20</h1>
            <h2>Erro do Sistema:</h2>
            <pre style="color: #e53935;">{str(e)}</pre>
            <a href="/dashboard/" style="color: #f7931a;">← Voltar ao Dashboard</a>
        </body>
        </html>
        """