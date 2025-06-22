-- 🧹 LIMPEZA E RECRIAÇÃO COMPLETA
DROP TABLE IF EXISTS matriz_ciclos_mercado CASCADE;

-- Criar tabela limpa
CREATE TABLE matriz_ciclos_mercado (
    id SERIAL PRIMARY KEY,
    nome_ciclo VARCHAR(50) NOT NULL,
    
    -- Ranges de entrada
    score_min INTEGER NOT NULL,
    score_max INTEGER NOT NULL,
    mvrv_min DECIMAL(4,2),
    mvrv_max DECIMAL(4,2),
    nupl_min DECIMAL(4,2),
    nupl_max DECIMAL(4,2),
    
    -- Regras de precedência 
    prioridade INTEGER DEFAULT 1,
    condicao_especial VARCHAR(100),
    
    -- Estratégia
    percentual_capital INTEGER NOT NULL,
    alavancagem DECIMAL(2,1) NOT NULL,
    
    -- Metadados
    caracteristicas TEXT,
    versao VARCHAR(10) DEFAULT 'v2.0',
    ativo BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

-- CARGA MATRIZ v2.0 - 16 CICLOS
-- Prioridade: 10=Override máximo, 9=Override topo, 8=Especial, 5=Extremos, 1=Normal

INSERT INTO matriz_ciclos_mercado (nome_ciclo, score_min, score_max, mvrv_min, mvrv_max, nupl_min, nupl_max, prioridade, condicao_especial, percentual_capital, alavancagem, caracteristicas) VALUES
-- Overrides NUPL < 0 (sempre compra)
('FUNDO ÉPICO', 90, 100, 0.0, 0.8, -1.0, 0.0, 10, 'NUPL<0 AND MVRV<0.8', 100, 3.0, 'Compra século'),
('REVERSÃO ÉPICA', 80, 90, 0.0, 1.0, -1.0, 0.1, 10, 'NUPL<0.1 AND MVRV<1.0', 100, 3.0, 'All-in'),
('CAPITULAÇÃO', 0, 20, 0.0, 0.8, -1.0, -0.1, 10, 'NUPL<-0.1 AND MVRV<0.8', 100, 3.0, 'Oportunidade histórica'),

-- Override MVRV > 3.7 (sempre topo)
('EUFORIA', 0, 20, 3.7, 10.0, 0.75, 1.0, 9, 'MVRV>3.7 AND NUPL>0.75', 20, 1.0, 'Mínimo absoluto'),

-- Casos especiais
('NOVO CICLO', 70, 80, 0.0, 1.2, -1.0, 0.25, 8, 'MVRV<1.2 AND NUPL<0.25', 100, 3.0, 'Reversão épica'),

-- Score extremos
('PRÉ-EUFORIA', 90, 100, 3.0, 10.0, 0.7, 1.0, 5, 'SCORE_EXTREMO_ALTO', 60, 1.0, 'Redução agressiva'),
('DISTRIBUIÇÃO', 20, 30, 3.0, 3.7, 0.65, 0.75, 5, 'SCORE_BAIXO_MVRV_ALTO', 40, 1.0, 'Proteção capital'),

-- Ciclos normais
('BEAR PROFUNDO', 20, 30, 0.8, 1.2, -0.1, 0.1, 1, NULL, 50, 1.0, 'Proteção máxima'),
('RECUPERAÇÃO', 30, 40, 1.0, 1.5, 0.0, 0.25, 1, NULL, 70, 1.0, 'Cautela'),
('ACUMULAÇÃO', 40, 50, 1.2, 2.0, 0.1, 0.35, 1, NULL, 80, 1.0, 'Preparação'),
('OPTIMISM', 50, 60, 1.5, 2.2, 0.35, 0.5, 1, NULL, 100, 1.3, 'Confiança inicial'),
('BELIEF', 50, 60, 2.0, 2.5, 0.5, 0.65, 1, NULL, 100, 1.5, 'Momentum confirmado'),
('TRANSIÇÃO BULL', 60, 70, 1.2, 1.8, 0.25, 0.4, 1, NULL, 100, 1.8, 'Breakout'),
('BULL INICIAL', 60, 70, 1.8, 2.5, 0.4, 0.55, 1, NULL, 100, 2.0, 'Tendência clara'),
('BULL CONFIRMADO', 70, 80, 2.0, 2.8, 0.5, 0.65, 1, NULL, 100, 2.2, 'Força sustentada'),
('BULL FORTE', 80, 90, 2.5, 3.5, 0.6, 0.75, 1, NULL, 100, 1.5, 'Cautela no topo'),
('BULL TARDIO', 30, 40, 2.5, 3.2, 0.55, 0.7, 1, NULL, 100, 1.5, 'Cautela no topo');

-- Verificação
SELECT nome_ciclo, 
       CONCAT(score_min,'-',score_max) as score,
       CONCAT(percentual_capital,'%') as capital,
       CONCAT(alavancagem,'x') as leverage,
       prioridade
FROM matriz_ciclos_mercado 
ORDER BY prioridade DESC, score_min;