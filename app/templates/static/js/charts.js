// ==========================================
// BTC TURBO - CHARTS.JS v1.0.21
// Chart.js Gauge Rendering
// ==========================================

function renderGauge(canvasId, score) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
        console.warn('Canvas não encontrado:', canvasId);
        return;
    }
    
    const ctx = canvas.getContext('2d');
    
    // Destruir gráfico existente se houver
    const existingChart = Chart.getChart(canvas);
    if (existingChart) {
        existingChart.destroy();
    }

    try {
        new Chart(ctx, {
            type: 'doughnut',
            data: { 
                datasets: [{ 
                    data: [100], 
                    backgroundColor: ['#0000'], 
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
                afterDraw: (chart) => {
                    drawGaugeElements(chart, score);
                }
            }]
        });
    } catch (error) { 
        console.error('Erro ao renderizar gráfico:', canvasId, error); 
    }
}

function drawGaugeElements(chart, score) {
    const ctx = chart.ctx;
    const angle = (score / 100) * Math.PI;
    const cx = chart.width / 2;
    const cy = chart.height - 42;
    const r = chart.width / 2.4;

    ctx.save();

    // Desenhar arcos coloridos de fundo
    drawGaugeArcs(ctx, cx, cy, r);
    
    // Desenhar ponteiro
    drawGaugePointer(ctx, cx, cy, r, angle);
    
    // Desenhar centro
    drawGaugeCenter(ctx, cx, cy);

    ctx.restore();
}

function drawGaugeArcs(ctx, cx, cy, r) {
    const lineWidth = 16;
    
    const arcs = [
        { start: 0, end: 0.2, color: "#e53935" },      // Crítico (0-20)
        { start: 0.2, end: 0.4, color: "#f57c00" },    // Ruim (20-40)
        { start: 0.4, end: 0.6, color: "#fbc02d" },    // Neutro (40-60)
        { start: 0.6, end: 0.8, color: "#9acb82" },    // Bom (60-80)
        { start: 0.8, end: 1.0, color: "#4caf50" }     // Ótimo (80-100)
    ];
    
    arcs.forEach(arc => {
        const startAngle = Math.PI + (arc.start * Math.PI);
        const endAngle = Math.PI + (arc.end * Math.PI);
        
        ctx.beginPath();
        ctx.arc(cx, cy, r, startAngle, endAngle);
        ctx.strokeStyle = arc.color;
        ctx.lineWidth = lineWidth;
        ctx.stroke();
    });
}

function drawGaugePointer(ctx, cx, cy, r, angle) {
    const angleRadians = Math.PI + angle;
    const pointerLength = r * 0.9;
    const pointerWidth = 6;
    
    // Calcular pontos do ponteiro
    const tipX = cx + pointerLength * Math.cos(angleRadians);
    const tipY = cy + pointerLength * Math.sin(angleRadians);
    
    const base1X = cx + pointerWidth * Math.cos(angleRadians + Math.PI / 2);
    const base1Y = cy + pointerWidth * Math.sin(angleRadians + Math.PI / 2);
    
    const base2X = cx + pointerWidth * Math.cos(angleRadians - Math.PI / 2);
    const base2Y = cy + pointerWidth * Math.sin(angleRadians - Math.PI / 2);
    
    // Desenhar ponteiro
    ctx.beginPath();
    ctx.moveTo(tipX, tipY);
    ctx.lineTo(base1X, base1Y);
    ctx.lineTo(base2X, base2Y);
    ctx.closePath();
    ctx.fillStyle = "#444";
    ctx.fill();
}

function drawGaugeCenter(ctx, cx, cy) {
    // Círculo central
    ctx.beginPath();
    ctx.arc(cx, cy, 6, 0, 2 * Math.PI);
    ctx.fillStyle = "#888";
    ctx.fill();
}

// ==========================================
// CHART UTILITIES
// ==========================================

function getScoreColor(score) {
    if (score >= 80) return "#4caf50";      // Verde - Ótimo
    if (score >= 60) return "#9acb82";      // Verde claro - Bom  
    if (score >= 40) return "#fbc02d";      // Amarelo - Neutro
    if (score >= 20) return "#f57c00";      // Laranja - Ruim
    return "#e53935";                       // Vermelho - Crítico
}

function validateScore(score) {
    // Garantir que score está entre 0-100
    if (typeof score !== 'number' || isNaN(score)) {
        console.warn('Score inválido:', score, '- usando 0');
        return 0;
    }
    
    return Math.max(0, Math.min(100, score));
}

// ==========================================
// CHART INITIALIZATION HELPERS
// ==========================================

function initAllCharts() {
    // Inicializar todos os gráficos com score 0
    const chartIds = ['geral', 'tecnico', 'ciclos', 'momentum', 'riscos'];
    
    chartIds.forEach(id => {
        const canvasId = 'gaugeChart_' + id;
        if (document.getElementById(canvasId)) {
            renderGauge(canvasId, 0);
        }
    });
}

function destroyAllCharts() {
    // Destruir todos os gráficos Chart.js na página
    Chart.helpers.each(Chart.instances, (instance) => {
        instance.destroy();
    });
}

// ==========================================
// RESPONSIVE CHART HANDLING
// ==========================================

function handleChartResize() {
    // Re-renderizar gráficos quando janela redimensionar
    window.addEventListener('resize', debounce(() => {
        Chart.helpers.each(Chart.instances, (instance) => {
            instance.resize();
        });
    }, 250));
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Inicializar manipuladores quando DOM carregar
document.addEventListener('DOMContentLoaded', function() {
    handleChartResize();
});