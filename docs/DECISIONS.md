# REGISTRO DE DECISÕES ARQUITETURAIS (DECISIONS.md)

Este documento registra as Decisões de Arquitetura de Software (ADRs - *Architectural Decision Records*) que guiam a evolução do projeto ULTRON.

---

## Índice de Decisões

- [ADR-001: Adoção do AI Gateway Agnóstico a Provedores e Modelos](#adr-001-adoção-do-ai-gateway-agnóstico-a-provedores-e-modelos)
- [ADR-002: Modularização dos Monólitos (ui.py e main.py) com Event Bus Assíncrono](#adr-002-modularização-dos-monólitos-uipy-e-mainpy-com-event-bus-assíncrono)
- [ADR-003: Implementação do Tool Registry Tipado com Pydantic e Execution Guard](#adr-003-implementação-do-tool-registry-tipado-com-pydantic-e-execution-guard)
- [ADR-004: Eliminação de Git Reset Destrutivo no Updater e Blindagem de Segredos](#adr-004-eliminação-de-git-reset-destrutivo-no-updater-e-blindagem-de-segredos)
- [ADR-005: Transição da Memória para Arquitetura Híbrida Vetorial](#adr-005-transição-da-memória-para-arquitetura-híbrida-vetorial)
- [ADR-006: Substituição de Mocks de Smart Home pela API Oficial do Home Assistant](#adr-006-substituição-de-mocks-de-smart-home-pela-api-oficial-do-home-assistant)
- [ADR-007: Isolamento e Sandbox para Execução de Código Gerado por IA](#adr-007-isolamento-e-sandbox-para-execução-de-código-gerado-por-ia)
- [ADR-008: Preservação Integral da Estética Visual Holográfica](#adr-008-preservação-integral-da-estética-visual-holográfica)
- [ADR-009: Padronização no SDK Moderno google-genai](#adr-009-padronização-no-sdk-moderno-google-genai)
- [ADR-010: Unificação dos Servidores Locais em um Único Gateway ASGI](#adr-010-unificação-dos-servidores-locais-em-um-único-gateway-asgi)

---

### ADR-001: Adoção do AI Gateway Agnóstico a Provedores e Modelos
- **Status:** Aceito.
- **Data:** 2026-10-02.
- **Contexto:** Diversos módulos do projeto contêm nomes de modelos hardcoded que não existem na API do Google (ex.: `"gemini-3.6-flash"`, `"gemini-3.1-flash-lite"`), além de chamadas diretas espalhadas por 49 arquivos, sem política uniforme de retries, rate-limits ou fallback offline.
- **Decisão:** Criar uma camada centralizadora denominada `AI Gateway` que padroniza o envio de prompts, streaming de áudio/texto e tool-calling, abstraindo completamente o provedor real (Gemini, Claude, OpenAI, OpenRouter ou Ollama local).
- **Consequências:**
  - *Positivas:* Eliminação de chamadas quebradas por modelos descontinuados; failover transparente para modelos locais se a internet cair; controle unificado de custos e cotas.
  - *Negativas:* Necessidade de mapear os recursos específicos do Gemini Live (áudio bidirecional) através de adaptadores dedicados.

---

### ADR-002: Modularização dos Monólitos (ui.py e main.py) com Event Bus Assíncrono
- **Status:** Aceito.
- **Data:** 2026-10-02.
- **Contexto:** [ui.py](file:///d:/Downloads/ultron/Ultron/ui.py) possui 14.329 linhas e [main.py](file:///d:/Downloads/ultron/Ultron/main.py) possui 4.784 linhas. O acoplamento entre interface, threads de áudio, sockets e lógica de negócio impede testes unitários, quebra a manutenibilidade e torna qualquer refatoração de alto risco.
- **Decisão:** Decompor `ui.py` em um pacote modular `ui/` e `main.py` em módulos de responsabilidade única (`audio/`, `agent/`, `core/`), conectando todos os subsistemas através de um `Event Bus` assíncrono baseado em corrotinas Python (`asyncio`).
- **Consequências:**
  - *Positivas:* Código manutenível, componentes com menos de 400 linhas, facilidade extrema de teste e isolamento de falhas.
  - *Negativas:* Exigirá cuidado rigoroso na transição entre threads de background e a thread principal de eventos do Qt (`QEventLoop`).

---

### ADR-003: Implementação do Tool Registry Tipado com Pydantic e Execution Guard
- **Status:** Aceito.
- **Data:** 2026-10-02.
- **Contexto:** O projeto possui mais de 1.250 linhas de declarações manuais de dicionários JSON em [main.py](file:///d:/Downloads/ultron/Ultron/main.py#L620), enquanto `agent/planner.py` usa outro formato de prompt texto. Além disso, ferramentas perigosas são chamadas diretamente pela IA sem classificação de risco.
- **Decisão:** Implementar um `Tool Registry` onde cada ferramenta é uma classe ou função decorada com esquemas tipados via Pydantic, associada a um interceptor de segurança (`Execution Guard`) que classifica o risco em 4 Tiers (0: Leitura, 1: Reversível, 2: Externo, 3: Crítico/Irreversível).
- **Consequências:**
  - *Positivas:* Validação de parâmetros em tempo de compilação/execução; geração automática de esquemas para qualquer LLM; bloqueio programático de ações perigosas sem aval humano.
  - *Negativas:* Refatoração gradual da assinatura das 49 ferramentas existentes.

---

### ADR-004: Eliminação de Git Reset Destrutivo no Updater e Blindagem de Segredos
- **Status:** Aceito.
- **Data:** 2026-10-02.
- **Contexto:** [core/updater.py](file:///d:/Downloads/ultron/Ultron/core/updater.py#L70) executa `git reset --hard origin/main` apontando para o repositório de outro desenvolvedor, com risco iminente de perda de dados. Além disso, chaves ativas estão gravadas em texto aberto em [config/api_keys.json](file:///d:/Downloads/ultron/Ultron/config/api_keys.json).
- **Decisão:** Desativar permanentemente o método de reset forçado do updater; criar um sistema de atualização limpo e opcional; migrar o carregamento de credenciais exclusivamente para arquivos `.env` ou Windows DPAPI.
- **Consequências:**
  - *Positivas:* Eliminação do maior risco de perda de código do repositório; proteção total das credenciais e conformidade com padrões de segurança da informação.
  - *Negativas:* Usuário deverá definir as variáveis em seu `.env` local ou interface segura.

---

### ADR-005: Transição da Memória para Arquitetura Híbrida Vetorial
- **Status:** Aceito.
- **Data:** 2026-10-02.
- **Contexto:** O sistema de memória atual ([memory/memory_manager.py](file:///d:/Downloads/ultron/Ultron/memory/memory_manager.py)) depende de expressões regulares e correspondência léxica de palavras em um arquivo JSON. O assistente é incapaz de compreender sinônimos ou conceitos relacionados semanticamente.
- **Decisão:** Adotar uma camada de memória híbrida: banco vetorial local embutido (`ChromaDB` ou `sqlite-vec`) para memória semântica + SQLite para histórico episódico de conversas.
- **Consequências:**
  - *Positivas:* Recuperação contextual de alta fidelidade; persistência real de projetos, preferências e fatos; suporte a RAG local.
  - *Negativas:* Inclusão de dependência de biblioteca de vetorização/embeddings.

---

### ADR-006: Substituição de Mocks de Smart Home pela API Oficial do Home Assistant
- **Status:** Aceito.
- **Data:** 2026-10-02.
- **Contexto:** O módulo [smart_home/providers/builtin.py](file:///d:/Downloads/ultron/Ultron/smart_home/providers/builtin.py) possui integrações falsas (mocks estáticos) para Philips Hue, LG, Daikin, Tuya, Nest e SmartThings, induzindo o usuário a acreditar que seus aparelhos estão conectados quando não estão.
- **Decisão:** Descontinuar os provedores mockados individuais e criar um provedor universal baseado na API WebSocket/REST do **Home Assistant**, que conecta nativamente a mais de 2.000 marcas e protocolos (Zigbee, Z-Wave, Matter, MQTT).
- **Consequências:**
  - *Positivas:* Suporte real e robusto a virtualmente qualquer dispositivo residencial; eliminação de centenas de linhas de mocks inúteis.
  - *Negativas:* Exige que o usuário possua uma instância do Home Assistant em sua rede local para aparelhos complexos (mantendo Kasa como suporte direto plug-and-play).

---

### ADR-007: Isolamento e Sandbox para Execução de Código Gerado por IA
- **Status:** Aceito.
- **Data:** 2026-10-02.
- **Contexto:** [agent/executor.py](file:///d:/Downloads/ultron/Ultron/agent/executor.py#L88) e [actions/auto_heal_engine.py](file:///d:/Downloads/ultron/Ultron/actions/auto_heal_engine.py) gravam scripts Python temporários e os executam diretamente no host com permissões de usuário ou administrador, permitindo vulnerabilidade de Remote Code Execution (RCE).
- **Decisão:** Proibir terminantemente a execução direta de código gerado no host principal. Implementar uma camada de sandbox (processos isolados com tokens restritos no Windows ou containerização) e validação sintática estrita com Árvore de Sintaxe Abstrata (AST) para barrar chamadas a comandos destrutivos do sistema operacional.
- **Consequências:**
  - *Positivas:* Segurança absoluta contra alucinações de IA ou códigos nocivos.
  - *Negativas:* Scripts que demandem bibliotecas nativas de baixo nível precisarão ser declarados e autorizados explicitamente.

---

### ADR-008: Preservação Integral da Estética Visual Holográfica
- **Status:** Aceito.
- **Data:** 2026-10-02.
- **Contexto:** A interface em PyQt6 com visual futurista (tons âmbar/dourado escuro `#020305`, reator Three.js/WebGL em tempo real e sonoplastia sci-fi) representa um dos pontos fortes da identidade do projeto.
- **Decisão:** Nenhuma refatoração de código de backend ou modularização de UI poderá alterar a estética, paleta de cores, tipografia, efeitos holográficos ou animações existentes.
- **Consequências:**
  - *Positivas:* Manutenção da experiência do usuário e do apelo visual do produto.
  - *Negativas:* Exige testes visuais contínuos após o desacoplamento dos componentes do `ui.py`.

---

### ADR-009: Padronização no SDK Moderno google-genai
- **Status:** Aceito.
- **Data:** 2026-10-02.
- **Contexto:** O projeto importa simultaneamente `google.generativeai` (SDK legado e descontinuado) e `google.genai` (novo SDK unificado do Google), inclusive no mesmo arquivo em [workspace_store.py](file:///d:/Downloads/ultron/Ultron/workspace_store.py).
- **Decisão:** Padronizar todo o repositório exclusivamente no SDK moderno `google-genai` e remover a dependência obsoleta `google-generativeai` do [requirements.txt](file:///d:/Downloads/ultron/Ultron/requirements.txt).
- **Consequências:**
  - *Positivas:* Compatibilidade com o Gemini 2.0/2.5 Live Audio API, tipagem unificada e melhoria na performance de streaming.
  - *Negativas:* Ajuste nas chamadas legadas em `agent/planner.py`, `agent/executor.py` e `workspace_store.py`.

---

### ADR-010: Unificação dos Servidores Locais em um Único Gateway ASGI
- **Status:** Aceito.
- **Data:** 2026-10-02.
- **Contexto:** O sistema mantém dois servidores FastAPI rodando em threads separadas: porta 8000 para dashboard web e porta 8765 para gateway mobile.
- **Decisão:** Consolidar os endpoints sob uma única aplicação FastAPI/ASGI com roteamento modular (`/api/v1/dashboard`, `/api/v1/connect`, `/ws/mobile`), eliminando conflitos de portas e facilitando configuração de firewall no Windows.
- **Consequências:**
  - *Positivas:* Menor consumo de memória e threads; configuração simplificada de rede local e certificados TLS.
  - *Negativas:* Ajuste na URL de conexão do aplicativo Android.
