-- ==========================================
-- DECISÃO ESTRATÉGICA - BTC TURBO v1.9
-- ==========================================


-- 1. TABELA MATRIZ ESTRATÉGICA (15 cenários)
DROP TABLE IF EXISTS matriz_estrategica CASCADE;

CREATE TABLE matriz_estrategica (
    id SERIAL PRIMARY KEY,
    
    -- Ranges de entrada
    score_tendencia_min INTEGER NOT NULL,
    score_tendencia_max INTEGER NOT NULL,
    score_ciclo_min INTEGER NOT NULL,
    score_ciclo_max INTEGER NOT NULL,
    
    -- Decisão estratégica
    fase_operacional VARCHAR(50) NOT NULL,
    alavancagem DECIMAL(3,1) NOT NULL,
    satelite DECIMAL(4,3) NOT NULL,
    acao VARCHAR(100) NOT NULL,
    tendencia VARCHAR(10) NOT NULL,
    
    -- Metadados
    created_at TIMESTAMP DEFAULT NOW(),
    ativo BOOLEAN DEFAULT true,
    
    -- Constraints
    CONSTRAINT chk_score_tend_min CHECK (score_tendencia_min >= 0 AND score_tendencia_min <= 100),
    CONSTRAINT chk_score_tend_max CHECK (score_tendencia_max >= 0 AND score_tendencia_max <= 100),
    CONSTRAINT chk_score_ciclo_min CHECK (score_ciclo_min >= 0 AND score_ciclo_min <= 100),
    CONSTRAINT chk_score_ciclo_max CHECK (score_ciclo_max >= 0 AND score_ciclo_max <= 100),
    CONSTRAINT chk_alavancagem CHECK (alavancagem >= 0 AND alavancagem <= 5),
    CONSTRAINT chk_satelite CHECK (satelite >= 0 AND satelite <= 1),
    CONSTRAINT chk_tendencia CHECK (tendencia IN ('BULL', 'BEAR', 'NEUTRO'))
);

-- 2. TABELA HISTÓRICO DECISÕES
DROP TABLE IF EXISTS decisao_estrategica CASCADE;

CREATE TABLE decisao_estrategica (
    id SERIAL PRIMARY KEY,
    
    -- Scores de entrada
    score_tendencia INTEGER NOT NULL,
    score_ciclo INTEGER NOT NULL,
    
    -- Decisão aplicada
    matriz_id INTEGER REFERENCES matriz_estrategica(id),
    fase_operacional VARCHAR(50) NOT NULL,
    alavancagem DECIMAL(3,1) NOT NULL,
    satelite DECIMAL(4,3) NOT NULL,
    acao VARCHAR(100) NOT NULL,
    tendencia VARCHAR(10) NOT NULL,
    
    -- Dados completos para auditoria
    json_emas JSONB,
    json_ciclo JSONB,
    
    -- Metadados
    timestamp TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT chk_decisao_tend CHECK (score_tendencia >= 0 AND score_tendencia <= 100),
    CONSTRAINT chk_decisao_ciclo CHECK (score_ciclo >= 0 AND score_ciclo <= 100)
);

-- 3. CARGA DA MATRIZ (15 cenários conforme documentação)
INSERT INTO matriz_estrategica (
    score_tendencia_min, score_tendencia_max, 
    score_ciclo_min, score_ciclo_max,
    fase_operacional, alavancagem, satelite, acao, tendencia
) VALUES
-- BULL (88-100)
(88, 100, 80, 100, 'Bull Aceleração', 3.0, 1.000, 'Hold + RPs Agendados', 'BULL'),
(88, 100, 60, 79, 'Bull Maduro', 2.0, 1.000, 'Hold', 'BULL'),
(88, 100, 0, 59, 'Bull Exaustão', 1.0, 0.800, 'Preparar RPs', 'BULL'),

-- BULL CONSOLIDAÇÃO (66-87)
(66, 87, 80, 100, 'Bull Inicial', 2.0, 0.900, 'Acumular Agressivo', 'BULL'),
(66, 87, 60, 79, 'Bull Consolidação', 1.0, 0.700, 'Acumular Gradual', 'BULL'),
(66, 87, 0, 59, 'Distribuição', 0.0, 0.500, 'Reduzir Exposição', 'NEUTRO'),

-- NEUTRO/TRANSIÇÃO (35-65)
(35, 65, 80, 100, 'Acumulação', 1.0, 0.500, 'Testar Mercado', 'NEUTRO'),
(35, 65, 60, 79, 'Equilíbrio', 0.0, 0.300, 'Wait & Watch', 'NEUTRO'),
(35, 65, 0, 59, 'Distribuição', 0.0, 0.100, 'Zerar Alavancagem', 'NEUTRO'),

-- BEAR DISTRIBUIÇÃO (13-34)
(13, 34, 80, 100, 'Bear Final', 1.0, 0.500, 'Hedge Long', 'BEAR'),
(13, 34, 60, 79, 'Bear Maduro', 0.0, 0.000, 'Exit Leverage', 'BEAR'),
(13, 34, 0, 59, 'Bear Início', 1.0, 0.200, 'Hedge Short', 'BEAR'),

-- BEAR CAPITULAÇÃO (0-12)
(0, 12, 80, 100, 'Bear Capitulação', 3.0, 1.000, 'Aporte Agressivo', 'BEAR'),
(0, 12, 60, 79, 'Bear Capitulação', 2.0, 0.700, 'Aporte Gradual (DCA)', 'BEAR'),
(0, 12, 0, 59, 'Bear Risco', 1.0, 0.500, 'Aporte Básico', 'BEAR');

-- 4. ÍNDICES PARA PERFORMANCE
CREATE INDEX idx_matriz_scores ON matriz_estrategica (score_tendencia_min, score_tendencia_max, score_ciclo_min, score_ciclo_max);
CREATE INDEX idx_decisao_timestamp ON decisao_estrategica (timestamp DESC);

-- 5. VERIFICAÇÃO
SELECT 
    CONCAT(score_tendencia_min, '-', score_tendencia_max) as tendencia_range,
    CONCAT(score_ciclo_min, '-', score_ciclo_max) as ciclo_range,
    fase_operacional,
    CONCAT(alavancagem, 'x') as leverage,
    CONCAT(ROUND(satelite * 100), '%') as satelite_pct,
    tendencia
FROM matriz_estrategica 
ORDER BY score_tendencia_min DESC, score_ciclo_min DESC;