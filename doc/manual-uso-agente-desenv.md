# Manual Prático - Janela de Contexto 15 Mensagens

## 🎯 OBJETIVO
Maximizar eficiência do agente desenvolvedor

## 📋 CONFIGURAÇÃO INICIAL

### 1. Configurar Context Window
```
Chat Memory → Context Window Length: 15
```

### 2. Estrutura da Conversa Ideal
```
Mensagem 1-3:   Setup/Contexto inicial
Mensagem 4-12:  Desenvolvimento ativo  
Mensagem 13-15: Finalização/Aprovação
```

## 🔧 ESTRATÉGIAS PRÁTICAS

### 💡 REGRA 1: CONVERSAS FOCADAS

**❌ EVITE:**
```
- Olá, como está?
- Pode me ajudar?
- Vou enviar alguns arquivos...
```

**✅ FAÇA:**
```
- Leia o arquivo src/controllers/userController.js e identifique problemas
- Implemente validação JWT no middleware auth.js  
- Corrija o bug na função calculateProfit() linha 45
```

### 💡 REGRA 2: AGRUPE TAREFAS RELACIONADAS

**❌ SEPARADO (consome contexto):**
```
Msg 1: Leia package.json
Msg 2: Leia .env.example  
Msg 3: Leia docker-compose.yml
Msg 4: Agora analise a estrutura
```

**✅ AGRUPADO (economiza contexto):**
```
Msg 1: Leia package.json, .env.example e docker-compose.yml. 
       Depois analise a estrutura e identifique inconsistências.
```

### 💡 REGRA 3: FINALIZE TAREFAS ANTES DE NOVAS

**❌ CONTEXTO FRAGMENTADO:**
```
Msg 1: Crie API /users
Msg 2: Na verdade, antes crie o modelo User
Msg 3: Aliás, configure o banco primeiro
Msg 4: Voltando para a API...
```

**✅ CONTEXTO LIMPO:**
```
Msg 1: Configure banco PostgreSQL + Prisma
Msg 2: [Aprovação] Está correto, pode commitar
Msg 3: Agora crie modelo User com validações
Msg 4: [Aprovação] Perfeito, próximo passo
Msg 5: Implemente API /users usando o modelo
```

## ⚡ TÉCNICAS AVANÇADAS

### 🔄 RESET ESTRATÉGICO

**Quando usar:**
- Mudança de contexto (nova feature)
- Contexto poluído com erros
- Chegou na mensagem 13-14

**Como fazer:**
```
"Contexto resetado. Projeto BTC Turbo:
- Estrutura atual: [resumo rápido]
- Última implementação: [status]
- Próxima tarefa: [objetivo claro]"
```

### 📝 RESUMOS EFICIENTES

**A cada 10 mensagens:**
```
"Resumo do progresso:
✅ Implementado: API users, middleware auth
🔄 Em andamento: Validação JWT
⏭️ Próximo: Testes unitários
Pode continuar com os testes."
```

### 🎯 COMANDOS OTIMIZADOS

**Use comandos diretos:**
```
✅ "Corrija linha 25 do auth.js - trocar bcrypt por argon2"
✅ "Adicione endpoint GET /users/:id com validação"
✅ "Documente função calculateProfit com JSDoc"

❌ "Você poderia por favor analisar se seria possível..."
❌ "Gostaria que você desse uma olhada no arquivo..."
```

## 📊 MONITORAMENTO

### 🔍 SINAIS DE CONTEXTO POLUÍDO:
- Agente repete informações
- Responde baseado em contexto antigo
- Perde foco da tarefa atual

### 🚨 QUANDO RESETAR:
- Erro recorrente por 3+ mensagens
- Mudança de módulo/feature
- Contexto chegou em 13-14 mensagens

## 🏆 EXEMPLO PRÁTICO PERFEITO

```
Msg 1: "Leia src/models/User.js e identifique melhorias de performance"
Msg 2: [Agente analisa e sugere otimizações]
Msg 3: "Aplique as otimizações e mostre código final"
Msg 4: [Agente implementa] 
Msg 5: "Aprovado, commit as alterações"
Msg 6: [Agente faz commit]
Msg 7: "Agora implemente testes unitários para User.js"
Msg 8: [Agente cria testes]
Msg 9: "Execute os testes e reporte resultados"
Msg 10: [Agente executa e reporta]
Msg 11: "Tudo aprovado. Próximo: API /users/profile"
Msg 12: [Agente implementa endpoint]
Msg 13: "Código final correto, pode commitar"
Msg 14: [Agente faz commit]
Msg 15: "Resumo: User.js otimizado, testes OK, API profile implementada"
```

**Resultado:** 15 mensagens = 1 módulo completo!

## 🎯 CHECKLIST DE EFICIÊNCIA

### Antes de Iniciar Conversa:
- [ ] Objetivo claro definido
- [ ] Arquivos/contexto necessário identificado
- [ ] Sequência de tarefas planejada

### Durante a Conversa:
- [ ] Comandos diretos e específicos
- [ ] Aguardar aprovação antes de próxima tarefa
- [ ] Agrupar tarefas relacionadas
- [ ] Monitorar número de mensagens

### Ao Finalizar:
- [ ] Resumo do que foi implementado
- [ ] Status dos commits realizados
- [ ] Próximos passos definidos

## 📈 MÉTRICAS DE SUCESSO

**Conversa Eficiente:**
- 1 funcionalidade completa por 15 mensagens
- Máximo 2 correções por implementação
- Zero mensagens de saudação/conversação
- 100% das tarefas finalizadas

**Sinais de Ineficiência:**
- Mais de 3 iterações para mesma tarefa
- Agente perde contexto recente
- Necessidade de repetir informações
- Tarefas inacabadas

---

**Versão:** 1.0  
**Projeto:** BTC Turbo  
**Data:** Maio 2025