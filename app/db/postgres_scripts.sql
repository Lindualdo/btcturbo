-- ==========================================
-- BTC TURBO - SCRIPTS POSTGRESQL
-- 1 TABELA POR BLOCO
-- ==========================================

-- TABELA BLOCO CICLO
CREATE TABLE indicadores_ciclo (
    id SERIAL PRIMARY KEY,
    mvrv_z_score DECIMAL(15,6),
    realized_ratio DECIMAL(15,6), 
    puell_multiple DECIMAL(15,6),
    timestamp TIMESTAMP DEFAULT NOW(),
    fonte VARCHAR(50) DEFAULT 'Sistema',
    metadados JSONB DEFAULT '{}'
);

-- TABELA BLOCO MOMENTUM  
CREATE TABLE indicadores_momentum (
    id SERIAL PRIMARY KEY,
    rsi_semanal DECIMAL(15,6),
    funding_rates DECIMAL(15,6),
    oi_change DECIMAL(15,6),
    long_short_ratio DECIMAL(15,6),
    timestamp TIMESTAMP DEFAULT NOW(),
    fonte VARCHAR(50) DEFAULT 'Sistema',
    metadados JSONB DEFAULT '{}'
);

-- TABELA BLOCO RISCO
CREATE TABLE indicadores_risco (
    id SERIAL PRIMARY KEY,
    dist_liquidacao DECIMAL(15,6),
    health_factor DECIMAL(15,6),
    exchange_netflow DECIMAL(15,6),
    stablecoin_ratio DECIMAL(15,6),
    timestamp TIMESTAMP DEFAULT NOW(),
    fonte VARCHAR(50) DEFAULT 'Sistema',
    metadados JSONB DEFAULT '{}'
);

-- TABELA BLOCO TÉCNICO
CREATE TABLE indicadores_tecnico (
    id SERIAL PRIMARY KEY,
    sistema_emas DECIMAL(15,6),
    padroes_graficos DECIMAL(15,6),
    timestamp TIMESTAMP DEFAULT NOW(),
    fonte VARCHAR(50) DEFAULT 'Sistema',
    metadados JSONB DEFAULT '{}'
);

-- ==========================================
-- ÍNDICES SEPARADOS (SINTAXE CORRETA POSTGRESQL)
-- ==========================================

CREATE INDEX idx_ciclo_timestamp ON indicadores_ciclo (timestamp DESC);
CREATE INDEX idx_momentum_timestamp ON indicadores_momentum (timestamp DESC);
CREATE INDEX idx_risco_timestamp ON indicadores_risco (timestamp DESC);
CREATE INDEX idx_tecnico_timestamp ON indicadores_tecnico (timestamp DESC);

-- ==========================================
-- DADOS DE EXEMPLO
-- ==========================================

-- Exemplo Bloco Ciclo
INSERT INTO indicadores_ciclo (mvrv_z_score, realized_ratio, puell_multiple, fonte) VALUES
(2.75, 1.85, 1.44, 'Notion'),
(2.68, 1.82, 1.41, 'Glassnode'),
(2.71, 1.88, 1.47, 'Manual');

-- Exemplo Bloco Momentum
INSERT INTO indicadores_momentum (rsi_semanal, funding_rates, oi_change, long_short_ratio, fonte) VALUES
(52.3, 0.015, 12.5, 0.98, 'TradingView'),
(48.7, 0.012, 8.2, 1.02, 'Coinglass');

-- ==========================================
-- QUERIES ÚTEIS PARA TESTE
-- ==========================================

-- Buscar dados mais recentes do bloco ciclo
SELECT * FROM indicadores_ciclo ORDER BY timestamp DESC LIMIT 1;

-- Buscar dados mais recentes do bloco momentum  
SELECT * FROM indicadores_momentum ORDER BY timestamp DESC LIMIT 1;

-- Verificar última atualização de cada bloco
SELECT 
    'ciclo' as bloco,
    timestamp,
    EXTRACT(EPOCH FROM (NOW() - timestamp))/3600 as horas_atras
FROM indicadores_ciclo 
ORDER BY timestamp DESC LIMIT 1

UNION ALL

SELECT 
    'momentum' as bloco,
    timestamp,
    EXTRACT(EPOCH FROM (NOW() - timestamp))/3600 as horas_atras
FROM indicadores_momentum 
ORDER BY timestamp DESC LIMIT 1;

-- ==========================================
-- LIMPEZA (se necessário)
-- ==========================================

-- DROP TABLE IF EXISTS indicadores_ciclo;
-- DROP TABLE IF EXISTS indicadores_momentum;
-- DROP TABLE IF EXISTS indicadores_risco;
-- DROP TABLE IF EXISTS indicadores_tecnico;