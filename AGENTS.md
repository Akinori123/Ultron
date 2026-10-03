# CONSTITUIÇÃO PERMANENTE DO PROJETO ULTRON (AGENTS.md)

Este documento estabelece as diretrizes fundamentais, princípios arquiteturais, regras de segurança e o protocolo de trabalho obrigatório para qualquer agente de IA, desenvolvedor ou engenheiro que atue no repositório **ULTRON**.

---

## 1. Princípios Fundamentais do ULTRON

1. **Assistente Pessoal Local e Modular:** O ULTRON é concebido como um assistente pessoal local, modular, extensível e seguro, projetado para operar com baixa latência no ambiente Windows do usuário, com integração profunda ao sistema operacional, dispositivos móveis e automação residencial.
2. **Sem Refatorações Intempestivas:** O agente **NÃO DEVE** realizar grandes refatorações sem planejamento explícito e aprovação prévia. Nenhuma intervenção estrutural de grande porte deve ocorrer em um único ciclo.
3. **Mudanças Atômicas e Reversíveis:** Toda alteração no código deve ser pequena, incremental, testável e facilmente reversível.
4. **Análise Prévia Obrigatória:** Antes de qualquer modificação de código ou arquitetura, o agente deve obrigatoriamente inspecionar e compreender a fundo o estado atual da implementação.
5. **Comandos Não-Destrutivos:** O agente **NUNCA** deve executar comandos destrutivos (remoção em massa de arquivos, limpeza de branches Git, `git reset --hard`, scripts invasivos no registro) sem confirmação explícita do usuário.
6. **Proteção Total de Credenciais:** É expressamente proibido expor, imprimir em logs, trafegar em conexões inseguras ou versionar API keys, tokens de acesso, senhas ou credenciais de qualquer serviço.
7. **Proibição de Hardcoded Secrets:** Credenciais, chaves criptográficas ou tokens nunca devem ser inseridos diretamente no código-fonte. Devem ser gerenciados por variáveis de ambiente (`.env`) ou cofres seguros locais (KMS/DPAPI).
8. **Isolamento de Código Dinâmico (Anti-RCE):** O agente **NUNCA** deve executar código arbitrário gerado por modelos de linguagem diretamente no host sem uma camada formal de proteção, validação sintática estrita, aprovação humana e sandbox apropriado.
9. **Preferência por APIs Oficiais:** Sempre que disponível, deve-se priorizar o uso de APIs oficiais e documentadas, evitando raspagens frágeis (web scraping cego) ou engenharia reversa de APIs privadas sujeitas a bloqueio imediato (ex.: automações não autorizadas de redes sociais).
10. **Independência de Provedor nas Ferramentas:** Ferramentas e automações (*Tools/Actions*) devem ser 100% desacopladas de qualquer SDK proprietário de IA. Uma ferramenta recebe e retorna tipos primitivos ou esquemas tipados agnósticos (Pydantic/Dataclasses).
11. **Independência de Modelos Específicos:** O código de produção não deve ser amarrado a nomes rígidos de modelos que possam ser descontinuados ou sofrer alteração de versão. Modelos devem ser configurados como variáveis ou parâmetros abstratos.
12. **Acesso Unificado via AI Gateway:** Qualquer requisição a modelos de linguagem, visão ou áudio (Google Gemini, Anthropic Claude, OpenAI, OpenRouter ou modelos locais como Ollama) deve passar obrigatoriamente por uma camada centralizadora denominada **AI Gateway**.
13. **Registro Centralizado via Tool Registry:** Todas as ferramentas do sistema devem ser registradas, catalogadas e validadas através de um **Tool Registry** tipado, contendo esquemas estritos e metadados de execução.
14. **Documentação Viva do Estado:** O estado de maturação, bugs identificados e cobertura do projeto devem permanecer documentados de forma canônica no diretório `docs/`.
15. **Registro de Decisões Arquiteturais (ADRs):** Toda e qualquer decisão arquitetural relevante deve ser formalizada em `docs/DECISIONS.md`, explicitando contexto, opções avaliadas, decisão e consequências.
16. **Testabilidade Obrigatória:** Toda fase de implementação importante deve ser acompanhada de testes unitários ou de integração automatizados.
17. **Preservação de Funcionalidades:** Nenhuma funcionalidade existente deve ser removida sem justificativa técnica documentada e alinhada previamente com o usuário.
18. **Preservação da Identidade Visual:** A estética futurista, o HUD holográfico e a paleta visual desenvolvida em PyQt6 e WebGL/Three.js devem ser rigorosamente preservadas durante quaisquer refatorações estruturais de backend.
19. **Rigor na Classificação de Status:** O agente deve classificar o estado dos componentes com honestidade técnica estrita, utilizando exclusivamente os rótulos canônicos:
    - `[FUNCTIONAL]`: Código completo, testado, dependências atendidas e operacional em runtime.
    - `[PARTIAL]`: Funcionalidade operando sob limitações, fallbacks parciais ou dependente de reparos secundários.
    - `[MOCK]`: Interface presente, mas com dados fictícios hardcoded sem comunicação real com o alvo.
    - `[STUB]`: Esqueleto de função/classe sem corpo ou retornando valores estáticos de preenchimento.
    - `[BROKEN]`: Código com erros de sintaxe, imports ausentes, modelos inexistentes ou exceções fatais em runtime.
    - `[NOT IMPLEMENTED]`: Funcionalidade apenas planejada ou conceituada, sem código executável.
20. **Proibição de Suposições:** Diante de incerteza, ausência de contexto ou ambiguidade, o agente **NÃO DEVE INVENTAR**. Deve inspecionar os arquivos, validar evidências e, se necessário, questionar o usuário.

---

## 2. Modelo de Trabalho Obrigatório

Toda intervenção de engenharia no projeto ULTRON seguirá sem exceção o fluxo linear:

$$\text{ANALYZE} \longrightarrow \text{PLAN} \longrightarrow \text{IMPLEMENT} \longrightarrow \text{TEST} \longrightarrow \text{VERIFY} \longrightarrow \text{REPORT}$$

- **ANALYZE:** Inspeção do código existente, identificação de dependências e mapeamento de riscos.
- **PLAN:** Estruturação do plano cirúrgico em passos pequenos, verificáveis e com critério de rollback.
- **IMPLEMENT:** Aplicação precisa da alteração apenas nos arquivos delimitados.
- **TEST:** Execução de testes automatizados ou checagem estática para validar a modificação.
- **VERIFY:** Confirmação de que nenhuma regressão foi introduzida no ecossistema adjacente.
- **REPORT:** Apresentação clara do que foi realizado, como testar e próximos passos.

**Conduta Estritamente Proibida:**
$$\text{ANALYZE} \longrightarrow \text{ALTERAR TUDO}$$

---

## 3. Arquitetura de Destino

O projeto ULTRON evoluirá progressivamente para a seguinte topologia de camadas desacopladas:

```text
       ┌────────────────────────┐
       │   UI (PyQt6 / WebGL)   │
       └───────────┬────────────┘
                   │ Eventos de I/O
                   ▼
       ┌────────────────────────┐
       │       Event Bus        │
       └───────────┬────────────┘
                   │ Ações & Intenções
                   ▼
       ┌────────────────────────┐
       │     Cognitive Core     │◄──────┐ Orquestração
       └─────┬────────────┬─────┘       │ & Raciocínio
             │            │             │
   Chamadas  │            │ Consultas   │
   de IA     ▼            ▼             │
┌──────────────┐   ┌────────────┐       │
│  AI Gateway  │   │   Memory   │       │
└──────────────┘   └────────────┘       │
             │                          │
             │ Despacho de Ferramentas  │
             ▼                          │
       ┌────────────────────────┐       │
       │     Tool Registry      │───────┘
       └───────────┬────────────┘
                   │ Validação de Risco & Permissão
                   ▼
       ┌────────────────────────┐
       │    Execution Guard     │
       └───────────┬────────────┘
                   │ Execução Segura
                   ▼
       ┌────────────────────────┐
       │         Tools          │
       └───────────┬────────────┘
                   │
                   ▼
       ┌────────────────────────┐
       │   Devices / Services   │
       └────────────────────────┘
```
