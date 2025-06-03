// ==========================================
// BTC TURBO - DASHBOARD JS v1.0.21
// ==========================================

const Dashboard = {
    // Variáveis globais
    dadosAtuais: null,
    config: window.DASHBOARD_CONFIG || {},

    // ==========================================
    // INICIALIZAÇÃO
    // ==========================================
    
    init() {
        console.log('🚀 Iniciando Dashboard v' + this.config.versao);
        
        // Aguardar Chart.js carregar
        if (typeof Chart === 'undefined') {
            setTimeout(() => this.init(), 100);
            return;
        }
        
        // Buscar dados iniciais
        this.buscarDados(false);
    },

    // ==========================================
    // API INTEGRATION
    // ==========================================

    async buscarDados(aplicarReducaoRisco = false) {
        try {
            UI.updateStatus('🔄 Buscando dados...', 'info');
            
            const response = await fetch(this.config.api_endpoint + '?incluir_risco=false&force_update=false');
            const dados = await response.json();
            
            if (dados.error || dados.status === 'error') {
                throw new Error(dados.erro || 'Erro na API');
            }
            
            this.dadosAtuais = dados;
            
            // Calcular score com novos pesos v1.0.21
            const scoreRecalculado = ScoreCalculator.calcularComNovosPesos(dados, aplicarReducaoRisco);
            UI.atualizarInterface(scoreRecalculado);
            
        } catch (error) {
            console.error('❌ Erro ao buscar dados:', error);
            UI.mostrarErro(error.message);
        }
    },

    async forcarAtualizacao() {
        try {
            UI.updateStatus('⏳ Forçando atualização...', 'info');
            UI.disableButton('btnForceUpdate', '⏳ Atualizando...');
            
            const response = await fetch(this.config.api_endpoint + '?incluir_risco=false&force_update=true');
            const dados = await response.json();
            
            if (dados.error || dados.status === 'error') {
                throw new Error(dados.erro || 'Erro na API');
            }
            
            this.dadosAtuais = dados;
            const scoreRecalculado = ScoreCalculator.calcularComNovosPesos(dados, false);
            UI.atualizarInterface(scoreRecalculado);
            
            UI.enableButton('btnForceUpdate', '🔄 Atualizar Dados');
            
        } catch (error) {
            console.error('❌ Erro ao forçar atualização:', error);
            UI.mostrarErro(error.message);
            UI.enableButton('btnForceUpdate', '❌ Erro - Tentar Novamente');
            
            setTimeout(() => {
                UI.enableButton('btnForceUpdate', '🔄 Atualizar Dados');
            }, 3000);
        }
    },

    // ==========================================
    // EVENT HANDLERS
    // ==========================================

    atualizarDados() {
        const toggle = document.getElementById('toggleReducaoRisco');
        const aplicarReducao = toggle ? toggle.checked : false;
        this.buscarDados(aplicarReducao);
    },

    navegarPara(url) {
        window.location.href = url;
    }
};

// ==========================================
// CALCULADOR DE SCORES
// ==========================================

const ScoreCalculator = {
    calcularComNovosPesos(dados, aplicarReducaoRisco) {
        console.log('🔍 DEBUG - Dados recebidos:', dados);
        
        const blocos = dados.blocos || {};
        console.log('📊 DEBUG - Blocos disponíveis:', Object.keys(blocos));
        
        let scoreTotal = 0;
        let pesoTotal = 0;
        
        // Mapeamento correto dos nomes (API vs JavaScript)
        const mapeamentoBlocos = {
            "tecnico": ["tecnico", "tecnicos"],
            "ciclos": ["ciclos", "ciclo"],
            "momentum": ["momentum"],
            "riscos": ["riscos", "risco"]
        };
        
        // Aplicar novos pesos v1.0.21
        for (const [nomeBloco, peso] of Object.entries(Dashboard.config.novos_pesos)) {
            if (peso > 0) {
                // Buscar bloco com nome correto
                let dadosBloco = null;
                const possiveisNomes = mapeamentoBlocos[nomeBloco] || [nomeBloco];
                
                for (const nome of possiveisNomes) {
                    if (blocos[nome]) {
                        dadosBloco = blocos[nome];
                        break;
                    }
                }
                
                if (dadosBloco) {
                    const scoreBloco = dadosBloco.score_consolidado || 0;
                    const pesoDecimal = peso / 100;
                    
                    scoreTotal += scoreBloco * pesoDecimal;
                    pesoTotal += pesoDecimal;
                    
                    console.log(`✅ ${nomeBloco}: score=${scoreBloco}, peso=${peso}%`);
                } else {
                    console.warn(`⚠️ Bloco ${nomeBloco} não encontrado na API`);
                }
            }
        }
        
        let scoreFinal = pesoTotal > 0 ? scoreTotal : 0;
        
        // Aplicar redução por risco se habilitada
        let modificadorRisco = 1.0;
        if (aplicarReducaoRisco && blocos.riscos) {
            const scoreRisco = blocos.riscos.score_consolidado || 10;
            modificadorRisco = Math.max(0.7, Math.min(1.0, scoreRisco / 10));
            scoreFinal *= modificadorRisco;
        }
        
        console.log('🎯 Score calculado:', {
            scoreTotal,
            scoreFinal,
            modificadorRisco,
            aplicarReducaoRisco
        });
        
        return {
            ...dados,
            score_final: scoreFinal,
            score_original: scoreTotal,
            modificador_risco: modificadorRisco,
            pesos_aplicados: Dashboard.config.novos_pesos,
            reducao_risco_ativa: aplicarReducaoRisco
        };
    }
};

// ==========================================
// INTERFACE DE USUÁRIO
// ==========================================

const UI = {
    atualizarInterface(dados) {
        // Atualizar subtitle
        const kelly = Utils.calcularKelly(dados.score_final);
        const acao = Utils.determinarAcao(dados.score_final);
        
        const subtitleElement = document.getElementById('subtitle');
        if (subtitleElement) {
            subtitleElement.textContent = 'Sistema v' + Dashboard.config.versao + ' - Kelly: ' + kelly + ' | ' + acao;
        }
        
        // Atualizar componentes
        this.updateToggleStatus(dados);
        this.updateScoreGeral(dados);
        this.updateBlocos(dados);
    },

    updateBlocos(dados) {
        const blocos = dados.blocos || {};
        
        // Mapeamento correto dos nomes
        const mapeamentoBlocos = {
            "tecnico": ["tecnico", "tecnicos"],
            "ciclos": ["ciclos", "ciclo"], 
            "momentum": ["momentum"],
            "riscos": ["riscos", "risco"]
        };
        
        // Atualizar cada bloco
        for (const [nome, peso] of Object.entries(Dashboard.config.novos_pesos)) {
            // Buscar dados do bloco
            let dadosBloco = null;
            const possiveisNomes = mapeamentoBlocos[nome] || [nome];
            
            for (const nomeApi of possiveisNomes) {
                if (blocos[nomeApi]) {
                    dadosBloco = blocos[nomeApi];
                    break;
                }
            }
            
            if (dadosBloco) {
                const score = Math.round((dadosBloco.score_consolidado || 0) * 10);
                const classificacao = dadosBloco.classificacao_consolidada || 'N/A';
                
                this.atualizarGrafico(nome, score, classificacao);
                this.updatePeso(nome, peso);
                
                console.log(`📊 Gráfico ${nome}: score=${score}, classificacao=${classificacao}`);
            } else {
                this.atualizarGrafico(nome, 0, 'N/A');
                this.updatePeso(nome, peso);
                console.warn(`⚠️ Bloco ${nome} não encontrado, usando fallback`);
            }
        }
    },

    updateScoreGeral(dados) {
        const scoreGeral = Math.round(dados.score_final * 10);
        const classificacaoGeral = Utils.classificarScore(dados.score_final);
        this.atualizarGrafico('geral', scoreGeral, classificacaoGeral);
    },

    updateToggleStatus(dados) {
        const toggleStatus = document.getElementById('toggleStatus');
        const statusInfo = document.getElementById('statusInfo');
        const graficoRiscos = document.querySelector('.grafico[onclick*="riscos"]');
        
        if (dados.reducao_risco_ativa) {
            toggleStatus.textContent = 'Ativa';
            statusInfo.innerHTML = '<strong>⚠️ Redução por Risco ATIVA</strong> - Score reduzido em ' + 
                Math.round((1 - dados.modificador_risco) * 100) + '%';
            if (graficoRiscos) graficoRiscos.classList.add('risco-reduzido');
        } else {
            toggleStatus.textContent = 'Desabilitada';
            statusInfo.innerHTML = '<strong>✅ Score SEM redução</strong>';
            if (graficoRiscos) graficoRiscos.classList.remove('risco-reduzido');
        }
    },

    atualizarGrafico(id, score, classificacao) {
        // Atualizar texto
        const element = document.getElementById('classificacao_' + id);
        if (element) {
            element.textContent = 'Score: ' + score + ' - ' + classificacao;
            element.classList.remove('loading', 'error');
        }
        
        // Renderizar gráfico
        GaugeChart.render('gaugeChart_' + id, score);
    },

    updatePeso(nome, peso) {
        const pesoElement = document.getElementById('peso_' + nome);
        if (pesoElement) {
            pesoElement.textContent = 'Peso: ' + peso + '%';
            pesoElement.style.color = peso > 0 ? '#f7931a' : '#666';
        }
    },

    updateStatus(message, type = 'info') {
        const statusElement = document.getElementById('statusInfo');
        if (statusElement) {
            const icon = type === 'error' ? '❌' : type === 'warning' ? '⚠️' : '✅';
            statusElement.innerHTML = '<strong>' + icon + ' ' + message + '</strong>';
        }
    },

    disableButton(id, text) {
        const button = document.getElementById(id);
        if (button) {
            button.disabled = true;
            button.innerHTML = text;
        }
    },

    enableButton(id, text) {
        const button = document.getElementById(id);
        if (button) {
            button.disabled = false;
            button.innerHTML = text;
        }
    },

    mostrarErro(mensagem) {
        this.updateStatus('Erro ao carregar dados - ' + mensagem, 'error');
        
        // Marcar gráficos como erro
        ['geral', 'tecnico', 'ciclos', 'momentum', 'riscos'].forEach(id => {
            const element = document.getElementById('classificacao_' + id);
            if (element) {
                element.textContent = 'Erro ao carregar';
                element.classList.remove('loading');
                element.classList.add('error');
            }
        });
    }
};

// ==========================================
// UTILITÁRIOS
// ==========================================

const Utils = {
    classificarScore(score) {
        if (score >= 8.0) return "ótimo";
        if (score >= 6.0) return "bom";
        if (score >= 4.0) return "neutro";
        if (score >= 2.0) return "ruim";
        return "crítico";
    },

    calcularKelly(score) {
        if (score >= 8.0) return "75%";
        if (score >= 6.0) return "50%";
        if (score >= 4.0) return "25%";
        if (score >= 2.0) return "10%";
        return "0%";
    },

    determinarAcao(score) {
        if (score >= 8.0) return "Aumentar posição";
        if (score >= 6.0) return "Manter posição";
        if (score >= 4.0) return "Posição neutra";
        if (score >= 2.0) return "Reduzir exposição";
        return "Zerar alavancagem";
    }
};

// ==========================================
// GRÁFICOS GAUGE
// ==========================================

const GaugeChart = {
    render(canvasId, score) {
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
                    afterDraw: (chart) => this.drawGauge(chart, score)
                }]
            });
        } catch (error) { 
            console.error('Erro ao renderizar gráfico:', canvasId, error); 
        }
    },

    drawGauge(chart, score) {
        const ctx = chart.ctx;
        const angle = (score / 100) * Math.PI;
        const cx = chart.width / 2;
        const cy = chart.height - 42;
        const r = chart.width / 2.4;

        ctx.save();

        // Desenhar arcos coloridos
        this.drawArc(ctx, cx, cy, r, Math.PI, Math.PI + Math.PI * 0.2, "#e53935");
        this.drawArc(ctx, cx, cy, r, Math.PI + Math.PI * 0.2, Math.PI + Math.PI * 0.4, "#f57c00");
        this.drawArc(ctx, cx, cy, r, Math.PI + Math.PI * 0.4, Math.PI + Math.PI * 0.6, "#fbc02d");
        this.drawArc(ctx, cx, cy, r, Math.PI + Math.PI * 0.6, Math.PI + Math.PI * 0.8, "#9acb82");
        this.drawArc(ctx, cx, cy, r, Math.PI + Math.PI * 0.8, 2 * Math.PI, "#4caf50");

        // Desenhar ponteiro
        this.drawPointer(ctx, cx, cy, r, Math.PI + angle);
        
        ctx.restore();
    },

    drawArc(ctx, cx, cy, r, start, end, color) {
        ctx.beginPath(); 
        ctx.arc(cx, cy, r, start, end);
        ctx.strokeStyle = color; 
        ctx.lineWidth = 16; 
        ctx.stroke();
    },

    drawPointer(ctx, cx, cy, r, angleRadians) {
        const pointerLength = r * 0.9;
        ctx.beginPath();
        ctx.moveTo(cx + pointerLength * Math.cos(angleRadians), cy + pointerLength * Math.sin(angleRadians));
        ctx.lineTo(cx + 6 * Math.cos(angleRadians + Math.PI / 2), cy + 6 * Math.sin(angleRadians + Math.PI / 2));
        ctx.lineTo(cx + 6 * Math.cos(angleRadians - Math.PI / 2), cy + 6 * Math.sin(angleRadians - Math.PI / 2));
        ctx.fillStyle = "#444"; 
        ctx.fill();
        
        // Centro
        ctx.beginPath(); 
        ctx.arc(cx, cy, 6, 0, 2 * Math.PI);
        ctx.fillStyle = "#888"; 
        ctx.fill();
    }
};

// ==========================================
// INICIALIZAÇÃO AUTOMÁTICA
// ==========================================

// Inicializar quando DOM carregar
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => Dashboard.init());
} else { 
    Dashboard.init(); 
}