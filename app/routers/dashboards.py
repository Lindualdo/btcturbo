# app/routers/dashboards.py - v1.0.20 - NOVOS PESOS + TOGGLE RISCO

from fastapi import APIRouter
from fastapi.responses import HTMLResponse
import requests
import logging

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def dashboard_index():
    """Dashboard principal v1.0.20 - Novos pesos + Toggle redução por risco"""
    try:
        # HTML Template Completo v1.0.20
        html = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
          <meta charset="UTF-8" />
          <meta name="viewport" content="width=device-width, initial-scale=1.0" />
          <title>BTC Turbo - Dashboard Principal v1.0.20</title>
          <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
          <style>
            *, *::before, *::after {{ box-sizing: border-box; }}
            html {{ overflow-x: hidden; }}
            body {{
              background: #0f111a; color: #fff; text-align: center;
              font-family: system-ui, sans-serif; padding: 2%; margin: 0;
              min-height: 100vh; width: 100%; overflow-x: hidden; max-width: 100vw;
            }}
            .version {{
              position: absolute; top: 10px; right: 15px; 
              font-size: 10px; color: #666; font-weight: normal;
            }}
            h1 {{
              font-size: clamp(24px, 5vw, 32px); color: #f7931a;
              margin-bottom: 1rem; padding: 0 2%; font-weight: 700;
            }}
            .subtitle {{
              color: #888; font-size: clamp(14px, 2.5vw, 18px); 
              margin-bottom: 1rem; padding: 0 2%;
            }}
            .toggle-container {{
              display: flex; justify-content: center; align-items: center; gap: 1rem;
              margin-bottom: 2rem; padding: 1rem; background: #161b22; border-radius: 8px;
              max-width: 700px; margin-left: auto; margin-right: auto;
              flex-wrap: wrap;
            }}
            .toggle-switch {{
              position: relative; display: inline-block; width: 60px; height: 34px;
            }}
            .toggle-switch input {{
              opacity: 0; width: 0; height: 0;
            }}
            .slider {{
              position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0;
              background-color: #ccc; transition: .4s; border-radius: 34px;
            }}
            .slider:before {{
              position: absolute; content: ""; height: 26px; width: 26px; left: 4px; bottom: 4px;
              background-color: white; transition: .4s; border-radius: 50%;
            }}
            input:checked + .slider {{
              background-color: #f7931a;
            }}
            input:checked + .slider:before {{
              transform: translateX(26px);
            }}
            .toggle-label {{
              color: #fff; font-weight: 600; font-size: clamp(14px, 2vw, 16px);
            }}
            .status-info {{
              background: #1e1e1e; padding: 1rem; border-radius: 8px; margin-bottom: 2rem;
              max-width: 900px; margin-left: auto; margin-right: auto;
              border-left: 4px solid #f7931a;
            }}
            .pesos-info {{
              background: #0a0d14; padding: 0.8rem; border-radius: 6px; margin-top: 1rem;
              font-size: 12px; color: #f7931a; border: 1px solid #333;
            }}
            .dashboard-grid {{
              display: grid; 
              grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
              gap: clamp(12px, 2vw, 24px); 
              margin-bottom: 3rem; 
              max-width: 1400px; 
              margin-left: auto; 
              margin-right: auto;
              padding: 0 1rem;
            }}
            .grafico {{
              background: #161b22; border-radius: 12px;
              padding: clamp(16px, 3vw, 24px); 
              box-shadow: 0 4px 20px rgba(0,0,0,0.6);
              display: flex; flex-direction: column; align-items: center;
              transition: all 0.3s ease;
              border: 2px solid transparent;
            }}
            .grafico.clicavel {{
              cursor: pointer;
            }}
            .grafico.clicavel:hover {{
              border-color: #f7931a;
              transform: translateY(-4px);
              box-shadow: 0 8px 25px rgba(247, 147, 26, 0.3);
            }}
            .grafico.risco-como-redutor {{
              opacity: 0.8;
              border: 2px dashed #666;
              position: relative;
            }}
            .grafico.risco-como-redutor::before {{
              content: "REDUTOR";
              position: absolute;
              top: 8px;
              right: 8px;
              background: #666;
              color: white;
              padding: 2px 6px;
              border-radius: 4px;
              font-size: 10px;
              font-weight: bold;
            }}
            .grafico h3 {{
              font-size: clamp(16px, 2.5vw, 20px); 
              margin: 0 0 1rem 0; 
              color: #fff;
            }}
            .grafico.principal h3 {{
              color: #f7931a;
              font-size: clamp(18px, 3vw, 24px);
            }}
            .classificacao {{
              font-size: clamp(13px, 2.2vw, 16px); 
              margin-top: 1rem; 
              font-weight: 600;
            }}
            .info-adicional {{
              font-size: clamp(11px, 1.8vw, 14px); 
              color: #888; 
              margin-top: 0.5rem;
              text-align: center;
            }}
            .peso-info {{
              font-size: clamp(10px, 1.6vw, 12px);
              color: #f7931a;
              margin-top: 0.25rem;
              font-weight: bold;
            }}
            canvas {{ max-width: 100%; height: auto; }}
            
            .footer {{
              margin-top: 3rem; padding-top: 2rem; 
              border-top: 1px solid #333; text-align: center;
            }}
            .footer a {{
              color: #f7931a; text-decoration: none; 
              margin: 0 clamp(8px, 2vw, 16px);
              font-size: clamp(12px, 2vw, 14px);
            }}
            .footer a:hover {{ text-decoration: underline; }}
            
            .loading {{
              color: #f7931a; font-style: italic;
            }}
            
            @media (max-width: 768px) {{
              .dashboard-grid {{
                grid-template-columns: 1fr;
                gap: 16px;
                padding: 0 0.5rem;
              }}
              .grafico {{
                padding: 20px 16px;
              }}
              .toggle-container {{
                flex-direction: column; gap: 0.5rem; text-align: center;
              }}
              .version {{ position: static; text-align: center; margin-bottom: 10px; }}
            }}
          </style>
        </head>
        <body>
          <div class="version">v1.0.20</div>
          <h1>🚀 BTC Turbo - Dashboard Principal</h1>
          <div class="subtitle" id="subtitle">
            Sistema v1.0.20 - Carregando dados...
          </div>
          
          <!-- Toggle para redução por risco -->
          <div class="toggle-container">
            <span class="toggle-label">Aplicar Redução por Risco:</span>
            <label class="toggle-switch">
              <input type="checkbox" id="toggleRisco" checked onchange="atualizarDados()">
              <span class="slider"></span>
            </label>
            <span class="toggle-label" id="toggleStatus">Ativado</span>
            
            <!-- Botão Forçar Atualização -->
            <button id="btnForceUpdate" onclick="forcarAtualizacao()" style="
              background: #f7931a; color: #000; border: none; border-radius: 6px;
              padding: 8px 16px; margin-left: 16px; cursor: pointer; font-weight: 600;
              font-size: 14px; transition: all 0.3s ease;
            " onmouseover="this.style.background='#e8851a'" onmouseout="this.style.background='#f7931a'">
              🔄 Forçar Atualização
            </button>
          </div>

          <!-- Status da configuração atual -->
          <div class="status-info" id="statusInfo">
            Carregando configuração...
          </div>
          
          <div class="dashboard-grid">
            <!-- Score Geral (Não clicável) -->
            <div class="grafico principal">
              <h3>🎯 Score Geral</h3>
              <canvas id="gaugeChart_geral" width="200" height="180"></canvas>
              <div id="classificacao_geral" class="classificacao loading">
                Carregando...
              </div>
              <div class="info-adicional" id="info_geral">
                Novos pesos v1.0.20
              </div>
            </div>

            <!-- Bloco Técnico (50% - AUMENTADO) -->
            <div class="grafico clicavel" onclick="navegarPara('/dashboard/tecnico')">
              <h3>📈 Análise Técnica</h3>
              <canvas id="gaugeChart_tecnico" width="200" height="180"></canvas>
              <div id="classificacao_tecnico" class="classificacao loading">
                Carregando...
              </div>
              <div class="info-adicional" id="info_tecnico">
                Clique para detalhes
              </div>
              <div class="peso-info" id="peso_tecnico">Peso: 50% 📈</div>
            </div>

            <!-- Bloco Ciclos (30% - REDUZIDO) -->
            <div class="grafico clicavel" onclick="navegarPara('/dashboard/ciclos')">
              <h3>🔄 Ciclos</h3>
              <canvas id="gaugeChart_ciclos" width="200" height="180"></canvas>
              <div id="classificacao_ciclos" class="classificacao loading">
                Carregando...
              </div>
              <div class="info-adicional" id="info_ciclos">
                Clique para detalhes
              </div>
              <div class="peso-info" id="peso_ciclos">Peso: 30% 🔄</div>
            </div>

            <!-- Bloco Momentum (20% - REDUZIDO) -->
            <div class="grafico clicavel" onclick="navegarPara('/dashboard/momentum')">
              <h3>⚡ Momentum</h3>
              <canvas id="gaugeChart_momentum" width="200" height="180"></canvas>
              <div id="classificacao_momentum" class="classificacao loading">
                Carregando...
              </div>
              <div class="info-adicional" id="info_momentum">
                Clique para detalhes
              </div>
              <div class="peso-info" id="peso_momentum">Peso: 20% ⚡</div>
            </div>

            <!-- Bloco Riscos (COMO REDUTOR) -->
            <div class="grafico clicavel risco-como-redutor" id="grafico_riscos" onclick="navegarPara('/dashboard/riscos')">
              <h3>🚨 Riscos</h3>
              <canvas id="gaugeChart_riscos" width="200" height="180"></canvas>
              <div id="classificacao_riscos" class="classificacao loading">
                Carregando...
              </div>
              <div class="info-adicional" id="info_riscos">
                Usado como redutor do score
              </div>
              <div class="peso-info" id="peso_riscos">Peso: 0% (Redutor)</div>
            </div>
          </div>

          <div class="footer">
            <a href="/docs">📋 APIs de Dados</a>
            <a href="/ping">🏥 Health Check</a>
            <a href="/api/v1/diagnostico/health-check">🔧 Diagnóstico</a>
            <a href="/api/v1/analise-btc">📊 API Consolidada</a>
          </div>

          <script>
            let dadosAtuais = null;

            function navegarPara(url) {{
              window.location.href = url;
            }}

            async function buscarDados(incluirRisco = true) {{
              try {{
                const response = await fetch(`/api/v1/analise-btc?incluir_risco=${{incluirRisco}}`);
                const dados = await response.json();
                
                if (dados.error || dados.status === 'error') {{
                  throw new Error(dados.erro || 'Erro na API');
                }}
                
                dadosAtuais = dados;
                atualizarInterface(dados);
                
              }} catch (error) {{
                console.error('Erro ao buscar dados:', error);
                mostrarErro(error.message);
              }}
            }}

            function atualizarInterface(dados) {{
              const config = dados.configuracao || {{}};
              const resumo = dados.resumo_blocos || {{}};
              const versao = dados.versao || "1.0.20";
              
              // Atualizar subtitle com novos dados
              const kelly = dados.kelly_allocation || 'N/A';
              const acao = dados.acao_recomendada || 'N/A';
              document.getElementById('subtitle').textContent = 
                `Sistema v${{versao}} - Kelly: ${{kelly}} | ${{acao}}`;
              
              // Atualizar toggle status
              const toggleStatus = document.getElementById('toggleStatus');
              const statusInfo = document.getElementById('statusInfo');
              
              if (config.incluir_risco) {{
                toggleStatus.textContent = 'Ativado';
                
                const scoreBase = dados.score_base || dados.score_final;
                const scoreFinal = dados.score_final;
                const redutor = dados.redutor_risco || 1.0;
                
                statusInfo.innerHTML = `
                  <strong>✅ Redução por Risco ATIVADA</strong><br>
                  <div style="font-size: 12px; margin-top: 8px; color: #888;">
                    Score Base: ${scoreBase} | Redutor: ${redutor.toFixed(2)} | Score Final: ${scoreFinal}
                  </div>
                  <div class="pesos-info">
                    📈 Técnico: 50% | 🔄 Ciclo: 30% | ⚡ Momentum: 20% | 🚨 Risco: Redutor (${config.nota_risco || 'Temporariamente 1.0'})
                  </div>
              } else {
                toggleStatus.textContent = 'Desativado';
                statusInfo.innerHTML = `
                  <strong>⚠️ Redução por Risco DESATIVADA</strong><br>
                  <div style="font-size: 12px; margin-top: 8px; color: #888;">
                    Usando apenas Score Base: ${dados.score_final}
                  </div>
                  <div class="pesos-info">
                    📈 Técnico: 50% | 🔄 Ciclo: 30% | ⚡ Momentum: 20% | 🚨 Risco: Ignorado
                  </div>
                `;
              }
              
              // Atualizar scores e gráficos
              const scoreGeral = Math.round((dados.score_final || 0) * 10);
              atualizarGrafico('gaugeChart_geral', scoreGeral, 'classificacao_geral', dados.classificacao_geral || 'N/A');
              
              // Atualizar blocos individuais com NOVOS PESOS
              atualizarBloco('tecnico', resumo.tecnico || {}, '50%');
              atualizarBloco('ciclos', resumo.ciclos || {}, '30%');
              atualizarBloco('momentum', resumo.momentum || {}, '20%');
              atualizarBloco('riscos', resumo.riscos || {}, '0% (Redutor)');
            }

            function atualizarBloco(nome, dados, pesoFixo) {
              const score = Math.round((dados.score_consolidado || 0) * 10);
              const classificacao = dados.classificacao || 'N/A';
              const incluido = dados.incluido_no_calculo;
              
              atualizarGrafico(`gaugeChart_${nome}`, score, `classificacao_${nome}`, classificacao);
              
              // Atualizar peso com os novos valores fixos
              const pesoElement = document.getElementById(`peso_${nome}`);
              if (pesoElement) {
                if (nome === 'tecnico') {
                  pesoElement.innerHTML = 'Peso: 50% 📈';
                } else if (nome === 'ciclos') {
                  pesoElement.innerHTML = 'Peso: 30% 🔄';
                } else if (nome === 'momentum') {
                  pesoElement.innerHTML = 'Peso: 20% ⚡';
                } else if (nome === 'riscos') {
                  pesoElement.innerHTML = 'Peso: 0% (Redutor)';
                }
                pesoElement.style.color = incluido ? '#f7931a' : '#666';
              }
            }

            function atualizarGrafico(canvasId, score, classificacaoId, classificacao) {
              // Atualizar texto
              const element = document.getElementById(classificacaoId);
              if (element) {
                element.textContent = `Score: ${score} - ${classificacao}`;
                element.classList.remove('loading');
              }
              
              // Renderizar gráfico
              renderGauge(canvasId, score);
            }

            function atualizarDados() {
              const toggle = document.getElementById('toggleRisco');
              const incluirRisco = toggle.checked; // Agora: checked = incluir redução
              buscarDados(incluirRisco);
            }

            function forcarAtualizacao() {
              const btnForce = document.getElementById('btnForceUpdate');
              const toggle = document.getElementById('toggleRisco');
              const incluirRisco = toggle.checked;
              
              // Visual feedback
              btnForce.disabled = true;
              btnForce.innerHTML = '⏳ Atualizando...';
              btnForce.style.background = '#666';
              
              // Mostrar loading nos gráficos
              document.getElementById('subtitle').textContent = 'Forçando atualização dos dados v1.0.20...';
              
              // Chamar API com force_update=true
              buscarDadosComForce(incluirRisco);
            }

            async function buscarDadosComForce(incluirRisco = true) {
              try {
                const response = await fetch(`/api/v1/analise-btc?incluir_risco=${incluirRisco}&force_update=true`);
                const dados = await response.json();
                
                if (dados.error || dados.status === 'error') {
                  throw new Error(dados.erro || 'Erro na API');
                }
                
                dadosAtuais = dados;
                atualizarInterface(dados);
                
                // Resetar botão
                const btnForce = document.getElementById('btnForceUpdate');
                btnForce.disabled = false;
                btnForce.innerHTML = '🔄 Forçar Atualização';
                btnForce.style.background = '#f7931a';
                
              } catch (error) {
                console.error('Erro ao forçar atualização:', error);
                mostrarErro(error.message);
                
                // Resetar botão mesmo com erro
                const btnForce = document.getElementById('btnForceUpdate');
                btnForce.disabled = false;
                btnForce.innerHTML = '❌ Erro - Tentar Novamente';
                btnForce.style.background = '#e53935';
                
                // Voltar ao normal após 3s
                setTimeout(() => {
                  btnForce.innerHTML = '🔄 Forçar Atualização';
                  btnForce.style.background = '#f7931a';
                }, 3000);
              }
            }

            function mostrarErro(mensagem) {
              document.getElementById('subtitle').textContent = `Erro v1.0.20: ${mensagem}`;
              document.getElementById('statusInfo').innerHTML = 
                `<strong>❌ Erro ao carregar dados</strong> - ${mensagem}`;
            }

            function renderGauge(canvasId, score) {
              const canvas = document.getElementById(canvasId);
              if (!canvas) return;
              
              const ctx = canvas.getContext('2d');
              const existingChart = Chart.getChart(canvas);
              if (existingChart) existingChart.destroy();

              try {
                new Chart(ctx, {
                  type: 'doughnut',
                  data: { datasets: [{ data: [100], backgroundColor: ['#0000'], borderWidth: 0, cutout: '80%' }] },
                  options: {
                    responsive: false, rotation: -Math.PI, circumference: Math.PI,
                    plugins: { tooltip: { enabled: false }, legend: { display: false } }
                  },
                  plugins: [{
                    afterDraw: (chart) => {
                      const ctx = chart.ctx;
                      const angle = (score / 100) * Math.PI;
                      const cx = chart.width / 2;
                      const cy = chart.height - 42;
                      const r = chart.width / 2.4;

                      ctx.save();
                      const drawArc = (start, end, color) => {
                        ctx.beginPath(); ctx.arc(cx, cy, r, start, end);
                        ctx.strokeStyle = color; ctx.lineWidth = 16; ctx.stroke();
                      };

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
                    }
                  }]
                });
              } catch (error) { 
                console.error('Erro gráfico:', error); 
              }
            }

            function initCharts() {
              if (typeof Chart === 'undefined') { 
                setTimeout(initCharts, 100); 
                return; 
              }
              
              console.log('🚀 Iniciando dashboard v1.0.20 com novos pesos');
              // Carregar dados iniciais com redução ativada por padrão
              buscarDados(true);
            }

            if (document.readyState === 'loading') {
              document.addEventListener('DOMContentLoaded', initCharts);
            } else { 
              initCharts(); 
            }
          </script>
        </body>
        </html>
        """
        
        return html
        
    except Exception as e:
        return f"""
        <html>
        <body style="background: #0f111a; color: white; font-family: monospace; padding: 20px;">
            <h1 style="color: #f7931a;">🔧 Debug - Dashboard Principal v1.0.20</h1>
            <h2>Erro:</h2>
            <pre style="color: #e53935;">{str(e)}</pre>
            <a href="/docs" style="color: #f7931a;">← APIs</a>
        </body>
        </html>
        """