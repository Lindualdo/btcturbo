// ==========================================
// BTC TURBO - DASHBOARD CORE v1.0.21
// JavaScript consolidado e unificado
// ==========================================

class DashboardCore {
    constructor(apiEndpoint = '/api/v1/analise-btc') {
        this.API_URL = apiEndpoint;
        this.gauges = new Map();
        this.isInitialized = false;
    }

    // ==========================================
    // INICIALIZAÇÃO
    // ==========================================

    async init() {
        console.log('🚀 Dashboard Core iniciando...');
        
        // Verificar se Chart.js carregou
        if (typeof Chart === 'undefined') {
            console.log('⏳ Aguardando Chart.js...');
            setTimeout(() => this.init(), 100);
            return;
        }
        
        console.log('✅ Chart.js carregado');
        this.isInitialized = true;
        
        // Carregar dados automaticamente
        await this.carregarDados();
    }

    // ==========================================
    // CARREGAMENTO DE DADOS
    // ==========================================

    async carregarDados(forceUpdate = false) {
        try {
            this.updateStatus('🔄 Carregando dados...');
            
            const url = forceUpdate ? `${this.API_URL}?force_update=true` : this.API_URL;
            const response = await fetch(url);
            const dados = await response.json();
            
            console.log('📊 Dados recebidos:', dados);
            
            if (dados.error) {
                throw new Error(dados.erro || 'Erro na API');
            }
            
            this.exibirDados(dados);
            
        } catch (error) {
            console.error('❌ Erro:', error);
            this.updateStatus('❌ Erro: ' + error.message);
        }
    }

    // ==========================================
    // EXIBIÇÃO DE DADOS
    // ==========================================

    exibirDados(dados) {
        console.log('🖥️ Exibindo dados...');
        
        // 1. SCORE GERAL (direto da API)
        const scoreGeral = Math.round(dados.score_final * 10);
        const classificacaoGeral = dados.classificacao;
        this.exibirGrafico('geral', scoreGeral, classificacaoGeral);
        
        // 2. BLOCOS INDIVIDUAIS (direto da API)
        const blocos = dados.blocos || {};
        
        for (const [nome, dadosBloco] of Object.entries(blocos)) {
            if (dadosBloco && dadosBloco.score_consolidado !== undefined) {
                const score = Math.round(dadosBloco.score_consolidado * 10);
                const classificacao = dadosBloco.classificacao_consolidada;
                
                // Mapear nome da API para ID do gráfico
                let graficoId = this.mapearNomeBloco(nome);
                
                this.exibirGrafico(graficoId, score, classificacao);
                console.log(`✅ ${graficoId}: ${score} (${classificacao})`);
            }
        }
        
        // 3. STATUS E INFORMAÇÕES
        this.updateStatus('✅ Dados carregados - Score: ' + scoreGeral);
        
        // 4. ATUALIZAR SUBTITLE
        this.updateSubtitle(dados);
    }

    mapearNomeBloco(nome) {
        const mapeamento = {
            'tecnicos': 'tecnico',
            'ciclo': 'ciclos',
            'risco': 'riscos'
        };
        return mapeamento[nome] || nome;
    }

    exibirGrafico(id, score, classificacao) {
        // Atualizar texto
        const textElement = document.getElementById('classificacao_' + id);
        if (textElement) {
            textElement.textContent = `Score: ${score} - ${classificacao}`;
            textElement.classList.remove('loading');
        }
        
        // Renderizar gráfico gauge
        this.renderizarGauge('gaugeChart_' + id, score);
    }

    // ==========================================
    // RENDERIZAÇÃO DE GRÁFICOS
    // ==========================================

    renderizarGauge(canvasId, score) {
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
                    afterDraw: (chart) => {
                        this.drawGaugeElements(chart.ctx, chart.width, chart.height, score);
                    }
                }]
            });
            
            console.log(`✅ Gráfico ${canvasId} renderizado: ${score}`);
        } catch (error) {
            console.error('❌ Erro ao renderizar gráfico:', canvasId, error);
        }
    }

    drawGaugeElements(ctx, width, height, score) {
        const cx = width / 2;
        const cy = height - 42;
        const radius = width / 2.4;
        const angle = (score / 100) * Math.PI;

        ctx.save();

        // Desenhar arcos coloridos de fundo
        this.drawGaugeArcs(ctx, cx, cy, radius);
        
        // Desenhar ponteiro
        this.drawGaugePointer(ctx, cx, cy, radius, angle);
        
        // Desenhar centro
        this.drawGaugeCenter(ctx, cx, cy);

        ctx.restore();
    }

    drawGaugeArcs(ctx, cx, cy, radius) {
        const arcs = [
            { start: Math.PI, end: Math.PI * 1.2, color: "#e53935" },      // Crítico
            { start: Math.PI * 1.2, end: Math.PI * 1.4, color: "#f57c00" }, // Ruim
            { start: Math.PI * 1.4, end: Math.PI * 1.6, color: "#fbc02d" }, // Neutro
            { start: Math.PI * 1.6, end: Math.PI * 1.8, color: "#9acb82" }, // Bom
            { start: Math.PI * 1.8, end: Math.PI * 2, color: "#4caf50" }    // Ótimo
        ];
        
        arcs.forEach(arc => {
            ctx.beginPath();
            ctx.arc(cx, cy, radius, arc.start, arc.end);
            ctx.strokeStyle = arc.color;
            ctx.lineWidth = 16;
            ctx.stroke();
        });
    }

    drawGaugePointer(ctx, cx, cy, radius, angle) {
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
    }

    drawGaugeCenter(ctx, cx, cy) {
        ctx.beginPath();
        ctx.arc(cx, cy, 6, 0, 2 * Math.PI);
        ctx.fillStyle = "#888";
        ctx.fill();
    }

    // ==========================================
    // UTILITÁRIOS
    // ==========================================

    updateStatus(message) {
        const el = document.getElementById('statusInfo');
        if (el) el.innerHTML = '<strong>' + message + '</strong>';
    }

    updateSubtitle(dados) {
        const subtitle = document.getElementById('subtitle');
        if (subtitle && dados.kelly && dados.acao) {
            subtitle.textContent = `Sistema v1.0.21 - Kelly: ${dados.kelly} | ${dados.acao}`;
        }
    }

    // ==========================================
    // AÇÕES PÚBLICAS
    // ==========================================

    async forcarUpdate() {
        try {
            const btn = document.getElementById('btnForceUpdate');
            if (btn) {
                btn.disabled = true;
                btn.innerHTML = '⏳ Atualizando...';
            }
            
            await this.carregarDados(true);
            
            if (btn) {
                btn.disabled = false;
                btn.innerHTML = '🔄 Atualizar Dados';
            }
            
        } catch (error) {
            console.error('❌ Erro no force update:', error);
            const btn = document.getElementById('btnForceUpdate');
            if (btn) {
                btn.innerHTML = '❌ Erro';
                setTimeout(() => {
                    btn.innerHTML = '🔄 Atualizar Dados';
                    btn.disabled = false;
                }, 3000);
            }
        }
    }
}

// ==========================================
// INSTÂNCIA GLOBAL E AUTO-INICIALIZAÇÃO
// ==========================================

let dashboardCore = null;

function initDashboard() {
    if (!dashboardCore) {
        dashboardCore = new DashboardCore();
    }
    dashboardCore.init();
}

// Funções globais para compatibilidade com template
function carregarDados() {
    if (dashboardCore) {
        return dashboardCore.carregarDados();
    }
}

function forcarUpdate() {
    if (dashboardCore) {
        return dashboardCore.forcarUpdate();
    }
}

// Auto-inicializar
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initDashboard);
} else {
    initDashboard();
}