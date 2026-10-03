# ROADMAP TÉCNICO E FASES DE EVOLUÇÃO (ROADMAP.md)

Este documento estabelece o planejamento estratégico e a ordem progressiva de evolução do projeto ULTRON.

> **IMPORTANTE:** Nenhuma das fases deste documento deve ser implementada de forma precipitada. Toda transição entre fases requer análise prévia, plano atômico aprovado, implementação, testes e validação rigorosa (*Workflow ANALYZE → PLAN → IMPLEMENT → TEST → VERIFY → REPORT*).

---

## Visão Geral das Fases

```text
Fase 0: Estabilização Emergencial & Segurança (P0)
   ↓
Fase 1: Desacoplamento Estrutural & Event Bus
   ↓
Fase 2: AI Gateway & Independência de Modelos
   ↓
Fase 3: Tool Registry & Execution Guard
   ↓
Fase 4: Memória Vetorial Semântica & Contexto Persistente
   ↓
Fase 5: Agente Autônomo com Verificação & Replanejamento
   ↓
Fase 6: Resiliência Offline & Modelos Locais (Voz e LLM)
   ↓
Fase 7: Ecossistema de Integrações Reais (Home Assistant & APIs Oficiais)
```

---

## Detalhamento das Fases

### Fase 0: Estabilização Emergencial & Segurança (P0)
- **Objetivo:** Eliminar riscos críticos de perda de código, vazamento de credenciais e quebras imediatas em runtime.
- **Escopo Técnico:**
  1. **Desativação do Updater Perigoso:** Neutralizar o método `apply_update_and_restart()` em [core/updater.py](file:///d:/Downloads/ultron/Ultron/core/updater.py#L64) para impedir que `git reset --hard` apague o trabalho do usuário.
  2. **Correção de Nomes de Modelos Fictícios:** Substituir as referências a modelos inexistentes (`gemini-3.6-flash`, `gemini-3.1-flash-lite`) por modelos oficiais estáveis da API do Google (`gemini-2.0-flash` e `models/gemini-2.0-flash-exp`).
  3. **Criação da Ferramenta Ausente `cmd_control`:** Implementar `actions/cmd_control.py` com tipagem e tratamento de erros para sanar o `ModuleNotFoundError` no executor.
  4. **Proteção de Segredos:** Criar suporte a `.env` via `python-dotenv` e remover segredos expostos em texto puro.
  5. **Habilitação da Suíte de Testes:** Adicionar `pytest` ao `requirements.txt` e validar a execução dos testes existentes.
- **Critérios de Aceitação (DoD):**
  - Nenhum modelo inexistente chamado no código.
  - `pytest tests/` executa e passa com 100% de sucesso.
  - O updater não executa resets destrutivos no repositório.

---

### Fase 1: Desacoplamento Estrutural & Event Bus
- **Objetivo:** Quebrar os monólitos [ui.py](file:///d:/Downloads/ultron/Ultron/ui.py) (14k linhas) e [main.py](file:///d:/Downloads/ultron/Ultron/main.py) (4.7k linhas) em componentes modulares integrados por um barramento assíncrono.
- **Escopo Técnico:**
  1. **Implementação do Event Bus:** Criar `core/event_bus.py` baseado em `asyncio` com fila de eventos tipados.
  2. **Modularização de `ui.py`:** Decompor a interface em pacote `ui/` mantendo 100% da estética holográfica:
     - `ui/theme.py`, `ui/views/`, `ui/overlays/`, `ui/widgets/`, `ui/main_window.py`.
  3. **Modularização de `main.py`:** Extrair o loop de áudio para `audio/engine.py` e o despacho para `agent/dispatcher.py`.
- **Critérios de Aceitação (DoD):**
  - Nenhum arquivo com mais de 600 linhas de código.
  - UI continua idêntica visualmente e reativa.
  - Zero referências circulares ou locks entre threads de UI e background.

---

### Fase 2: AI Gateway & Independência de Modelos
- **Objetivo:** Isolar o sistema de dependências de provedores de IA específicos com pooling de conexões e failover automático.
- **Escopo Técnico:**
  1. **Criação do AI Gateway:** Pacote `ai_gateway/` com adaptadores para Google Gemini (`google-genai`), Anthropic Claude, OpenAI e OpenRouter.
  2. **Failover Transparente:** Se a API primária retornar erro 429 ou falhar, o gateway alterna automaticamente para a secundária sem interromper a fala do usuário.
  3. **Depreciação de SDKs Legados:** Remoção completa de `google-generativeai`.
- **Critérios de Aceitação (DoD):**
  - Troca de provedor via arquivo de configuração sem alterar código de produção.
  - Testes automatizados de failover simulado passando com sucesso.

---

### Fase 3: Tool Registry & Execution Guard
- **Objetivo:** Padronizar todas as 49 ferramentas sob uma interface estrita com validação Pydantic e classificação de risco.
- **Escopo Técnico:**
  1. **Implementação do Tool Registry:** `tools/registry.py` com registro via decorators e geração automática de esquemas para Gemini e OpenAI.
  2. **Implementação do Execution Guard:** Interceptor de permissão avaliando Tiers 0 a 3.
  3. **Integração com `core/confirm.py` e `core/undo.py`:** Bloqueio de ações críticas com aprovação modal no HUD e registro automático de rollback.
- **Critérios de Aceitação (DoD):**
  - Nenhuma ferramenta aceita parâmetros sem validação tipada prévia.
  - Tentativas de deleção de arquivos ou desligamento do PC exigem confirmação obrigatória.

---

### Fase 4: Memória Vetorial Semântica & Contexto Persistente
- **Objetivo:** Capacitar o ULTRON a lembrar de preferências, projetos e conceitos correlatos através de busca vetorial local.
- **Escopo Técnico:**
  1. **Banco Vetorial Local:** Integração do ChromaDB ou `sqlite-vec` operando 100% local no disco do usuário.
  2. **Motor de Busca Híbrido:** Junção de busca vetorial (similaridade de cosseno) com busca léxica (FTS5 no SQLite) via Reciprocal Rank Fusion (RRF).
  3. **Consolidação em Background:** Compactação automática e resumos periódicos de sessões.
- **Critérios de Aceitação (DoD):**
  - Uma pergunta como "qual é o meu carro?" encontra a memória "comprei um Civic ano passado" com precisão.
  - Orçamento do prompt do sistema permanece rigorosamente sob 2.600 caracteres.

---

### Fase 5: Agente Autônomo com Verificação & Replanejamento
- **Objetivo:** Permitir a resolução autônoma de tarefas complexas em múltiplos passos com auto-avaliação de resultados.
- **Escopo Técnico:**
  1. **Planejador em Grafo (DAG):** Geração de grafos de tarefas com dependências explícitas e teto de 8 passos.
  2. **Módulo de Reflexão (Verifier):** Inspeção pós-etapa confirmando a veracidade e consistência do resultado.
  3. **Replanejamento Dinâmico:** Capacidade de contornar falhas de ferramentas alterando a estratégia em tempo real.
- **Critérios de Aceitação (DoD):**
  - O agente resolve tarefas compostas (pesquisar -> criar PDF -> enviar e-mail) de forma autônoma e consistente.
  - Se uma etapa intermediária falhar, o agente replaneja sem travar nem alucinar conclusão falsa.

---

### Fase 6: Resiliência Offline & Modelos Locais (Voz e LLM)
- **Objetivo:** Tornar o assistente funcional mesmo quando desconectado da internet.
- **Escopo Técnico:**
  1. **STT Local:** Integração do Whisper.cpp / Faster-Whisper ou Vosk para transcrição de microfone local.
  2. **VAD Local:** Silero VAD para detecção de início e término de fala com zero latência de rede.
  3. **TTS Local:** Piper TTS ou síntese nativa do Windows Speech API para fala offline rápida.
  4. **LLM Local:** Conexão nativa com Ollama (Llama 3.2 / Qwen 2.5) para comandos básicos locais.
- **Critérios de Aceitação (DoD):**
  - Desconectar o cabo de rede/Wi-Fi permite continuar controlando volume, abrindo apps, consultando lembretes e recebendo respostas faladas locais.

---

### Fase 7: Ecossistema de Integrações Reais
- **Objetivo:** Conectar o assistente ao ecossistema real de dispositivos sem mocks ou automações frágeis.
- **Escopo Técnico:**
  1. **Home Assistant Universal:** Provedor oficial WebSocket/REST controlando luzes, termostatos, sensores e eletrodomésticos reais.
  2. **Google APIs Oficiais:** Integração oficial com Google Calendar e Google Drive via OAuth 2.0.
  3. **Unificação do Gateway:** Um único servidor ASGI na porta 8765 atendendo dashboard web, API mobile e WebSockets protegidos.
- **Critérios de Aceitação (DoD):**
  - Zero mocks em produção.
  - Dispositivos residenciais reais controlados com confirmação de status em tempo real.
