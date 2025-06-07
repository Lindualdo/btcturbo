-- 1. Criar tabela principal alertas
CREATE TABLE IF NOT EXISTS alertas_historico (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(50) NOT NULL,
    categoria VARCHAR(20) NOT NULL,
    prioridade INTEGER NOT NULL,
    
    titulo VARCHAR(200) NOT NULL,
    mensagem TEXT NOT NULL,
    
    threshold_configurado DECIMAL(15,6),
    valor_atual DECIMAL(15,6),
    dados_contexto JSONB DEFAULT '{}',
    
    ativo BOOLEAN DEFAULT TRUE,
    resolvido BOOLEAN DEFAULT FALSE,
    resolvido_em TIMESTAMP NULL,
    
    cooldown_ate TIMESTAMP NULL,
    
    timestamp TIMESTAMP DEFAULT NOW()
);

-- 2. Criar tabela configurações
CREATE TABLE IF NOT EXISTS alertas_config (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(50) NOT NULL,
    categoria VARCHAR(20) NOT NULL,
    
    habilitado BOOLEAN DEFAULT TRUE,
    threshold_customizado DECIMAL(15,6) NULL,
    cooldown_minutos INTEGER DEFAULT 60,
    
    notificacao_dashboard BOOLEAN DEFAULT TRUE,
    notificacao_webhook BOOLEAN DEFAULT FALSE,
    webhook_url VARCHAR(500) NULL,
    
    criado_em TIMESTAMP DEFAULT NOW(),
    atualizado_em TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(tipo, categoria)
);

-- 3. Criar índices
CREATE INDEX IF NOT EXISTS idx_alertas_ativo 
ON alertas_historico (ativo, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_alertas_tipo_categoria 
ON alertas_historico (tipo, categoria);

CREATE INDEX IF NOT EXISTS idx_alertas_prioridade 
ON alertas_historico (prioridade, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_alertas_cooldown 
ON alertas_historico (cooldown_ate) 
WHERE cooldown_ate IS NOT NULL;

-- 4. Inserir configurações padrão
INSERT INTO alertas_config (tipo, categoria, habilitado, cooldown_minutos) VALUES
('posicao', 'critico', true, 5),
('posicao', 'urgente', true, 30),
('volatilidade', 'critico', true, 240),
('volatilidade', 'urgente', true, 120),
('mercado', 'critico', true, 60),
('mercado', 'urgente', true, 120),
('tatico', 'urgente', true, 60),
('onchain', 'informativo', true, 360)
ON CONFLICT (tipo, categoria) DO NOTHING;