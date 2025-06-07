# app/database/migrations/create_alertas_tables.py

import logging
from app.services.utils.helpers.postgres.base import execute_query

logger = logging.getLogger(__name__)

def create_alertas_tables():
    """Cria tabelas do sistema de alertas"""
    try:
        logger.info("🔧 Criando tabelas do sistema de alertas...")
        
        # Tabela principal de alertas
        alertas_table = """
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
        """
        
        execute_query(alertas_table)
        logger.info("✅ Tabela alertas_historico criada")
        
        # Tabela configurações
        config_table = """
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
        """
        
        execute_query(config_table)
        logger.info("✅ Tabela alertas_config criada")
        
        # Índices para performance
        indices = [
            "CREATE INDEX IF NOT EXISTS idx_alertas_ativo ON alertas_historico (ativo, timestamp DESC);",
            "CREATE INDEX IF NOT EXISTS idx_alertas_tipo_categoria ON alertas_historico (tipo, categoria);",
            "CREATE INDEX IF NOT EXISTS idx_alertas_prioridade ON alertas_historico (prioridade, timestamp DESC);",
            "CREATE INDEX IF NOT EXISTS idx_alertas_cooldown ON alertas_historico (cooldown_ate);"
        ]
        
        for idx in indices:
            execute_query(idx)
        
        logger.info("✅ Índices criados")
        logger.info("🎉 Sistema de alertas configurado com sucesso!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro criando tabelas alertas: {str(e)}")
        return False

if __name__ == "__main__":
    create_alertas_tables()