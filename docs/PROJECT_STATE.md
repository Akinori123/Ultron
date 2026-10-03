# ESTADO REAL DO PROJETO ULTRON (PROJECT_STATE.md)

Este documento registra a radiografia canônica do estado real das funcionalidades do projeto ULTRON, classificadas com rigor técnico com base em inspeção estática do código, análise de dependências e verificação de fluxo.

---

## 1. Glossário de Classificação

- **`[FUNCTIONAL]`**: Código completo, testado, dependências atendidas e operacional em runtime sem quebras.
- **`[PARTIAL]`**: Funcionalidade operando sob limitações, fallbacks parciais, nomes de modelos a corrigir ou dependente de ajustes secundários.
- **`[MOCK]`**: Interface visual ou método presente, mas retornando dados fictícios estáticos hardcoded sem integração real.
- **`[STUB]`**: Estrutura básica/esqueleto de classe ou função sem lógica de negócio implementada.
- **`[BROKEN]`**: Código quebrado por imports faltantes, nomes de modelos inexistentes na API ou falhas fatais imediatas em runtime.
- **`[NOT IMPLEMENTED]`**: Funcionalidade apenas planejada ou conceituada, sem código presente no repositório.

---

## 2. Inventário por Subsistema

### 2.1 Subsistema de Voz (Audio & Speech)
| Componente | Arquivo de Origem | Status | Diagnóstico Técnico |
| :--- | :--- | :--- | :--- |
| **STT Cloud (Gemini Live)** | [main.py](file:///d:/Downloads/ultron/Ultron/main.py) | **`[FUNCTIONAL]`** | Streaming contínuo via WebSocket de PCM 16kHz mono. Depende de conexão ativa com a internet. |
| **STT Local (Offline)** | N/A | **`[NOT IMPLEMENTED]`** | Não há modelos de Whisper, Vosk ou Sherpa-ONNX locais integrados. Se a rede cair, o sistema não escuta. |
| **TTS Cloud (Gemini Live)** | [main.py](file:///d:/Downloads/ultron/Ultron/main.py) | **`[FUNCTIONAL]`** | Streaming nativo de áudio PCM 24kHz via `sounddevice.RawOutputStream`. Voz fluida e natural. |
| **TTS Fallback (Edge-TTS)** | [actions/attention_monitor.py](file:///d:/Downloads/ultron/Ultron/actions/attention_monitor.py) | **`[FUNCTIONAL]`** | Gera arquivos `.mp3` temporários via Microsoft Edge Online TTS e reproduz via Windows MCI (`mciSendStringW`). |
| **Interrupção de Fala (Barge-in)** | [main.py](file:///d:/Downloads/ultron/Ultron/main.py) | **`[FUNCTIONAL]`** | Esvaziamento instantâneo da fila de reprodução quando o modelo ou microfone detecta que o usuário interrompeu a fala. |
| **Supressão de Eco (EchoGuard)**| [core/echo.py](file:///d:/Downloads/ultron/Ultron/core/echo.py) | **`[FUNCTIONAL]`** | Medição de RMS e similaridade de texto para evitar que a própria voz do assistente seja retranscrita. |
| **Push-to-Talk (PTT)** | [core/hotkey.py](file:///d:/Downloads/ultron/Ultron/core/hotkey.py) | **`[FUNCTIONAL]`** | Tecla de atalho global para mutar/desmutar microfone sob demanda. |
| **Gestão de Dispositivos de Áudio**| [core/audio_devices.py](file:///d:/Downloads/ultron/Ultron/core/audio_devices.py) | **`[FUNCTIONAL]`** | Enumeração de microfones e alto-falantes WASAPI/MME no Windows com persistência de escolha. |

---

### 2.2 Subsistema de Visão Computacional (Vision)
| Componente | Arquivo de Origem | Status | Diagnóstico Técnico |
| :--- | :--- | :--- | :--- |
| **Captura de Tela (Screenshots)** | [actions/screen_processor.py](file:///d:/Downloads/ultron/Ultron/actions/screen_processor.py) | **`[FUNCTIONAL]`** | Captura multi-monitor via `PIL.ImageGrab` com fallback para `mss`. Conversão otimizada para JPEG. |
| **Captura de Câmera (Webcam)** | [actions/screen_processor.py](file:///d:/Downloads/ultron/Ultron/actions/screen_processor.py) | **`[FUNCTIONAL]`** | Captura via OpenCV (`cv2.VideoCapture`) com auto-detecção de índices de dispositivo de 0 a 5. |
| **Análise Visual da Tela/Câmera** | [actions/screen_processor.py](file:///d:/Downloads/ultron/Ultron/actions/screen_processor.py) | **`[BROKEN]`** | Tenta enviar a imagem para o modelo inexistente `"models/gemini-3.6-flash-native-audio-preview-12-2025"`. |
| **Reconhecimento de Gestos** | [gesture_utils.py](file:///d:/Downloads/ultron/Ultron/gesture_utils.py) | **`[FUNCTIONAL]`** | Classificador MediaPipe para 5 gestos: Palma (Play/Pause), Swipe (Mídia), Polegar (Volume), Paz (Print), Pinça (Mouse). |
| **Reconhecimento Facial Biométrico** | [core/haarcascade_frontalface_default.xml](file:///d:/Downloads/ultron/Ultron/core/haarcascade_frontalface_default.xml) | **`[NOT IMPLEMENTED]`** | Existe apenas detecção genérica de face para contar exercícios; não há identificação do dono. |
| **Contador de Exercícios Físicos** | [actions/pushup_counter.py](file:///d:/Downloads/ultron/Ultron/actions/pushup_counter.py) | **`[FUNCTIONAL]`** | Contagem de repetições por fluxo óptico e Haar cascade via webcam com feedback sonoro. |
| **Análise de Alimentos / Calorias** | [actions/calorie_counter.py](file:///d:/Downloads/ultron/Ultron/actions/calorie_counter.py) | **`[BROKEN]`** | Captura foto da refeição, mas chama `"gemini-3.6-flash"` na etapa de interpretação nutricional. |

---

### 2.3 Subsistema de Agente e Orquestração (Agent Core)
| Componente | Arquivo de Origem | Status | Diagnóstico Técnico |
| :--- | :--- | :--- | :--- |
| **Task Planner (Planejador)** | [agent/planner.py](file:///d:/Downloads/ultron/Ultron/agent/planner.py) | **`[BROKEN]`** | Depende de lista com modelos inexistentes (`gemini-3.1-flash-lite`, `gemini-3.5-flash`) e planeja ferramenta ausente `cmd_control`. |
| **Task Executor (Executor)** | [agent/executor.py](file:///d:/Downloads/ultron/Ultron/agent/executor.py) | **`[BROKEN]`** | Falha ao importar `actions.cmd_control` (`ModuleNotFoundError`); possui falha de segurança grave com execução de código Python livre. |
| **Fila de Tarefas (Task Queue)** | [agent/task_queue.py](file:///d:/Downloads/ultron/Ultron/agent/task_queue.py) | **`[FUNCTIONAL]`** | Fila thread-safe com prioridades (`LOW`, `NORMAL`, `HIGH`), flags de cancelamento e worker dedicado. |
| **Tratamento de Erros e Replanejamento** | [agent/error_handler.py](file:///d:/Downloads/ultron/Ultron/agent/error_handler.py) | **`[BROKEN]`** | Lógica estruturada excelente, mas chama modelo inexistente `gemini-3.1-flash-lite` para decidir retry/replan. |
| **Agente de Código Autônomo** | [actions/brahma_dev_agent.py](file:///d:/Downloads/ultron/Ultron/actions/brahma_dev_agent.py) | **`[PARTIAL]`** | Loop de desenvolvimento com ferramentas nativas; tenta modelo `gemini-3.6-flash` antes de cair no OpenRouter. |
| **Motor de Autocura (Auto-Heal)** | [actions/auto_heal_engine.py](file:///d:/Downloads/ultron/Ultron/actions/auto_heal_engine.py) | **`[BROKEN]`** | Analisador de traceback e gerador de patch estático; quebra ao tentar sintetizar código com `gemini-3.6-flash`. |

---

### 2.4 Subsistema de Ferramentas do Sistema Operacional (Windows Control)
| Componente | Arquivo de Origem | Status | Diagnóstico Técnico |
| :--- | :--- | :--- | :--- |
| **Abertura de Aplicativos** | [actions/open_app.py](file:///d:/Downloads/ultron/Ultron/actions/open_app.py) | **`[FUNCTIONAL]`** | Abertura ágil via pesquisa do Windows, atalhos do menu Iniciar e registro. |
| **Controle de Configurações (Settings)**| [actions/computer_settings.py](file:///d:/Downloads/ultron/Ultron/actions/computer_settings.py) | **`[FUNCTIONAL]`** | Volume (pycaw), brilho (WMI), Wi-Fi (netsh), bloqueio de tela e suspensão do Windows. |
| **Gerenciador de Processos** | [actions/system_manager.py](file:///d:/Downloads/ultron/Ultron/actions/system_manager.py) | **`[FUNCTIONAL]`** | Consulta telemetria de uso e encerra processos não responsivos via psutil. |
| **Manipulador de Arquivos (CRUD)** | [actions/file_controller.py](file:///d:/Downloads/ultron/Ultron/actions/file_controller.py) | **`[FUNCTIONAL]`** | Leitura, escrita, cópia, movimentação, exclusão segura e busca no disco local. |
| **Organizador de Área de Trabalho** | [actions/desktop_organizer_mcp.py](file:///d:/Downloads/ultron/Ultron/actions/desktop_organizer_mcp.py)| **`[FUNCTIONAL]`** | Agrupa arquivos por tipo ou data com suporte à reversão via `core/undo.py`. |
| **Manipulador de Desktop & Wallpaper** | [actions/desktop.py](file:///d:/Downloads/ultron/Ultron/actions/desktop.py) | **`[FUNCTIONAL]`** | Altera papel de parede via API nativa do Windows e gerencia ícones da área de trabalho. |
| **Comando de Terminal (`cmd_control`)** | `actions/cmd_control.py` | **`[BROKEN]`** | **Arquivo ausente no disco.** O executor quebra com `ModuleNotFoundError` ao tentar importá-lo. |
| **Lembretes Nativos do Windows** | [actions/reminder.py](file:///d:/Downloads/ultron/Ultron/actions/reminder.py) | **`[FUNCTIONAL]`** | Registra scripts sonoros `.pyw` no Agendador de Tarefas do Windows (`schtasks`). |
| **Barreira de Confirmação Humana** | [core/confirm.py](file:///d:/Downloads/ultron/Ultron/core/confirm.py) | **`[FUNCTIONAL]`** | Banner modal com timeout de 90s impedindo que a IA execute ações irreversíveis por conta própria. |
| **Pilha de Desfazer (Undo)** | [core/undo.py](file:///d:/Downloads/ultron/Ultron/core/undo.py) | **`[FUNCTIONAL]`** | Pilha LIFO de até 10 operações reversíveis com execução atômica sob comando do usuário. |

---

### 2.5 Documentação, Office e Web
| Componente | Arquivo de Origem | Status | Diagnóstico Técnico |
| :--- | :--- | :--- | :--- |
| **Geração de Apresentações (PPTX)** | [actions/office_builder.py](file:///d:/Downloads/ultron/Ultron/actions/office_builder.py) | **`[FUNCTIONAL]`** | Criação programática de slides profissionais via `python-pptx` com templates visuais. |
| **Geração de Planilhas (XLSX)** | [actions/office_builder.py](file:///d:/Downloads/ultron/Ultron/actions/office_builder.py) | **`[FUNCTIONAL]`** | Criação de planilhas formatadas, fórmulas e tabelas via `openpyxl`. |
| **Geração de Documentos Word (DOCX)**| [actions/docx_tools.py](file:///d:/Downloads/ultron/Ultron/actions/docx_tools.py) | **`[PARTIAL]`** | Geração via `python-docx` operacional; etapa de elaboração com IA tenta modelo inexistente. |
| **Geração de Relatórios PDF** | [actions/pdf_tools.py](file:///d:/Downloads/ultron/Ultron/actions/pdf_tools.py) | **`[FUNCTIONAL]`** | Criação de PDFs completos, estilizados e estruturados via `reportlab`. |
| **Navegação Web (Playwright)** | [actions/browser_control.py](file:///d:/Downloads/ultron/Ultron/actions/browser_control.py) | **`[FUNCTIONAL]`** | Automação robusta de browser com busca de executáveis locais (Chrome, Brave, Opera, Edge). |
| **Cliente Playwright MCP** | [actions/playwright_mcp_client.py](file:///d:/Downloads/ultron/Ultron/actions/playwright_mcp_client.py)| **`[FUNCTIONAL]`** | Integração via stdio JSON-RPC com o pacote `@playwright/mcp`. |
| **Construtor de Websites Estáticos** | [actions/website_builder.py](file:///d:/Downloads/ultron/Ultron/actions/website_builder.py) | **`[FUNCTIONAL]`** | Gera sites completos com servidor HTTP local embutido para visualização imediata. |
| **Pesquisa Web com Grounding** | [actions/web_search.py](file:///d:/Downloads/ultron/Ultron/actions/web_search.py) | **`[PARTIAL]`** | Gemini Google Search grounding tenta `gemini-3.6-flash`; fallback DuckDuckGo opera com sucesso. |
| **YouTube (Busca e Transcrição)** | [actions/youtube_video.py](file:///d:/Downloads/ultron/Ultron/actions/youtube_video.py) | **`[FUNCTIONAL]`** | Abre vídeos, pesquisa faixas e obtém legendas completas via `youtube-transcript-api`. |

---

### 2.6 Integrações Externas e Redes Sociais
| Componente | Arquivo de Origem | Status | Diagnóstico Técnico |
| :--- | :--- | :--- | :--- |
| **Android Gateway (Brahma Connect)** | [brahma_connect/](file:///d:/Downloads/ultron/Ultron/brahma_connect/) | **`[FUNCTIONAL]`** | Servidor FastAPI/WebSocket (porta 8765), pareamento QR Code e comunicação bidirecional com celular. |
| **App Android Nativo (Kotlin)** | [brahma-connect-android/](file:///d:/Downloads/ultron/Ultron/brahma-connect-android/) | **`[FUNCTIONAL]`** | Aplicativo nativo com serviço de acessibilidade, leitura de tela, toques remotos e notificações. |
| **Gmail (Leitura e Envio)** | [actions/google_workspace_mcp.py](file:///d:/Downloads/ultron/Ultron/actions/google_workspace_mcp.py)| **`[FUNCTIONAL]`** | Conexão real via IMAP/SMTP usando App Password criptografada com Fernet no disco. |
| **Google Calendar** | [actions/google_workspace_mcp.py](file:///d:/Downloads/ultron/Ultron/actions/google_workspace_mcp.py)| **`[MOCK]`** | Redireciona silenciosamente para o calendário JSON local; não sincroniza com o Google Calendar. |
| **Google Drive** | [actions/google_workspace_mcp.py](file:///d:/Downloads/ultron/Ultron/actions/google_workspace_mcp.py)| **`[MOCK]`** | Apenas copia arquivos para `Desktop\BrahmaAI` simulando um envio para a nuvem do Google. |
| **WhatsApp Desktop (Mensagens)** | [actions/send_message.py](file:///d:/Downloads/ultron/Ultron/actions/send_message.py) | **`[PARTIAL]`** | Automação cega por PyAutoGUI com `time.sleep()`. Altamente suscetível a erros de foco de janela. |
| **Instagram (DMs e Postagens)** | [actions/instagram_mcp.py](file:///d:/Downloads/ultron/Ultron/actions/instagram_mcp.py) | **`[PARTIAL]`** | Opera com `instagrapi` e browser headless; viola os termos da Meta com alto risco de bloqueio de conta. |
| **Spotify** | [actions/spotify_controller.py](file:///d:/Downloads/ultron/Ultron/actions/spotify_controller.py)| **`[PARTIAL]`** | Não usa a API oficial; envia teclas de mídia do Windows ou abre links de busca no Google Chrome. |
| **Discord Bot** | [discord_bot.py](file:///d:/Downloads/ultron/Ultron/discord_bot.py) | **`[FUNCTIONAL]`** | Conecta-se à API do Discord via WebSocket e permite controle do assistente remotamente. |
| **Smart Home - TP-Link Kasa** | [smart_home/providers/builtin.py](file:///d:/Downloads/ultron/Ultron/smart_home/providers/builtin.py)| **`[FUNCTIONAL]`** | Descoberta e controle real de dispositivos Kasa na rede local via protocolo UDP/TCP. |
| **Smart Home - Atomberg** | [smart_home/providers/builtin.py](file:///d:/Downloads/ultron/Ultron/smart_home/providers/builtin.py)| **`[FUNCTIONAL]`** | Integração real com API em nuvem para ventiladores de teto inteligentes. |
| **Smart Home - Outras Marcas** | [smart_home/providers/builtin.py](file:///d:/Downloads/ultron/Ultron/smart_home/providers/builtin.py)| **`[MOCK]`** | Philips Hue, LG ThinQ, Daikin, Tuya, Nest e SmartThings retornam listas estáticas fictícias. |
| **Home Assistant / MQTT** | N/A | **`[NOT IMPLEMENTED]`** | Nenhuma linha de código ou biblioteca de integração com Home Assistant ou MQTT existe no projeto. |

---

### 2.7 Memória e Persistência
| Componente | Arquivo de Origem | Status | Diagnóstico Técnico |
| :--- | :--- | :--- | :--- |
| **Memória de Longo Prazo** | [memory/memory_manager.py](file:///d:/Downloads/ultron/Ultron/memory/memory_manager.py) | **`[FUNCTIONAL]`** | Salva dados estruturados em JSON. Recuperação por casamento de palavras-chave (sem embeddings). |
| **Histórico de Conversas** | [workspace_store.py](file:///d:/Downloads/ultron/Ultron/workspace_store.py) | **`[FUNCTIONAL]`** | Banco SQLite com tabelas relacionais de conversas e mensagens. |
| **Regras Aprendidas do Usuário**| [core/learned_rules.py](file:///d:/Downloads/ultron/Ultron/core/learned_rules.py) | **`[FUNCTIONAL]`** | Grava regras e preferências comportamentais expressas em arquivo JSON. |
| **Busca Semântica / Vetorial** | N/A | **`[NOT IMPLEMENTED]`** | Não há banco vetorial (ChromaDB/FAISS); a memória não reconhece sinônimos ou conceitos correlatos. |

---

### 2.8 Interface, UX e Segurança
| Componente | Arquivo de Origem | Status | Diagnóstico Técnico |
| :--- | :--- | :--- | :--- |
| **HUD Holográfico PyQt6** | [ui.py](file:///d:/Downloads/ultron/Ultron/ui.py) | **`[FUNCTIONAL]`** | Interface complexa com dezenas de widgets estilizados e telemetria (porém contida em arquivo de 14k linhas). |
| **Fundo Holográfico 3D (WebGL)**| [assets/web_background/index.html](file:///d:/Downloads/ultron/Ultron/assets/web_background/index.html)| **`[PARTIAL]`** | Reator 3D Three.js operacional; scripts de eventos inline estão quebrados por estarem dentro de tags `<script src="...">`. |
| **Efeitos Sonoros Sci-Fi** | [sound_manager.py](file:///d:/Downloads/ultron/Ultron/sound_manager.py) | **`[FUNCTIONAL]`** | Síntese procedural de arquivos WAV caso estejam ausentes e reprodução via `QSoundEffect`. |
| **Armazenamento Seguro de Chaves**| [config/api_keys.json](file:///d:/Downloads/ultron/Ultron/config/api_keys.json) | **`[BROKEN]`** | **Risco crítico de segurança.** Chaves ativas de API gravadas em texto puro sem criptografia ou `.env`. |
| **Atualizador Automático** | [core/updater.py](file:///d:/Downloads/ultron/Ultron/core/updater.py) | **`[BROKEN]`** | **Risco crítico de destruição de código.** Executa `git reset --hard` contra repositório de terceiros. |
| **Cobertura de Testes** | [tests/](file:///d:/Downloads/ultron/Ultron/tests/) | **`[BROKEN]`** | Apenas 4 arquivos parciais de teste; dependem de `pytest` que não está instalado nem nas dependências. |
