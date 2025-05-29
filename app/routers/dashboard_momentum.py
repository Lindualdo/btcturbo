# app/routers/dashboard_momentum.py

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from app.services.scores import momentum
import json

router = APIRouter()

@router.get("/momentum", response_class=HTMLResponse)
async def dashboard_momentum():
    """Dashboard de análise de momentum v1.0.12"""
    try:
        # Buscar dados da API interna
        dados = momentum.calcular_score()
        
        # Extrair dados com valores padrão seguros - TODOS SCORES INTEIROS
        score_consolidado = round(dados.get("score_consolidado", 0) * 10)
        classificacao_consolidada = dados.get("classificacao_consolidada", "N/A")
        
        indicadores = dados.get("indicadores", {})
        rsi_data = indicadores.get("RSI_Semanal", {})
        funding_data = indicadores.get("Funding_Rates", {})
        netflow_data = indicadores.get("Exchange_Netflow", {})
        ls_data = indicadores.get("Long_Short_Ratio", {})
        
        # Valores seguros para cada indicador - TODOS SCORES INTEIROS
        score_rsi = round(rsi_data.get("score", 0) * 10)
        classificacao_rsi = rsi_data.get("classificacao", "N/A")
        valor_rsi = str(rsi_data.get("valor", "N/A"))
        peso_rsi = str(rsi_data.get("peso", "N/A"))
        
        score_funding = round(funding_data.get("score", 0) * 10)
        classificacao_funding = funding_data.get("classificacao", "N/A")
        valor_funding = str(funding_data.get("valor", "N/A"))
        peso_funding = str(funding_data.get("peso", "N/A"))
        
        score_netflow = round(netflow_data.get("score", 0) * 10)
        classificacao_netflow = netflow_data.get("classificacao", "N/A")
        valor_netflow = f"{netflow_data.get('valor', 0):.0f} BTC" if netflow_data.get('valor') else "N/A"
        peso_netflow = str(netflow_data.get("peso", "N/A"))
        
        score_ls = round(ls_data.get("score", 0) * 10)
        classificacao_ls = ls_data.get("classificacao", "N/A")
        valor_ls = str(ls_data.get("valor", "N/A"))
        peso_ls = str(ls_data.get("peso", "N/A"))
        
        # HTML Template Completo
        html = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
          <meta charset="UTF-8" />
          <meta name="viewport" content="width=device-width, initial-scale=1.0" />
          <title>BTC Turbo - Análise de Momentum v1.0.12</title>
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
            canvas {{ max-width: 100%; height: auto; }}
            @media (max-width: 600px) {{
              .grafico {{ width: calc(100% - 2px); padding: 4% 3%; }}
              .dashboard-grid {{ flex-direction: column; align-items: center; gap: 0; }}
            }}
          </style>
        </head>
        <body>
          <h1>⚡ BTC Turbo - Análise de Momentum v1.0.12</h1>
          <div class="menu-scroll">
            <a href="/dashboard/">Home</a>
            <a href="/dashboard/riscos">Riscos</a>
            <a href="/dashboard/momentum" class="ativo">Momentum</a>
            <a href="/dashboard/ciclos">Ciclos</a>
            <a href="/dashboard/tecnico">Técnica</a>
          </div>
          
          <div class="dashboard-grid">
            <!-- Resultado Consolidado -->
            <div class="grafico">
              <h3>Resultado Consolidado</h3>
              <canvas id="gaugeChart_consolidado" width="200" height="180"></canvas>
              <div id="classificacao_consolidado" class="classificacao">
                Score: {score_consolidado} - {classificacao_consolidada}
              </div>
            </div>
                    
            <!-- RSI Semanal -->
            <div class="grafico">
              <h3>RSI Semanal</h3>
              <canvas id="gaugeChart_rsi" width="200" height="180"></canvas>
              <div id="classificacao_rsi" class="classificacao">
                Score: {score_rsi} - {classificacao_rsi}
              </div>
              <div class="info-text">Valor: {valor_rsi} | Peso: {peso_rsi}</div>
            </div>
                    
            <!-- Funding Rates -->
            <div class="grafico">
              <h3>Funding Rates</h3>
              <canvas id="gaugeChart_funding" width="200" height="180"></canvas>
              <div id="classificacao_funding" class="classificacao">
                Score: {score_funding} - {classificacao_funding}
              </div>
              <div class="info-text">Valor: {valor_funding} | Peso: {peso_funding}</div>
            </div>

            <!-- Exchange Netflow -->
            <div class="grafico">
              <h3>Exchange Netflow 7D</h3>
              <canvas id="gaugeChart_netflow" width="200" height="180"></canvas>
              <div id="classificacao_netflow" class="classificacao">
                Score: {score_netflow} - {classificacao_netflow}
              </div>
              <div class="info-text">Valor: {valor_netflow} | Peso: {peso_netflow}</div>
            </div>

            <!-- Long/Short Ratio -->
            <div class="grafico">
              <h3>Long/Short Ratio</h3>
              <canvas id="gaugeChart_ls" width="200" height="180"></canvas>
              <div id="classificacao_ls" class="classificacao">
                Score: {score_ls} - {classificacao_ls}
              </div>
              <div class="info-text">Valor: {valor_ls} | Peso: {peso_ls}</div>
            </div>
          </div>

          <script>
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
              
              renderGauge("gaugeChart_consolidado", {score_consolidado});
              renderGauge("gaugeChart_rsi", {score_rsi});
              renderGauge("gaugeChart_funding", {score_funding});
              renderGauge("gaugeChart_netflow", {score_netflow});
              renderGauge("gaugeChart_ls", {score_ls});
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
            <h1 style="color: #f7931a;">🔧 Debug - Dashboard Momentum v1.0.12</h1>
            <h2>Erro:</h2>
            <pre style="color: #e53935;">{str(e)}</pre>
            <a href="/dashboard/" style="color: #f7931a;">← Voltar</a>
        </body>
        </html>
        """