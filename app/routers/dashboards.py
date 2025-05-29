# app/routers/dashboards.py

from fastapi import APIRouter
from fastapi.responses import HTMLResponse
import requests
import logging

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def dashboard_index():
    """Dashboard principal consolidado com 5 velocímetros"""
    try:
        # Buscar dados da API consolidada
        try:
            # Tentar buscar da API local primeiro
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get("http://localhost:8000/api/v1/analise-btc", timeout=10.0)
                response.raise_for_status()
                dados_api = response.json()
        except Exception as e:
            logging.error(f"Erro ao buscar API consolidada: {str(e)}")
            # Fallback com dados mockados
            dados_api = {
                "score_final": 5.5,
                "classificacao_geral": "neutro",
                "kelly_allocation": "25%",
                "acao_recomendada": "Dados mockados - API indisponível",
                "resumo_blocos": {
                    "ciclos": {"score_consolidado": 6.2, "classificacao": "bom", "peso": "40%"},
                    "momentum": {"score_consolidado": 4.8, "classificacao": "neutro", "peso": "30%"},
                    "riscos": {"score_consolidado": 7.1, "classificacao": "bom", "peso": "10%"},
                    "tecnico": {"score_consolidado": 5.9, "classificacao": "neutro", "peso": "20%"}
                }
            }
        
        # Extrair dados com valores seguros - SCORES INTEIROS PARA CHART.JS
        score_geral = round(dados_api.get("score_final", 0) * 10)
        classificacao_geral = dados_api.get("classificacao_geral", "N/A")
        kelly_allocation = dados_api.get("kelly_allocation", "N/A")
        acao_recomendada = dados_api.get("acao_recomendada", "N/A")
        
        resumo = dados_api.get("resumo_blocos", {})
        
        # Scores por bloco - INTEIROS
        score_ciclos = round(resumo.get("ciclos", {}).get("score_consolidado", 0) * 10)
        classificacao_ciclos = resumo.get("ciclos", {}).get("classificacao", "N/A")
        peso_ciclos = resumo.get("ciclos", {}).get("peso", "40%")
        
        score_momentum = round(resumo.get("momentum", {}).get("score_consolidado", 0) * 10)
        classificacao_momentum = resumo.get("momentum", {}).get("classificacao", "N/A")
        peso_momentum = resumo.get("momentum", {}).get("peso", "30%")
        
        score_riscos = round(resumo.get("riscos", {}).get("score_consolidado", 0) * 10)
        classificacao_riscos = resumo.get("riscos", {}).get("classificacao", "N/A")
        peso_riscos = resumo.get("riscos", {}).get("peso", "10%")
        
        score_tecnico = round(resumo.get("tecnico", {}).get("score_consolidado", 0) * 10)
        classificacao_tecnico = resumo.get("tecnico", {}).get("classificacao", "N/A")
        peso_tecnico = resumo.get("tecnico", {}).get("peso", "20%")
        
        # HTML Template Completo
        html = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
          <meta charset="UTF-8" />
          <meta name="viewport" content="width=device-width, initial-scale=1.0" />
          <title>BTC Turbo - Dashboard Principal</title>
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
              font-size: clamp(24px, 5vw, 32px); color: #f7931a;
              margin-bottom: 1rem; padding: 0 2%; font-weight: 700;
            }}
            .subtitle {{
              color: #888; font-size: clamp(14px, 2.5vw, 18px); 
              margin-bottom: 2rem; padding: 0 2%;
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
            
            @media (max-width: 768px) {{
              .dashboard-grid {{
                grid-template-columns: 1fr;
                gap: 16px;
                padding: 0 0.5rem;
              }}
              .grafico {{
                padding: 20px 16px;
              }}
            }}
          </style>
        </head>
        <body>
          <h1>🚀 BTC Turbo - Dashboard Principal</h1>
          <div class="subtitle">
            Sistema v1.0.11 - Análise Consolidada | Kelly: {kelly_allocation} | {acao_recomendada}
          </div>
          
          <div class="dashboard-grid">
            <!-- Score Geral (Não clicável) -->
            <div class="grafico principal">
              <h3>🎯 Score Geral</h3>
              <canvas id="gaugeChart_geral" width="200" height="180"></canvas>
              <div id="classificacao_geral" class="classificacao">
                Score: {score_geral} - {classificacao_geral}
              </div>
              <div class="info-adicional">
                Consolidado de todos os blocos
              </div>
            </div>

            <!-- Bloco Ciclos (Clicável) -->
            <div class="grafico clicavel" onclick="navegarPara('/dashboard/ciclos')">
              <h3>🔄 Ciclos</h3>
              <canvas id="gaugeChart_ciclos" width="200" height="180"></canvas>
              <div id="classificacao_ciclos" class="classificacao">
                Score: {score_ciclos} - {classificacao_ciclos}
              </div>
              <div class="info-adicional">
                Peso: {peso_ciclos} | Clique para detalhes
              </div>
            </div>

            <!-- Bloco Momentum (Clicável) -->
            <div class="grafico clicavel" onclick="navegarPara('/dashboard/momentum')">
              <h3>⚡ Momentum</h3>
              <canvas id="gaugeChart_momentum" width="200" height="180"></canvas>
              <div id="classificacao_momentum" class="classificacao">
                Score: {score_momentum} - {classificacao_momentum}
              </div>
              <div class="info-adicional">
                Peso: {peso_momentum} | Clique para detalhes
              </div>
            </div>

            <!-- Bloco Riscos (Clicável) -->
            <div class="grafico clicavel" onclick="navegarPara('/dashboard/riscos')">
              <h3>🚨 Riscos</h3>
              <canvas id="gaugeChart_riscos" width="200" height="180"></canvas>
              <div id="classificacao_riscos" class="classificacao">
                Score: {score_riscos} - {classificacao_riscos}
              </div>
              <div class="info-adicional">
                Peso: {peso_riscos} | Clique para detalhes
              </div>
            </div>

            <!-- Bloco Técnico (Clicável) -->
            <div class="grafico clicavel" onclick="navegarPara('/dashboard/tecnico')">
              <h3>📈 Análise Técnica</h3>
              <canvas id="gaugeChart_tecnico" width="200" height="180"></canvas>
              <div id="classificacao_tecnico" class="classificacao">
                Score: {score_tecnico} - {classificacao_tecnico}
              </div>
              <div class="info-adicional">
                Peso: {peso_tecnico} | Clique para detalhes
              </div>
            </div>
          </div>

          <div class="footer">
            <a href="/docs">📋 APIs de Dados</a>
            <a href="/ping">🏥 Health Check</a>
            <a href="/api/v1/diagnostico/health-check">🔧 Diagnóstico</a>
            <a href="/api/v1/analise-btc">📊 API Consolidada</a>
          </div>

          <script>
            function navegarPara(url) {{
              window.location.href = url;
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
              }} catch (error) {{ console.error('Erro gráfico:', error); }}
            }}

            function initCharts() {{
              if (typeof Chart === 'undefined') {{ setTimeout(initCharts, 100); return; }}
              
              renderGauge("gaugeChart_geral", {score_geral});
              renderGauge("gaugeChart_ciclos", {score_ciclos});
              renderGauge("gaugeChart_momentum", {score_momentum});
              renderGauge("gaugeChart_riscos", {score_riscos});
              renderGauge("gaugeChart_tecnico", {score_tecnico});
            }}

            if (document.readyState === 'loading') {{
              document.addEventListener('DOMContentLoaded', initCharts);
            }} else {{ initCharts(); }}
          </script>
        </body>
        </html>
        """
        
        return html
        
    except Exception as e:
        return f"""
        <html>
        <body style="background: #0f111a; color: white; font-family: monospace; padding: 20px;">
            <h1 style="color: #f7931a;">🔧 Debug - Dashboard Principal</h1>
            <h2>Erro:</h2>
            <pre style="color: #e53935;">{str(e)}</pre>
            <a href="/docs" style="color: #f7931a;">← APIs</a>
        </body>
        </html>
        """