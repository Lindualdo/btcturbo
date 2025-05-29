# app/routers/dashboard_tecnico.py

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
import requests
import json
import logging

router = APIRouter()

@router.get("/tecnico", response_class=HTMLResponse)
async def dashboard_tecnico():
    """Dashboard de análise técnica - consome API externa temporariamente"""
    try:
        # Buscar dados da API externa (temporário)
        api_url = "https://btc-turbo-api-production.up.railway.app/api/v1/analise-tecnica-emas"
        
        try:
            response = requests.get(api_url, timeout=10)
            response.raise_for_status()
            dados_api = response.json()
        except requests.RequestException as e:
            logging.error(f"Erro ao buscar API externa: {str(e)}")
            # Fallback com dados mockados
            dados_api = {
                "consolidado": {"score": 7.5, "classificacao": "bom", "racional": "Dados mockados - API externa indisponível"},
                "emas": {
                    "1w": {"analise": {"score": 8.0, "classificacao": "bom", "observacao": "Semanal bullish"}},
                    "1d": {"analise": {"score": 7.2, "classificacao": "bom", "observacao": "Diário positivo"}},
                    "4h": {"analise": {"score": 6.8, "classificacao": "neutro", "observacao": "4H lateral"}},
                    "1h": {"analise": {"score": 5.5, "classificacao": "neutro", "observacao": "1H neutro"}},
                    "15m": {"analise": {"score": 4.2, "classificacao": "neutro", "observacao": "15M bearish"}}
                }
            }
        
        # Extrair dados com valores seguros
        consolidado = dados_api.get("consolidado", {})
        emas = dados_api.get("emas", {})
        
        score_consolidado = round(consolidado.get("score", 0) * 10, 1)
        classificacao_consolidada = consolidado.get("classificacao", "N/A")
        racional_consolidado = consolidado.get("racional", "Análise técnica multi-timeframe")
        
        # Timeframes
        score_1w = round(emas.get("1w", {}).get("analise", {}).get("score", 0) * 10, 1)
        classificacao_1w = emas.get("1w", {}).get("analise", {}).get("classificacao", "N/A")
        observacao_1w = emas.get("1w", {}).get("analise", {}).get("observacao", "Semanal")
        
        score_1d = round(emas.get("1d", {}).get("analise", {}).get("score", 0) * 10, 1)
        classificacao_1d = emas.get("1d", {}).get("analise", {}).get("classificacao", "N/A")
        observacao_1d = emas.get("1d", {}).get("analise", {}).get("observacao", "Diário")
        
        score_4h = round(emas.get("4h", {}).get("analise", {}).get("score", 0) * 10, 1)
        classificacao_4h = emas.get("4h", {}).get("analise", {}).get("classificacao", "N/A")
        observacao_4h = emas.get("4h", {}).get("analise", {}).get("observacao", "4 Horas")
        
        score_1h = round(emas.get("1h", {}).get("analise", {}).get("score", 0) * 10, 1)
        classificacao_1h = emas.get("1h", {}).get("analise", {}).get("classificacao", "N/A")
        observacao_1h = emas.get("1h", {}).get("analise", {}).get("observacao", "1 Hora")
        
        score_15m = round(emas.get("15m", {}).get("analise", {}).get("score", 0) * 10, 1)
        classificacao_15m = emas.get("15m", {}).get("analise", {}).get("classificacao", "N/A")
        observacao_15m = emas.get("15m", {}).get("analise", {}).get("observacao", "15 Minutos")
        
        # HTML Template Completo
        html = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
          <meta charset="UTF-8" />
          <meta name="viewport" content="width=device-width, initial-scale=1.0" />
          <title>BTC Turbo - Análise Técnica</title>
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
            .info-text {{ font-size: 12px; color: #888; margin-top: 10px; }}
            .tooltip {{
              margin-top: 2%; position: relative; cursor: pointer;
            }}
            .tooltip-text {{
              visibility: hidden; opacity: 0; transition: opacity 0.3s;
              font-size: clamp(11px, 2vw, 14px); color: #ccc; background: #1e1e1e;
              border: 1px solid #333; border-radius: 4px; padding: 8px 12px;
              position: absolute; bottom: -150%; left: 50%; transform: translateX(-50%);
              z-index: 1; white-space: normal; width: 200px; word-wrap: break-word;
              line-height: 1.3; text-align: left;
            }}
            .tooltip:hover .tooltip-text {{ visibility: visible; opacity: 1; }}
            .info-icon {{
              width: clamp(18px, 3vw, 24px); height: clamp(18px, 3vw, 24px);
              cursor: pointer; vertical-align: middle;
            }}
            canvas {{ max-width: 100%; height: auto; }}
            @media (max-width: 600px) {{
              .grafico {{ width: calc(100% - 2px); padding: 4% 3%; }}
              .dashboard-grid {{ flex-direction: column; align-items: center; gap: 0; }}
            }}
          </style>
        </head>
        <body>
          <h1>📈 BTC Turbo - Análise Técnica EMAs</h1>
          <div class="menu-scroll">
            <a href="/dashboard/">Home</a>
            <a href="/dashboard/riscos">Riscos</a>
            <a href="/dashboard/momentum">Momentum</a>
            <a href="/dashboard/ciclos">Ciclos</a>
            <a href="/dashboard/tecnico" class="ativo">Técnico</a>
          </div>
          
          <div class="dashboard-grid">
            <!-- Resultado Consolidado -->
            <div class="grafico">
              <h3>Resultado Consolidado</h3>
              <canvas id="gaugeChart_consolidado" width="200" height="180"></canvas>
              <div id="classificacao_consolidado" class="classificacao">
                Score: {score_consolidado} - {classificacao_consolidada}
              </div>
              <div class="tooltip">
                <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#ccc" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="info-icon">
                  <circle cx="12" cy="12" r="10" />
                  <line x1="12" y1="16" x2="12" y2="12" />
                  <line x1="12" y1="8" x2="12.01" y2="8" />
                </svg>
                <span class="tooltip-text">{racional_consolidado}</span>
              </div>
            </div>
                    
            <!-- Tempo Gráfico 1W -->
            <div class="grafico">
              <h3>Tempo Gráfico - 1W</h3>
              <canvas id="gaugeChart_1w" width="200" height="180"></canvas>
              <div id="classificacao_1w" class="classificacao">
                Score: {score_1w} - {classificacao_1w}
              </div>
              <div class="tooltip">
                <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#ccc" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="info-icon">
                  <circle cx="12" cy="12" r="10" />
                  <line x1="12" y1="16" x2="12" y2="12" />
                  <line x1="12" y1="8" x2="12.01" y2="8" />
                </svg>
                <span class="tooltip-text">{observacao_1w}</span>
              </div>
            </div>
                    
            <!-- Tempo Gráfico 1D -->
            <div class="grafico">
              <h3>Tempo Gráfico - 1D</h3>
              <canvas id="gaugeChart_1d" width="200" height="180"></canvas>
              <div id="classificacao_1d" class="classificacao">
                Score: {score_1d} - {classificacao_1d}
              </div>
              <div class="tooltip">
                <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#ccc" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="info-icon">
                  <circle cx="12" cy="12" r="10" />
                  <line x1="12" y1="16" x2="12" y2="12" />
                  <line x1="12" y1="8" x2="12.01" y2="8" />
                </svg>
                <span class="tooltip-text">{observacao_1d}</span>
              </div>
            </div>

            <!-- Tempo Gráfico 4H -->
            <div class="grafico">
              <h3>Tempo Gráfico - 4H</h3>
              <canvas id="gaugeChart_4h" width="200" height="180"></canvas>
              <div id="classificacao_4h" class="classificacao">
                Score: {score_4h} - {classificacao_4h}
              </div>
              <div class="tooltip">
                <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#ccc" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="info-icon">
                  <circle cx="12" cy="12" r="10" />
                  <line x1="12" y1="16" x2="12" y2="12" />
                  <line x1="12" y1="8" x2="12.01" y2="8" />
                </svg>
                <span class="tooltip-text">{observacao_4h}</span>
              </div>
            </div>

            <!-- Tempo Gráfico 1H -->
            <div class="grafico">
              <h3>Tempo Gráfico - 1H</h3>
              <canvas id="gaugeChart_1h" width="200" height="180"></canvas>
              <div id="classificacao_1h" class="classificacao">
                Score: {score_1h} - {classificacao_1h}
              </div>
              <div class="tooltip">
                <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#ccc" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="info-icon">
                  <circle cx="12" cy="12" r="10" />
                  <line x1="12" y1="16" x2="12" y2="12" />
                  <line x1="12" y1="8" x2="12.01" y2="8" />
                </svg>
                <span class="tooltip-text">{observacao_1h}</span>
              </div>
            </div>

            <!-- Tempo Gráfico 15M -->
            <div class="grafico">
              <h3>Tempo Gráfico - 15M</h3>
              <canvas id="gaugeChart_15m" width="200" height="180"></canvas>
              <div id="classificacao_15m" class="classificacao">
                Score: {score_15m} - {classificacao_15m}
              </div>
              <div class="tooltip">
                <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#ccc" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="info-icon">
                  <circle cx="12" cy="12" r="10" />
                  <line x1="12" y1="16" x2="12" y2="12" />
                  <line x1="12" y1="8" x2="12.01" y2="8" />
                </svg>
                <span class="tooltip-text">{observacao_15m}</span>
              </div>
            </div>
          </div>

          <script>
            function waitForChartJS() {{
              return new Promise((resolve) => {{
                if (typeof Chart !== 'undefined') {{
                  resolve();
                }} else {{
                  const checkChart = setInterval(() => {{
                    if (typeof Chart !== 'undefined') {{
                      clearInterval(checkChart);
                      resolve();
                    }}
                  }}, 100);
                }}
              }});
            }}

            function renderGauge({{ canvasId, score, classificacaoId }}) {{
              const canvas = document.getElementById(canvasId);
              if (!canvas) {{
                console.error(`Canvas ${{canvasId}} não encontrado`);
                return;
              }}

              const ctx = canvas.getContext('2d');
              if (!ctx) {{
                console.error(`Contexto 2D não disponível para ${{canvasId}}`);
                return;
              }}

              const existingChart = Chart.getChart(canvas);
              if (existingChart) {{
                existingChart.destroy();
              }}

              let corTexto;
              if (score < 20) corTexto = "#e53935";
              else if (score < 40) corTexto = "#f57c00";
              else if (score < 60) corTexto = "#fbc02d";
              else if (score < 80) corTexto = "#9acb82";
              else corTexto = "#4caf50";

              const classificacaoElement = document.getElementById(classificacaoId);
              if (classificacaoElement) {{
                classificacaoElement.style.color = corTexto;
              }}

              try {{
                new Chart(ctx, {{
                  type: 'doughnut',
                  data: {{
                    labels: ['Score'],
                    datasets: [{{
                      data: [100],
                      backgroundColor: ['#0000'],
                      borderWidth: 0,
                      cutout: '80%',
                    }}]
                  }},
                  options: {{
                    responsive: false,
                    rotation: -Math.PI,
                    circumference: Math.PI,
                    plugins: {{
                      tooltip: {{ enabled: false }},
                      legend: {{ display: false }}
                    }},
                  }},
                  plugins: [{{
                    id: 'customGauge',
                    afterDraw: (chart) => {{
                      const ctx = chart.ctx;
                      const angle = (score / 100) * Math.PI;
                      const cx = chart.width / 2;
                      const cy = chart.height - 42;
                      const r = chart.width / 2.4;

                      ctx.save();

                      const drawArc = (start, end, color) => {{
                        ctx.beginPath();
                        ctx.arc(cx, cy, r, start, end);
                        ctx.strokeStyle = color;
                        ctx.lineWidth = 16;
                        ctx.lineCap = "butt";
                        ctx.stroke();
                      }};

                      drawArc(Math.PI, Math.PI + Math.PI * 0.2 - 0.01, "#e53935");
                      drawArc(Math.PI + Math.PI * 0.2, Math.PI + Math.PI * 0.4 - 0.01, "#f57c00");
                      drawArc(Math.PI + Math.PI * 0.4, Math.PI + Math.PI * 0.6 - 0.01, "#fbc02d");
                      drawArc(Math.PI + Math.PI * 0.6, Math.PI + Math.PI * 0.8 - 0.01, "#9acb82");
                      drawArc(Math.PI + Math.PI * 0.8, 2 * Math.PI - 0.01, "#4caf50");

                      const pointerLength = r * 0.9;
                      const pointerWidth = 6;
                      const angleRadians = Math.PI + angle;

                      const x1 = cx + pointerLength * Math.cos(angleRadians);
                      const y1 = cy + pointerLength * Math.sin(angleRadians);
                      const x2 = cx + pointerWidth * Math.cos(angleRadians + Math.PI / 2);
                      const y2 = cy + pointerWidth * Math.sin(angleRadians + Math.PI / 2);
                      const x3 = cx + pointerWidth * Math.cos(angleRadians - Math.PI / 2);
                      const y3 = cy + pointerWidth * Math.sin(angleRadians - Math.PI / 2);

                      ctx.beginPath();
                      ctx.moveTo(x1, y1);
                      ctx.lineTo(x2, y2);
                      ctx.lineTo(x3, y3);
                      ctx.closePath();
                      ctx.fillStyle = "#444";
                      ctx.fill();

                      ctx.beginPath();
                      ctx.arc(cx, cy, 6, 0, 2 * Math.PI);
                      ctx.fillStyle = "#888";
                      ctx.fill();

                      ctx.font = "400 11px system-ui, sans-serif";
                      ctx.fillStyle = "#888";
                      ctx.textAlign = "center";
                      ctx.textBaseline = "middle";
                      const x0 = cx + r * Math.cos(Math.PI);
                      const y0 = cy + r * Math.sin(Math.PI);
                      const x100 = cx + r * Math.cos(0);
                      const y100 = cy + r * Math.sin(0);
                      ctx.fillText("0", x0, y0 + 15);
                      ctx.fillText("100", x100 - 3, y100 + 15);

                      ctx.restore();
                    }}
                  }}]
                }});
              }} catch (error) {{
                console.error(`Erro ao criar gráfico ${{canvasId}}:`, error);
                setTimeout(() => {{
                  renderGauge({{ canvasId, score, classificacaoId }});
                }}, 500);
              }}
            }}

            async function initializeCharts() {{
              await waitForChartJS();
              
              const charts = [
                {{ canvasId: "gaugeChart_consolidado", score: {score_consolidado}, classificacaoId: "classificacao_consolidado" }},
                {{ canvasId: "gaugeChart_1w", score: {score_1w}, classificacaoId: "classificacao_1w" }},
                {{ canvasId: "gaugeChart_1d", score: {score_1d}, classificacaoId: "classificacao_1d" }},
                {{ canvasId: "gaugeChart_4h", score: {score_4h}, classificacaoId: "classificacao_4h" }},
                {{ canvasId: "gaugeChart_1h", score: {score_1h}, classificacaoId: "classificacao_1h" }},
                {{ canvasId: "gaugeChart_15m", score: {score_15m}, classificacaoId: "classificacao_15m" }}
              ];

              charts.forEach((chart, index) => {{
                setTimeout(() => {{
                  renderGauge(chart);
                }}, index * 200);
              }});
            }}

            if (document.readyState === 'loading') {{
              document.addEventListener('DOMContentLoaded', initializeCharts);
            }} else {{
              initializeCharts();
            }}

            let resizeTimeout;
            window.addEventListener('resize', () => {{
              clearTimeout(resizeTimeout);
              resizeTimeout = setTimeout(initializeCharts, 300);
            }});
          </script>
        </body>
        </html>
        """
        
        return html
        
    except Exception as e:
        return f"""
        <html>
        <body style="background: #0f111a; color: white; font-family: monospace; padding: 20px;">
            <h1 style="color: #f7931a;">🔧 Debug - Dashboard Técnico</h1>
            <h2>Erro:</h2>
            <pre style="color: #e53935;">{str(e)}</pre>
            <a href="/dashboard/" style="color: #f7931a;">← Voltar</a>
        </body>
        </html>
        """