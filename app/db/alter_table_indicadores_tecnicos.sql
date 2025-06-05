-- ==========================================
-- ALTER TABLE indicadores_tecnico
-- Adicionar campos para EMAs e scores por timeframe
-- Release 1.0.19 - Coleta EMAs
-- ==========================================

-- 1. ADICIONAR COLUNAS EMAs SEMANAL (1W)
ALTER TABLE indicadores_tecnico 
ADD COLUMN IF NOT EXISTS ema_17_1w DECIMAL(15,6),
ADD COLUMN IF NOT EXISTS ema_34_1w DECIMAL(15,6),
ADD COLUMN IF NOT EXISTS ema_144_1w DECIMAL(15,6),
ADD COLUMN IF NOT EXISTS ema_305_1w DECIMAL(15,6),
ADD COLUMN IF NOT EXISTS ema_610_1w DECIMAL(15,6);

-- 2. ADICIONAR COLUNAS EMAs DIÁRIO (1D)
ALTER TABLE indicadores_tecnico 
ADD COLUMN IF NOT EXISTS ema_17_1d DECIMAL(15,6),
ADD COLUMN IF NOT EXISTS ema_34_1d DECIMAL(15,6),
ADD COLUMN IF NOT EXISTS ema_144_1d DECIMAL(15,6),
ADD COLUMN IF NOT EXISTS ema_305_1d DECIMAL(15,6),
ADD COLUMN IF NOT EXISTS ema_610_1d DECIMAL(15,6);

-- 3. ADICIONAR PREÇO ATUAL
ALTER TABLE indicadores_tecnico 
ADD COLUMN IF NOT EXISTS btc_price_current DECIMAL(15,6);

-- 4. ADICIONAR SCORES CALCULADOS
ALTER TABLE indicadores_tecnico 
ADD COLUMN IF NOT EXISTS score_1w_ema DECIMAL(5,2),      -- Alinhamento semanal (0-10)
ADD COLUMN IF NOT EXISTS score_1w_price DECIMAL(5,2),    -- Posição semanal (0-10)
ADD COLUMN IF NOT EXISTS score_1d_ema DECIMAL(5,2),      -- Alinhamento diário (0-10)
ADD COLUMN IF NOT EXISTS score_1d_price DECIMAL(5,2);    -- Posição diário (0-10)

-- 5. ADICIONAR METADADOS COMPLEMENTARES
ALTER TABLE indicadores_tecnico 
ADD COLUMN IF NOT EXISTS score_consolidado_1w DECIMAL(5,2),  -- Score total semanal
ADD COLUMN IF NOT EXISTS score_consolidado_1d DECIMAL(5,2),  -- Score total diário
ADD COLUMN IF NOT EXISTS score_final_ponderado DECIMAL(5,2), -- 70% semanal + 30% diário
ADD COLUMN IF NOT EXISTS distancias_json JSONB DEFAULT '{}'; -- Distâncias % de cada EMA

-- 6. COMENTÁRIOS NAS COLUNAS PARA DOCUMENTAÇÃO
COMMENT ON COLUMN indicadores_tecnico.ema_17_1w IS 'EMA 17 períodos timeframe semanal';
COMMENT ON COLUMN indicadores_tecnico.ema_34_1w IS 'EMA 34 períodos timeframe semanal';
COMMENT ON COLUMN indicadores_tecnico.ema_144_1w IS 'EMA 144 períodos timeframe semanal';
COMMENT ON COLUMN indicadores_tecnico.ema_305_1w IS 'EMA 305 períodos timeframe semanal';
COMMENT ON COLUMN indicadores_tecnico.ema_610_1w IS 'EMA 610 períodos timeframe semanal';

COMMENT ON COLUMN indicadores_tecnico.ema_17_1d IS 'EMA 17 períodos timeframe diário';
COMMENT ON COLUMN indicadores_tecnico.ema_34_1d IS 'EMA 34 períodos timeframe diário';
COMMENT ON COLUMN indicadores_tecnico.ema_144_1d IS 'EMA 144 períodos timeframe diário';
COMMENT ON COLUMN indicadores_tecnico.ema_305_1d IS 'EMA 305 períodos timeframe diário';
COMMENT ON COLUMN indicadores_tecnico.ema_610_1d IS 'EMA 610 períodos timeframe diário';

COMMENT ON COLUMN indicadores_tecnico.btc_price_current IS 'Preço BTC no momento da coleta';

COMMENT ON COLUMN indicadores_tecnico.score_1w_ema IS 'Score alinhamento EMAs semanal (0-10)';
COMMENT ON COLUMN indicadores_tecnico.score_1w_price IS 'Score posição vs EMAs semanal com distância (0-10)';
COMMENT ON COLUMN indicadores_tecnico.score_1d_ema IS 'Score alinhamento EMAs diário (0-10)';
COMMENT ON COLUMN indicadores_tecnico.score_1d_price IS 'Score posição vs EMAs diário com distância (0-10)';

COMMENT ON COLUMN indicadores_tecnico.score_consolidado_1w IS 'Score total semanal (alinhamento + posição) / 2';
COMMENT ON COLUMN indicadores_tecnico.score_consolidado_1d IS 'Score total diário (alinhamento + posição) / 2';
COMMENT ON COLUMN indicadores_tecnico.score_final_ponderado IS 'Score final: 70% semanal + 30% diário';

COMMENT ON COLUMN indicadores_tecnico.distancias_json IS 'Distâncias percentuais do preço para cada EMA';

-- 7. ÍNDICE PARA PERFORMANCE
CREATE INDEX IF NOT EXISTS idx_tecnico_timestamp_scores 
ON indicadores_tecnico (timestamp DESC, score_final_ponderado DESC);

-- 8. VERIFICAR ESTRUTURA ATUALIZADA
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'indicadores_tecnico' 
ORDER BY ordinal_position;

-- ==========================================
-- EXEMPLO DE DADOS APÓS IMPLEMENTAÇÃO
-- ==========================================

/*
INSERT INTO indicadores_tecnico (
    ema_17_1w, ema_34_1w, ema_144_1w, ema_305_1w, ema_610_1w,
    ema_17_1d, ema_34_1d, ema_144_1d, ema_305_1d, ema_610_1d,
    btc_price_current,
    score_1w_ema, score_1w_price, score_1d_ema, score_1d_price,
    score_consolidado_1w, score_consolidado_1d, score_final_ponderado,
    distancias_json, fonte, timestamp
) VALUES (
    94500.00, 92800.00, 89200.00, 85600.00, 81200.00,  -- EMAs semanal
    95200.00, 94100.00, 91500.00, 88200.00, 84800.00,  -- EMAs diário
    95000.00,                                           -- Preço atual
    8.5, 7.2, 7.0, 6.8,                               -- Scores individuais
    7.85, 6.90, 7.50,                                 -- Scores consolidados
    '{"1w": {"17": "+0.53%", "34": "+2.37%", "144": "+6.50%"}, "1d": {"17": "-0.21%", "34": "+0.96%"}}',
    'tvdatafeed', NOW()
);
*/