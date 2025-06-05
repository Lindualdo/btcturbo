// ==========================================
// BTC TURBO - DASHBOARD JS SIMPLES v1.0.21
// ==========================================

const API_URL = '/api/v1/analise-btc';

// CARREGAR DADOS DA API
async function carregarDados() {
    try {
        updateStatus('🔄 Carregando dados...');
        
        // Buscar dados da API
        const response = await fetch(API_URL);
        const dados = await response.json();
        
        console.log('📊 Dados recebidos:', dados);
        
        if (dados.error) {
            throw new Error(dados.erro || 'Erro na API');
        }
        
        // EXIBIR DADOS (sem calcular nada)
        exibirDados(dados);
        
    } catch (error) {
        console.error('❌ Erro:', error);
        updateStatus('❌ Erro: ' + error.message);
    }
}

// EXIBIR DADOS NO HTML
function exibirDados(dados) {
    console.log('🖥️ Exibindo dados...');
    
    // 1. SCORE GERAL (direto da API)
    const scoreGeral = Math.round(dados.score_final * 10);
    const classificacaoGeral = dados.classificacao;
    exibirGrafico('geral', scoreGeral, classificacaoGeral);
    
    // 2. BLOCOS INDIVIDUAIS (direto da API)
    const blocos = dados.blocos || {};
    
    for (const [nome, dadosBloco] of Object.entries(blocos)) {
        if (dadosBloco && dadosBloco.score_consolidado !== undefined) {
            const score = Math.round(dadosBloco.score_consolidado * 10);
            const classificacao = dadosBloco.classificacao_consolidada;
            
            // Mapear nome da API para ID do gráfico
            let graficoId = nome;
            if (nome === 'tecnicos') graficoId = 'tecnico';
            if (nome === 'ciclo') graficoId = 'ciclos';
            if (nome === 'risco') graficoId = 'riscos';
            
            exibirGrafico(graficoId, score, classificacao);
            console.log(`✅ ${graficoId}: ${score} (${classificacao})`);
        }
    }
    
    // 3. STATUS E INFORMAÇÕES
    updateStatus('✅ Dados carregados - Score: ' + scoreGeral);
    
    // 4. ATUALIZAR SUBTITLE
    const subtitle = document.getElementById('subtitle');
    if (subtitle && dados.kelly && dados.acao) {
        subtitle.textContent = `Sistema v1.0.21 - Kelly: ${dados.kelly} | ${dados.acao}`;
    }
}

// EXIBIR GRÁFICO
function exibirGrafico(id, score, classificacao) {
    // Atualizar texto
    const textElement = document.getElementById('classificacao_' + id);
    if (textElement) {
        textElement.textContent = `Score: ${score} - ${classificacao}`;
        textElement.classList.remove('loading');
    }
    
    // Renderizar gráfico gauge
    renderizarGauge('gaugeChart_' + id, score);
}

// FORÇAR ATUALIZAÇÃO
async function forcarUpdate() {
    try {
        const btn = document.getElementById('btnForceUpdate');
        btn.disabled = true;
        btn.innerHTML = '⏳ Atualizando...';
        
        const response = await fetch(API_URL + '?force_update=true');
        const dados = await response.json();
        
        if (dados.error) throw new Error(dados.erro);
        
        exibirDados(dados);
        
        btn.disabled = false;
        btn.innerHTML = '🔄 Atualizar Dados';
        
    } catch (error) {
        console.error('❌ Erro:', error);
        document.getElementById('btnForceUpdate').innerHTML = '❌ Erro';
        setTimeout(() => {
            document.getElementById('btnForceUpdate').innerHTML = '🔄 Atualizar Dados';
            document.getElementById('btnForceUpdate').disabled = false;
        }, 3000);
    }
}

// HELPERS
function updateStatus(message) {
    const el = document.getElementById('statusInfo');
    if (el) el.innerHTML = '<strong>' + message + '</strong>';
}

// RENDERIZAR GRÁFICO GAUGE
function renderizarGauge(canvasId, score) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
        console.warn('Canvas não encontrado:', canvasId);
        return;
    }
    
    const ctx = canvas.getContext('2d');
    
    // Destruir gráfico anterior se existir
    const existingChart = Chart.getChart(canvas);
    if (existingChart) existingChart.destroy();

    try {
        new Chart(ctx, {
            type: 'doughnut',
            data: { 
                datasets: [{ 
                    data: [100], 
                    backgroundColor: ['transparent'], 
                    borderWidth: 0, 
                    cutout: '80%' 
                }] 
            },
            options: {
                responsive: false,
                rotation: -Math.PI,
                circumference: Math.PI,
                plugins: { 
                    tooltip: { enabled: false }, 
                    legend: { display: false } 
                }
            },
            plugins: [{
                afterDraw: function(chart) {
                    drawGaugeChart(chart.ctx, chart.width, chart.height, score);
                }
            }]
        });
        
        console.log(`✅ Gráfico ${canvasId} renderizado: ${score}`);
    } catch (error) {
        console.error('❌ Erro ao renderizar gráfico:', canvasId, error);
    }
}

// DESENHAR GRÁFICO GAUGE
function drawGaugeChart(ctx, width, height, score) {
    const cx = width / 2;
    const cy = height - 42;
    const radius = width / 2.4;
    const angle = (score / 100) * Math.PI;

    ctx.save();

    // Desenhar arcos coloridos de fundo
    function desenharArco(inicio, fim, cor) {
        ctx.beginPath();
        ctx.arc(cx, cy, radius, inicio, fim);
        ctx.strokeStyle = cor;
        ctx.lineWidth = 16;
        ctx.stroke();
    }

    desenharArco(Math.PI, Math.PI * 1.2, "#e53935");
    desenharArco(Math.PI * 1.2, Math.PI * 1.4, "#f57c00");
    desenharArco(Math.PI * 1.4, Math.PI * 1.6, "#fbc02d");
    desenharArco(Math.PI * 1.6, Math.PI * 1.8, "#9acb82");
    desenharArco(Math.PI * 1.8, Math.PI * 2, "#4caf50");

    // Desenhar ponteiro
    const ponteiroAngulo = Math.PI + angle;
    const ponteiroTamanho = radius * 0.9;
    
    ctx.beginPath();
    ctx.moveTo(
        cx + ponteiroTamanho * Math.cos(ponteiroAngulo),
        cy + ponteiroTamanho * Math.sin(ponteiroAngulo)
    );
    ctx.lineTo(
        cx + 6 * Math.cos(ponteiroAngulo + Math.PI / 2),
        cy + 6 * Math.sin(ponteiroAngulo + Math.PI / 2)
    );
    ctx.lineTo(
        cx + 6 * Math.cos(ponteiroAngulo - Math.PI / 2),
        cy + 6 * Math.sin(ponteiroAngulo - Math.PI / 2)
    );
    ctx.fillStyle = "#444";
    ctx.fill();

    // Centro do ponteiro
    ctx.beginPath();
    ctx.arc(cx, cy, 6, 0, 2 * Math.PI);
    ctx.fillStyle = "#888";
    ctx.fill();

    ctx.restore();
}

// INICIALIZAR QUANDO DOM CARREGAR
function inicializar() {
    console.log('🚀 Dashboard Ultra Simples iniciando...');
    
    // Verificar se Chart.js carregou
    if (typeof Chart === 'undefined') {
        console.log('⏳ Aguardando Chart.js...');
        setTimeout(inicializar, 100);
        return;
    }
    
    console.log('✅ Chart.js carregado, buscando dados...');
    carregarDados();
}

// AUTO-INICIALIZAR
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', inicializar);
} else {
    inicializar();
}