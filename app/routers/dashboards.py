# app/routers/dashboards.py

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from app.services.scores import ciclos, momentum, riscos, tecnico
import json

router = APIRouter()

@router.get("/riscos", response_class=HTMLResponse)
async def dashboard_riscos():
    """Dashboard de análise de riscos"""
    try:
        # Buscar dados da API interna
        dados = riscos.calcular_score()
        
        # Template HTML embutido (temporário)
        html_template = """
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
          <meta charset="UTF-8" />
          <meta name="viewport" content="width=device-width, initial-scale=1.0" />
          <title>BTC Turbo - Análise de Riscos</title>
          <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
          <style>
            body {
              background: #0f111a;
              color: #fff;
              text-align: center;
              font-family: system-ui, sans-serif;
              padding: 2%;
              margin: 0;
              min-height: 100vh;
            }
            h1 {
              font-size: clamp(20px, 4vw, 28px);
              color: #f7931a;
              margin-bottom: 3%;
              font-weight: 700;
            }
            .dashboard-grid {
              display: flex;
              flex-wrap: wrap;
              justify-content: center;
              gap: 2%;
              margin-bottom: 4%;
            }
            .grafico {
              width: clamp(200px, 30%, 280px);
              background: #161b22;
              border-radius: 4%;
              padding: 3% 2%;
              box-shadow: 0 0 10px rgba(0,0,0,0.6);
              display: flex;
              flex-direction: column;
              align-items: center;
              margin-bottom: 2%;
            }
            .classificacao {
              font-size: clamp(12px, 2.2vw, 16px);
              margin-top: 2%;
              font-weight: 600;
            }
            .menu-scroll {
              display: flex;
              justify-content: center;
              gap: clamp(8px, 1.5vw, 24px);
              margin-bottom: 4%;
              padding: 1.5%;
              border-bottom: 1px solid #333;
            }
            .menu-scroll a {
              color: #888;
              font-weight: 600;
              text-decoration: none;
              padding: clamp(8px, 1.5vw, 12px) clamp(12px, 2vw, 20px);
              border-bottom: 3px solid transparent;
              transition: 0.3s;
              font-size: clamp(14px, 1.6vw, 16px);
            }
            .menu-scroll a:hover {
              color: #f7931a;
              border-bottom: 3px solid #f7931a;
            }
            .menu-scroll a.ativo {
              color: #f7931a;
              border-bottom: 3px solid #f7931a;
            }
            canvas {
              max-width: 100%;
              height: auto;
            }
          </style>
        </head>
        <body>
          <h1>🚀 BTC Turbo - Análise de Riscos</h1>
          <div class="menu-scroll">
            <a href="/dashboard/tecnico">Técnico</a>
            <a href="/dashboard/ciclos">Ciclos</a>
            <a href="/dashboard/momentum">Momentum</a>
            <a href="/dashboard/riscos" class="ativo">Riscos</a>
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
                    
            <!-- Distância Liquidação -->
            <div class="grafico">
              <h3>Distância Liquidação</h3>
              <canvas id="gaugeChart_dist" width="200" height="180"></canvas>
              <div id="classificacao_dist" class="classificacao">
                Score: {score_dist} - {classificacao_dist}
              </div>
              <p>Valor: {valor_dist} | Peso: {peso_dist}</p>
            </div>
                    
            <!-- Health Factor -->
            <div class="grafico">
              <h3>Health Factor</h3>
              <canvas id="gaugeChart_health" width="200" height="180"></canvas>
              <div id="classificacao_health" class="classificacao">
                Score: {score_health} - {classificacao_health}
              </div>
              <p>Valor: {valor_health} | Peso: {peso_health}</p>
            </div>
          </div>

          <script>
            function renderGauge(canvasId, score) {{
              const canvas = document.getElementById(canvasId);
              const ctx = canvas.getContext('2d');
              
              // Limpar gráfico existente
              const existingChart = Chart.getChart(canvas);
              if (existingChart) existingChart.destroy();

              // Cor baseada no score
              let cor = score < 20 ? "#e53935" : score < 40 ? "#f57c00" : score < 60 ? "#fbc02d" : score < 80 ? "#9acb82" : "#4caf50";

              new Chart(ctx, {{
                type: 'doughnut',
                data: {{
                  datasets: [{{ data: [100], backgroundColor: ['#0000'], borderWidth: 0, cutout: '80%' }}]
                }},
                options: {{
                  responsive: false,
                  rotation: -Math.PI,
                  circumference: Math.PI,
                  plugins: {{ tooltip: {{ enabled: false }}, legend: {{ display: false }} }}
                }},
                plugins: [{{
                  afterDraw: (chart) => {{
                    const ctx = chart.ctx;
                    const angle = (score / 100) * Math.PI;
                    const cx = chart.width / 2;
                    const cy = chart.height - 42;
                    const r = chart.width / 2.4;

                    // Desenhar arcos coloridos
                    const drawArc = (start, end, color) => {{
                      ctx.beginPath();
                      ctx.arc(cx, cy, r, start, end);
                      ctx.strokeStyle = color;
                      ctx.lineWidth = 16;
                      ctx.stroke();
                    }};

                    drawArc(Math.PI, Math.PI + Math.PI * 0.2, "#e53935");
                    drawArc(Math.PI + Math.PI * 0.2, Math.PI + Math.PI * 0.4, "#f57c00");
                    drawArc(Math.PI + Math.PI * 0.4, Math.PI + Math.PI * 0.6, "#fbc02d");
                    drawArc(Math.PI + Math.PI * 0.6, Math.PI + Math.PI * 0.8, "#9acb82");
                    drawArc(Math.PI + Math.PI * 0.8, 2 * Math.PI, "#4caf50");

                    // Ponteiro
                    const angleRadians = Math.PI + angle;
                    ctx.beginPath();
                    ctx.moveTo(cx + (r * 0.9) * Math.cos(angleRadians), cy + (r * 0.9) * Math.sin(angleRadians));
                    ctx.lineTo(cx + 6 * Math.cos(angleRadians + Math.PI / 2), cy + 6 * Math.sin(angleRadians + Math.PI / 2));
                    ctx.lineTo(cx + 6 * Math.cos(angleRadians - Math.PI / 2), cy + 6 * Math.sin(angleRadians - Math.PI / 2));
                    ctx.fillStyle = "#444";
                    ctx.fill();
                  }}
                }}]
              }});
            }}

            // Inicializar gráficos
            setTimeout(() => {{
              renderGauge("gaugeChart_consolidado", {js_score_consolidado});
              renderGauge("gaugeChart_dist", {js_score_dist});
              renderGauge("gaugeChart_health", {js_score_health});
            }}, 500);
          </script>
        </body>
        </html>
        """
        
        # Extrair dados para substituição
        score_consolidado = int(dados.get("score_consolidado", 0) * 10)
        classificacao_consolidada = dados.get("classificacao_consolidada", "N/A")
        
        indicadores = dados.get("indicadores", {})
        dist_data = indicadores.get("Dist_Liquidacao", {})
        health_data = indicadores.get("Health_Factor", {})
        
        # Substituir valores no template
        html = html_template.format(
            score_consolidado=score_consolidado,
            classificacao_consolidada=classificacao_consolidada,
            js_score_consolidado=score_consolidado,
            
            score_dist=int(dist_data.get("score", 0) * 10),
            classificacao_dist=dist_data.get("classificacao", "N/A"),
            js_score_dist=int(dist_data.get("score", 0) * 10),
            valor_dist=dist_data.get("valor", "N/A"),
            peso_dist=dist_data.get("peso", "N/A"),
            
            score_health=int(health_data.get("score", 0) * 10),
            classificacao_health=health_data.get("classificacao", "N/A"),
            js_score_health=int(health_data.get("score", 0) * 10),
            valor_health=health_data.get("valor", "N/A"),
            peso_health=health_data.get("peso", "N/A")
        )
        
        return html
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar dashboard riscos: {str(e)}")

@router.get("/", response_class=HTMLResponse)
async def dashboard_index():
    """Página inicial dos dashboards"""
    return """
    <html>
    <head>
        <title>BTC Turbo - Dashboards</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #0f111a; color: white; }
            h1 { color: #f7931a; }
            .dashboard-links { display: flex; flex-wrap: wrap; gap: 20px; margin-top: 30px; }
            .dashboard-link { 
                background: #161b22; 
                padding: 20px; 
                border-radius: 8px; 
                text-decoration: none; 
                color: white;
                min-width: 200px;
                text-align: center;
                transition: background 0.3s;
            }
            .dashboard-link:hover { background: #1e1e1e; }
            .status { color: #4caf50; }
        </style>
    </head>
    <body>
        <h1>🚀 BTC Turbo - Dashboards</h1>
        <p>Sistema funcionando sem N8N!</p>
        
        <div class="dashboard-links">
            <a href="/dashboard/riscos" class="dashboard-link">
                <h3>📊 Riscos</h3>
                <p class="status">✅ Funcionando</p>
            </a>
        </div>
        
        <div style="margin-top: 40px;">
            <a href="/docs" style="color: #f7931a;">📋 Ver APIs</a> | 
            <a href="/ping" style="color: #f7931a;">🏥 Health Check</a>
        </div>
    </body>
    </html>
    """