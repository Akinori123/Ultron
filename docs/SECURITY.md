# POLÍTICA DE SEGURANÇA E MODELO DE AMEAÇAS (SECURITY.md)

Este documento estabelece o modelo de ameaças (*Threat Model*), os vetores de vulnerabilidade identificados no projeto ULTRON e as diretrizes permanentes de blindagem, gestão de credenciais e controle de execução.

---

## 1. Modelo de Ameaças (Threat Modeling)

Com base na auditoria estrutural do repositório, foram mapeados 8 vetores críticos de risco de segurança:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        MAPA DE AMEAÇAS DO ULTRON                       │
├────────────────────────────────────────────────────────────────────────┤
│ [Ameaça 1] Execução de Código Arbitrário (RCE no Host)                 │
│   → agent/executor.py executa código Python gerado por LLM via         │
│     subprocess.run sem sandbox ou validação de segurança.              │
├────────────────────────────────────────────────────────────────────────┤
│ [Ameaça 2] Destruição de Código via Git Reset Não Autorizado           │
│   → core/updater.py dispara 'git reset --hard' contra repo externo.    │
├────────────────────────────────────────────────────────────────────────┤
│ [Ameaça 3] Exposição e Vazamento de Credenciais em Texto Claro        │
│   → config/api_keys.json armazena chaves ativas do Gemini e OR no disco│
│   → config/.email_key armazena chave de criptografia na mesma pasta.   │
├────────────────────────────────────────────────────────────────────────┤
│ [Ameaça 4] Superfície de Rede Desprotegida (Bind 0.0.0.0)             │
│   → brahma_connect e dashboard escutam em todas as interfaces locais.  │
├────────────────────────────────────────────────────────────────────────┤
│ [Ameaça 5] Elevação Indiscriminada de Privilégios (Admin / UAC)        │
│   → bootstrap.ps1 auto-eleva para Administrador global no Windows.     │
├────────────────────────────────────────────────────────────────────────┤
│ [Ameaça 6] Injeção Indireta de Prompt (Indirect Prompt Injection)      │
│   → Conteúdos lidos da web, e-mails ou mensagens podem conter comandos │
│     maliciosos que forçam a IA a disparar ferramentas destrutivas.     │
├────────────────────────────────────────────────────────────────────────┤
│ [Ameaça 7] Automação Cega de Interface (Blind GUI Macros)              │
│   → send_message.py digita teclas às cegas em janelas de terceiros.    │
├────────────────────────────────────────────────────────────────────────┤
│ [Ameaça 8] Banimento de Contas por Violação de Termos (TOS Breach)     │
│   → instagram_mcp.py utiliza instagrapi e browser headless em login.   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Análise Detalhada dos Riscos Críticos

### 2.1 Execução de Código Arbitrário (RCE)
- **Local:** [agent/executor.py](file:///d:/Downloads/ultron/Ultron/agent/executor.py#L88) e [actions/auto_heal_engine.py](file:///d:/Downloads/ultron/Ultron/actions/auto_heal_engine.py#L396).
- **Mecanismo:** A IA é instruída a gerar código Python livre para resolver tarefas. O código é salvo em `%TEMP%` e executado no processo host através de `subprocess.run([sys.executable, tmp_path])`.
- **Risco:** Se o assistente for induzido via prompt injection ou falha de raciocínio a gerar comandos de exclusão (`shutil.rmtree`), roubo de dados ou download de binários, o sistema executará com todos os privilégios do usuário.
- **Mitigação Obrigatória:**
  1. Fim imediato da execução direta de scripts gerados por IA no processo host principal.
  2. Implementação de um ambiente de execução isolado (Sandbox com permissões de leitura apenas em pastas designadas, sem acesso de rede desnecessário e sem privilégios administrativos).
  3. Verificação de AST (Abstract Syntax Tree) para rejeitar imports de `os`, `subprocess`, `ctypes`, `shutil` quando a tarefa for matemática ou de processamento de texto.

### 2.2 Auto-Destruição via Updater
- **Local:** [core/updater.py](file:///d:/Downloads/ultron/Ultron/core/updater.py#L70).
- **Mecanismo:** Método `apply_update_and_restart()` executa:
  ```python
  subprocess.check_call(["git", "reset", "--hard", "origin/main"])
  ```
  apontando para `https://github.com/titechprabhasolutions/Brahma---personal.git`.
- **Risco:** Se disparado, descarta todo o código local não commitado e força o alinhamento com um repositório remoto divergente.
- **Mitigação Obrigatória:** Desativação completa do reset forçado. Atualizações devem ser notificadas ao usuário e nunca aplicadas via `reset --hard`.

### 2.3 Exposição de Credenciais
- **Local:** [config/api_keys.json](file:///d:/Downloads/ultron/Ultron/config/api_keys.json) e [config/email_credentials.json](file:///d:/Downloads/ultron/Ultron/config/email_credentials.json).
- **Mecanismo:** Chaves ativas salvas em JSON legível no disco.
- **Mitigação Obrigatória:**
  1. Substituição por variáveis de ambiente carregadas via arquivo `.env` (ignorado pelo Git).
  2. Armazenamento seguro de senhas no Windows via Windows Credential Manager ou Windows DPAPI (`CryptProtectData`).

### 2.4 Privilégios Excessivos no Windows
- **Local:** [bootstrap.ps1](file:///d:/Downloads/ultron/Ultron/bootstrap.ps1#L6).
- **Mecanismo:** O script de bootstrap força a elevação para Administrador (`runAs`). Com isso, todo o aplicativo e qualquer subprocesso derivado herdará nível de integridade alto (`High Integrity Level`).
- **Mitigação Obrigatória:** O ULTRON deve rodar sob nível de integridade padrão de usuário (*Medium Integrity Level*). Privilégios administrativos só devem ser solicitados pontualmente para tarefas que explicitamente exijam intervenção no sistema.

---

## 3. Classificação de Risco de Ferramentas (Risk Tiering)

Nenhuma ferramenta pode ser acionada pela IA sem passar pelo **Execution Guard**, que verifica a classificação de risco estrita:

| Nível de Risco | Definição | Exemplo de Ferramentas | Política de Execução |
| :--- | :--- | :--- | :--- |
| **Tier 0 (Inofensiva)** | Leitura estrita, sem alteração de estado no host ou rede externa. | `weather_report`, `system_manager` (status), `calendar_scheduler` (leitura). | **Execução Automática Imediata.** |
| **Tier 1 (Reversível)** | Modifica estado local, mas possui rollback imediato na pilha de desfazer (`core/undo.py`). | `computer_settings` (volume, brilho), `desktop_organizer` (mover arquivos), `desktop` (wallpaper). | **Execução Automática com Registro Obrigatório no Undo Stack.** |
| **Tier 2 (Externa/Compartilhamento)** | Envia dados do usuário para fora do computador ou realiza chamadas de rede externas. | `send_message`, `google_workspace` (envio de email), `browser_control` (navegação ativa). | **Notificação Visual/Auditiva no HUD antes da execução.** |
| **Tier 3 (Crítica/Irreversível)** | Operações destrutivas, exclusão permanente de arquivos, encerramento do SO ou comandos de terminal. | `file_controller` (delete permanente), `computer_settings` (shutdown/reboot), `cmd_control` (bash/terminal). | **BLOQUEIO OBRIGATÓRIO.** Exige aprovação humana explícita no portal de confirmação (`core/confirm.py`) com timeout de 90s. |

---

## 4. Política de Rede e Servidores Locais

1. **Bind Restrito por Padrão:** Por padrão, qualquer servidor web ou WebSocket (dashboard e gateway mobile) deve realizar bind em `127.0.0.1` (localhost).
2. **Bind em 0.0.0.0 Apenas com Autenticação Forte:** Caso o usuário ative o acesso de dispositivos da rede local (como o app Android), o servidor deve exigir:
   - Pareamento prévio com chave efêmera trocada via QR Code na tela física do PC.
   - Assinatura criptográfica HMAC ou token de sessão SHA-256 em todas as mensagens WebSocket.
   - Bloqueio por força bruta (rate limiting por IP de origem).

---

## 5. Diretrizes Contra Injeção de Prompt Indireta

1. **Separação Rígida entre Instruções e Dados:** Dados não confiáveis provenientes da web (páginas raspadas, resumos de notícias, transcrições de vídeos do YouTube ou e-mails recebidos) devem ser delimitados dentro de tags XML estritas (ex.: `<external_untrusted_data>...</external_untrusted_data>`).
2. **Defesa em Camadas:** O prompt de sistema mestre deve orientar o modelo a nunca acionar ferramentas críticas (Tier 2 e 3) em resposta a instruções contidas dentro de dados externos não confiáveis.
