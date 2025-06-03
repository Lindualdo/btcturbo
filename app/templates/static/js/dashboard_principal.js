// ==========================================
// BTC TURBO - DASHBOARD PRINCIPAL JS v1.0.21
// ==========================================

// Variáveis globais
let dadosAtuais = null;
let CONFIG = null;

// ==========================================
// INICIALIZAÇÃO
// ==========================================

function initDashboard(config) {
    CONFIG = config;
    console.log('🚀 Iniciando Dashboard v' + CONFIG.versao);
    
    // Aguardar Chart.js carregar
    if (typeof Chart === 'undefined') {
        setTimeout(() => initDashboard(config), 100);
        return;
    }
    
    // Buscar dados iniciais
    buscarDados(false);
}

// ==========================================
// API INTEGRATION
// ==========================================

async function buscarDados(aplicarReducaoRisco = false) {
    try {
        updateStatus('🔄 Buscando dados...', 'info');
        
        const response = await fetch(CONFIG.api_endpoint + '?incluir_risco=false&force_update=false');
        const dados = await response.json();
        
        if (dados.error || dados.status === 'error') {
            throw new Error(dados.erro || 'Erro na API');
        }
        
        dadosAtuais = dados;
        
        // Calcular score com novos pesos v1.0.21
        const scoreRecalculado = calcularScoreComNovosPesos(dados, aplicarReducaoRisco);
        atualizarInterface(scoreRecalculado);
        
    } catch (error) {
        console.error('❌ Erro ao buscar dados:', error);
        mostrarErro(error.message);
    }
}

async function buscarDadosComForce(aplicarReducaoRisco = false) {
    try {
        updateStatus('⏳ Forçando atualização...', 'info');
        disableButton('btnForceUpdate', '⏳ Atualizando...');
        
        const response = await fetch(CONFIG.api_endpoint + '?incluir_risco=false&force_update=true');
        const dados = await response.json();
        
        if (dados.error || dados.status === 'error') {
            throw new Error(dados.erro || 'Erro na API');
        }
        
        dadosAtuais = dados;
        const scoreRecalculado = calcularScoreComNovosPesos(dados, aplicarReducaoRisco);
        atualizarInterface(scoreRecalculado);
        
        enableButton('btnForceUpdate', '🔄 Atualizar Dados');
        
    } catch (error) {
        console.error('❌ Erro ao forçar atualização:', error);
        mostrarErro(error.message);
        enableButton('btnForceUpdate', '❌ Erro - Tentar Novamente');
        
        setTimeout(() => {
            enableButton('btnForceUpdate', '🔄 Atualizar Dados');
        }, 3000);
    }
}

// ==========================================
// CÁLCULOS E PROCESSAMENTO
// ==========================================

function calcularScoreComNovosPesos(dados, aplicarReducaoRisco) {
    const blocos = dados.blocos || {};
    
    let scoreTotal = 0;
    let pesoTotal = 0;
    
    // Aplicar novos pesos v1.0.21
    for (const [nomeBloco, peso] of Object.entries(CONFIG.novos_pesos)) {
        if (peso > 0 && blocos[nomeBloco]) {
            const scoreBloco = blocos[nomeBloco].score || 0;
            const pesoDecimal = peso / 100; // Converter % para decimal
            scoreTotal += scoreBloco * pesoDecimal;
            pesoTotal += pesoDecimal;
        }
    }
    
    let scoreFinal = pesoTotal > 0 ? scoreTotal : 0;
    
    // Aplicar redução por risco se habilitada
    let modificadorRisco = 1.0;
    if (aplicarReducaoRisco && blocos.riscos) {
        const scoreRisco = blocos.riscos.score || 10;
        // Fórmula: redução maior quando risco for menor
        modificadorRisco = Math.max(0.7, Math.min(1.0, scoreRisco / 10));
        scoreFinal *= modificadorRisco;
    }
    
    return {
        ...dados,
        score_final: scoreFinal,
        score_original: scoreTotal,
        modificador_risco: modificadorRisco,
        pesos_aplicados: CONFIG.novos_pesos,
        reducao_risco_ativa: aplicarReducaoRisco
    };
}

// ==========================================
// INTERFACE UPDATES
// ==========================================

function atualizarInterface(dados) {
    // Atualizar subtitle
    const kelly = calcularKelly(dados.score_final);
    const acao = determinarAcao(dados.score_final);
    updateSubtitle('Sistema v' + CONFIG.versao + ' - Kelly: ' + kelly + ' | ' + acao);
    
    // Atualizar toggle status
    updateToggleStatus(dados);
    
    // Atualizar scores
    updateScoreGeral(dados);
    updateBlocos(dados);
}

function updateScoreGeral(dados) {
    const scoreGeral = Math.round(dados.score_final * 10);
    const classificacaoGeral = classificarScore(dados.score_final);
    atualizarGrafico('geral', scoreGeral, classificacaoGeral);
}

function updateBlocos(dados) {
    const blocos = dados.blocos || {};
    
    // Atualizar cada bloco
    for (const [nome, peso] of Object.entries(CONFIG.novos_pesos)) {
        const dadosBloco = blocos[nome] || { score: 0, classificacao: 'N/A' };
        const score = Math.round((dadosBloco.score || 0) * 10);
        const classificacao = dadosBloco.classificacao || 'N/A';
        
        atualizarGrafico(nome, score, classificacao);
        updatePeso(nome, peso);
    }
}

function updateToggleStatus(dados) {
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
}

function atualizarGrafico(id, score, classificacao) {
    // Atualizar texto
    const element = document.getElementById('classificacao_' + id);
    if (element) {
        element.textContent = 'Score: ' + score + ' - ' + classificacao;
        element.classList.remove('loading', 'error');
    }
    
    // Renderizar gráfico
    renderGauge('gaugeChart_' + id, score);
}

function updatePeso(nome, peso) {
    const pesoElement = document.getElementById('peso_' + nome);
    if (pesoElement) {
        pesoElement.textContent = 'Peso: ' + peso + '%';
        pesoElement.style.color = peso > 0 ? '#f7931a' : '#666';
    }
}

// ==========================================
// HELPERS E UTILITÁRIOS
// ==========================================

function classificarScore(score) {
    if (score >= 8.0) return "ótimo";
    if (score >= 6.0) return "bom";
    if (score >= 4.0) return "neutro";
    if (score >= 2.0) return "ruim";
    return "crítico";
}

function calcularKelly(score) {
    if (score >= 8.0) return "75%";
    if (score >= 6.0) return "50%";
    if (score >= 4.0) return "25%";
    if (score >= 2.0) return "10%";
    return "0%";
}

function determinarAcao(score) {
    if (score >= 8.0) return "Aumentar posição";
    if (score >= 6.0) return "Manter posição";
    if (score >= 4.0) return "Posição neutra";
    if (score >= 2.0) return "Reduzir exposição";
    return "Zerar alavancagem";
}

// ==========================================
// EVENT HANDLERS
// ==========================================

function atualizarDados() {
    const toggle = document.getElementById('toggleReducaoRisco');
    const aplicarReducao = toggle ? toggle.checked : false;
    buscarDados(aplicarReducao);
}

function forcarAtualizacao() {
    const toggle = document.getElementById('toggleReducaoRisco');
    const aplicarReducao = toggle ? toggle.checked : false;
    buscarDadosComForce(aplicarReducao);
}

function navegarPara(url) {
    window.location.href = url;
}

// ==========================================
// UI HELPERS
// ==========================================

function updateStatus(message, type = 'info') {
    const statusElement = document.getElementById('statusInfo');
    if (statusElement) {
        const icon = type === 'error' ? '❌' : type === 'warning' ? '⚠️' : '✅';
        statusElement.innerHTML = '<strong>' + icon + ' ' + message + '</strong>';
    }
}

function updateSubtitle(text) {
    const subtitleElement = document.getElementById('subtitle');
    if (subtitleElement) {
        subtitleElement.textContent = text;
    }
}

function disableButton(id, text) {
    const button = document.getElementById(id);
    if (button) {
        button.disabled = true;
        button.innerHTML = text;
    }
}

function enableButton(id, text) {
    const button = document.getElementById(id);
    if (button) {
        button.disabled = false;
        button.innerHTML = text;
    }
}

function mostrarErro(mensagem) {
    updateSubtitle('Erro: ' + mensagem);
    updateStatus('Erro ao carregar dados - ' + mensagem, 'error');
    
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