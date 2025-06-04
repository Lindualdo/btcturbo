# app/routers/dashboard_tecnico_detalhes.py - v2.1.0

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/tecnico/detalhes", response_class=HTMLResponse)
async def dashboard_tecnico_detalhes():
    """Página ultra-simplificada de detalhes técnicos - v2.1.0"""
    html = """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>BTC Turbo - Detalhes Técnicos v2.1.0</title>
      <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { background: #0f111a; color: #fff; font-family: system-ui; padding: 20px; }
        .container { max-width: 1000px; margin: 0 auto; }
        .header { margin-bottom: 30px; text-align: center; }
        .breadcrumb { font-size: 14px; color: #888; margin-bottom: 15px; }
        .breadcrumb a { color: #f7931a; text-decoration: none; }
        h1 { color: #f7931a; font-size: 28px; margin-bottom: 15px; }
        .btn-voltar { background: #f7931a; color: #000; padding: 10px 20px; border-radius: 5px; text-decoration: none; font-weight: 600; }
        
        .score-card { background: #1e1e1e; border-radius: 10px; padding: 30px; margin-bottom: 30px; text-align: center; border-left: 4px solid #f7931a; }
        .score-numero { font-size: 48px; color: #f7931a; font-weight: 800; }
        .score-texto { font-size: 20px; margin: 10px 0; }
        .btc-price { font-size: 24px; color: #4caf50; margin: 15px 0; }
        
        .section { margin-bottom: 30px; }
        .section-title { font-size: 20px; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 2px solid #333; }
        .diario { border-left: 4px solid #2196f3; }
        .semanal { border-left: 4px solid #4caf50; }
        
        table { width: 100%; background: #161b22; border-radius: 8px; overflow: hidden; }
        th { background: #333; padding: 15px; text-align: left; font-weight: 600; }
        td { padding: 15px; border-bottom: 1px solid #333; }
        tr:hover { background: #1a1a1a; }
        
        .bull { color: #4caf50; font-weight: 600; }
        .bear { color: #e53935; font-weight: 600; }
        .loading { color: #f7931a; }
      </style>
    </head>
    <body>
      <div class="container">
        <div class="header">
          <div class="breadcrumb"><a href="/dashboard/">Dashboard</a> > <a href="/dashboard/tecnico">Técnico</a> > Detalhes</div>
          <a href="/dashboard/tecnico" class="btn-voltar">← Voltar</a>
          <h1>📊 Análise Técnica Detalhada</h1>
        </div>
        
        <div class="score-card">
          <div id="scoreNumero" class="score-numero loading">...</div>
          <div id="scoreTexto" class="score-texto"></div>
          <div id="btcPrice" class="btc-price"></div>
          <div style="font-size: 14px; color: #888; margin-top: 15px;">
            <span id="timestamp">Carregando...</span>
          </div>
        </div>
        
        <div class="section diario">
          <h2 class="section-title">📊 Timeframe Diário (Peso: 30%)</h2>
          <table>
            <thead><tr><th>EMA</th><th>Valor</th><th>Distância</th></tr></thead>
            <tbody id="tabelaDiario"><tr><td colspan="3" class="loading">Carregando...</td></tr></tbody>
          </table>
        </div>
        
        <div class="section semanal">
          <h2 class="section-title">📅 Timeframe Semanal (Peso: 70%)</h2>
          <table>
            <thead><tr><th>EMA</th><th>Valor</th><th>Distância</th></tr></thead>
            <tbody id="tabelaSemanal"><tr><td colspan="3" class="loading">Carregando...</td></tr></tbody>
          </table>
        </div>
      </div>

      <script>
        async function init() {
          try {
            const response = await fetch('/api/v1/obter-indicadores/tecnico');
            const data = await response.json();
            
            if (data.status !== 'success') throw new Error('API erro');
            
            // Score principal
            const score = data.indicadores.Score_Final_Ponderado.score_numerico;
            document.getElementById('scoreNumero').textContent = Math.round(score * 10);
            document.getElementById('scoreTexto').textContent = data.indicadores.Score_Final_Ponderado.valor;
            document.getElementById('btcPrice').textContent = `BTC: ${data.indicadores.BTC_Price.valor}`;
            document.getElementById('timestamp').textContent = `Atualizado: ${new Date(data.timestamp).toLocaleTimeString()}`;
            
            // Tabela Diário
            renderTabela('tabelaDiario', data.timeframes.diario.emas, data.distancias.daily);
            
            // Tabela Semanal  
            renderTabela('tabelaSemanal', data.timeframes.semanal.emas, data.distancias.weekly);
            
          } catch (error) {
            document.getElementById('scoreNumero').textContent = 'Erro';
            console.error('Erro:', error);
          }
        }

        function renderTabela(id, emas, distancias) {
          const tabela = document.getElementById(id);
          const emasArray = ['17', '34', '144', '305', '610'];
          
          let html = '';
          emasArray.forEach(periodo => {
            const emaValor = emas[periodo];
            const distancia = distancias[`ema_${periodo}`];
            if (!emaValor || !distancia) return;
            
            const distanciaClass = distancia.startsWith('+') ? 'bull' : 'bear';
            
            html += `
              <tr>
                <td>EMA ${periodo}</td>
                <td>$${emaValor.toLocaleString()}</td>
                <td class="${distanciaClass}">${distancia}</td>
              </tr>
            `;
          });
          
          tabela.innerHTML = html;
        }

        document.addEventListener('DOMContentLoaded', init);
      </script>
    </body>
    </html>
    """
    return html