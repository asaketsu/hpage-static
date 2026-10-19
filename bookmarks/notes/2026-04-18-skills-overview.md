# 🐱 猫仔 Skills 全览

> **共 242 个 Skills · 23 个分类 · 更新于 2026-04-18**

> 每个 skill 的功能简介从 SKILL.md 的 description 字段自动提取。

---

## 📋 分类索引

| # | 分类 | 数量 | 占比 |
|---|------|------|------|
| 1 | 🔴 安全攻防 (Red Teaming) | 102 | 42.1% |
| 2 | 🧠 ML/AI 工程 (MLOps) | 22 | 9.1% |
| 3 | 🔧 运维管理 (DevOps) | 22 | 9.1% |
| 4 | 📄 办公效率 (Productivity) | 19 | 7.9% |
| 5 | 🎨 创意内容 (Creative) | 14 | 5.8% |
| 6 | 💻 软件开发 (Software Development) | 11 | 4.5% |
| 7 | 🔬 学术研究 (Research) | 10 | 4.1% |
| 8 | 🐙 GitHub 协作 (GitHub) | 7 | 2.9% |
| 9 | 👥 团队角色 (Team Roles) | 5 | 2.1% |
| 10 | 📥 外部导入 (OpenClaw Imports) | 5 | 2.1% |
| 11 | 🎬 媒体处理 (Media) | 5 | 2.1% |
| 12 | 🍎 Apple 生态 (Apple) | 4 | 1.7% |
| 13 | 🤖 自主 Agent (Autonomous AI Agents) | 4 | 1.7% |
| 14 | 🎮 游戏 (Gaming) | 2 | 0.8% |
| 15 | 🔌 MCP 协议 (MCP) | 2 | 0.8% |
| 16 | 📝 笔记管理 (Note Taking) | 1 | 0.4% |
| 17 | 🧪 内测 QA (Dogfood) | 1 | 0.4% |
| 18 | 📊 数据科学 (Data Science) | 1 | 0.4% |
| 19 | 📱 社交媒体 (Social Media) | 1 | 0.4% |
| 20 | 🏠 智能家居 (Smart Home) | 1 | 0.4% |
| 21 | 🎯 Logo 生成 (Logo Generator) | 1 | 0.4% |
| 22 | ☕ 休闲生活 (Leisure) | 1 | 0.4% |
| 23 | 📧 邮件管理 (Email) | 1 | 0.4% |
| | **总计** | **242** | **100%** |

---

## 🔴 安全攻防 (Red Teaming)

| # | Skill 名称 | 功能简介 |
|---|-----------|---------|
| 1 | `401-403-bypass-techniques` | 401/403 bypass playbook. Use when encountering access-denied responses on admin panels, API endpo... |
| 2 | `active-directory-acl-abuse` | Active Directory ACL abuse playbook. Use when exploiting misconfigured AD permissions including G... |
| 3 | `active-directory-certificate-services` | AD Certificate Services attack playbook. Use when targeting misconfigured AD CS for privilege esc... |
| 4 | `active-directory-kerberos-attacks` | Kerberos attack playbook for Active Directory. Use when targeting AD authentication via AS-REP ro... |
| 5 | `ai-ml-security` | AI/ML security playbook. Use when assessing model supply chain attacks (pickle RCE, poisoned weig... |
| 6 | `android-pentesting-tricks` | Android pentesting playbook. Use when testing Android applications for SSL pinning bypass, export... |
| 7 | `anti-debugging-techniques` | Anti-debugging detection and bypass playbook. Use when reversing protected binaries that detect d... |
| 8 | `api-auth-and-jwt-abuse` | API authentication and JWT abuse playbook. Use when testing bearer tokens, API keys, claim trust,... |
| 9 | `api-authorization-and-bola` | API authorization and BOLA testing playbook. Use when APIs expose object identifiers, nested reso... |
| 10 | `api-recon-and-docs` | API reconnaissance and documentation review playbook. Use when discovering endpoints, schemas, ve... |
| 11 | `api-sec` | Entry P1 category router for API security. Use when choosing between API recon, authorization, to... |
| 12 | `arbitrary-write-to-rce` | Arbitrary write to RCE playbook. Use when you have an arbitrary write primitive (from heap exploi... |
| 13 | `auth-sec` | Entry P1 category router for authentication and authorization. Use when testing login flows, sess... |
| 14 | `authbypass-authentication-flaws` | Authentication bypass testing playbook. Use when assessing login flows, password reset logic, acc... |
| 15 | `binary-protection-bypass` | Binary protection bypass playbook. Use when identifying and bypassing ASLR, PIE, NX/DEP, stack ca... |
| 16 | `browser-exploitation-v8` | Browser and V8 exploitation playbook. Use when exploiting JavaScript engine vulnerabilities inclu... |
| 17 | `business-logic-vuln` | Entry P1 category router for business logic testing. Use when workflow abuse, race conditions, pr... |
| 18 | `business-logic-vulnerabilities` | Business logic vulnerability playbook. Use when reasoning about workflows, race conditions, price... |
| 19 | `classical-cipher-analysis` | Classical cipher analysis playbook. Use when encountering substitution ciphers, Vigenere, transpo... |
| 20 | `clickjacking` | Clickjacking playbook. Use when testing whether target pages can be framed, whether X-Frame-Optio... |
| 21 | `cmdi-command-injection` | Command injection playbook. Use when user input may reach shell commands, process execution, conv... |
| 22 | `code-obfuscation-deobfuscation` | Code obfuscation analysis and deobfuscation playbook. Use when reversing binaries protected by ju... |
| 23 | `container-escape-techniques` | Container escape playbook. Use when operating inside a Docker container, LXC, or Kubernetes pod a... |
| 24 | `cors-cross-origin-misconfiguration` | CORS misconfiguration testing playbook. Use when analyzing cross-origin trust, credentialed brows... |
| 25 | `crlf-injection` | CRLF injection playbook. Use when user input reaches HTTP response headers, Location redirects, S... |
| 26 | `csp-bypass-advanced` | Advanced Content Security Policy bypass techniques. Use when XSS or data exfiltration is blocked ... |
| 27 | `csrf-cross-site-request-forgery` | CSRF testing playbook. Use when reviewing state-changing web flows, anti-CSRF defenses, SameSite ... |
| 28 | `csv-formula-injection` | CSV/spreadsheet formula injection (DDE, Excel/LibreOffice, Google Sheets IMPORT*). Use when expor... |
| 29 | `dangling-markup-injection` | Dangling markup injection playbook. Use when HTML injection is possible but JavaScript execution ... |
| 30 | `defi-attack-patterns` | DeFi attack pattern playbook. Use when analyzing flash loan attacks, price oracle manipulation, M... |
| 31 | `dependency-confusion` | Supply-chain testing via package-manager dependency confusion: when internal package names resolv... |
| 32 | `deserialization-insecure` | Insecure deserialization playbook. Use when Java, PHP, or Python applications deserialize untrust... |
| 33 | `dns-rebinding-attacks` | DNS rebinding attack playbook. Use when testing applications that trust DNS resolution for origin... |
| 34 | `email-header-injection` | Email header injection and spoofing playbook. Use when testing contact forms, email APIs, passwor... |
| 35 | `expression-language-injection` | Expression Language injection playbook. Use when Java EL, SpEL, OGNL, or MVEL expressions may eva... |
| 36 | `file-access-vuln` | Entry P1 category router for file access and upload workflows. Use when testing download endpoint... |
| 37 | `format-string-exploitation` | Format string exploitation playbook. Use when printf-family functions receive user-controlled for... |
| 38 | `godmode` | "Jailbreak API-served LLMs using G0DM0D3 techniques — Parseltongue input obfuscation (33 techniqu... |
| 39 | `graphql-and-hidden-parameters` | GraphQL and hidden parameter testing playbook. Use when exploring introspection, batching, undocu... |
| 40 | `hack` | Entry P0 primary router for HackSkills. Use when the task involves web application testing, API s... |
| 41 | `hash-attack-techniques` | Hash attack playbook. Use when exploiting length extension, MD5/SHA1 collisions, HMAC timing leak... |
| 42 | `heap-exploitation` | Heap exploitation playbook. Use when targeting ptmalloc2/glibc heap vulnerabilities including UAF... |
| 43 | `http-host-header-attacks` | HTTP Host header injection and routing abuse playbook. Use when the application trusts the Host h... |
| 44 | `http-parameter-pollution` | HTTP Parameter Pollution (HPP): duplicate query/body keys parsed differently by servers, proxies,... |
| 45 | `http2-specific-attacks` | HTTP/2 protocol-specific attack playbook. Use when the target supports HTTP/2 and you need to exp... |
| 46 | `idor-broken-object-authorization` | IDOR and broken object authorization testing playbook. Use when requests expose object identifier... |
| 47 | `injection-checking` | Entry P1 category router for injection testing. Use when routing between XSS, SQLi, SSRF, XXE, SS... |
| 48 | `insecure-source-code-management` | Source control and artifact exposure (.git, .svn, .hg, backups, .env). Use when recon finds VCS p... |
| 49 | `ios-pentesting-tricks` | iOS pentesting playbook. Use when testing iOS applications for keychain extraction, URL scheme hi... |
| 50 | `jndi-injection` | JNDI injection playbook. Use when Java applications perform JNDI lookups with attacker-controlled... |
| 51 | `jwt-oauth-token-attacks` | JWT and OAuth token attack playbook. Use when validating token trust, signing algorithms, key han... |
| 52 | `kernel-exploitation` | Linux kernel exploitation playbook. Use when exploiting kernel vulnerabilities (UAF, OOB, race co... |
| 53 | `kubernetes-pentesting` | Kubernetes penetration testing playbook. Use when targeting Kubernetes clusters via API server, R... |
| 54 | `lattice-crypto-attacks` | Lattice-based cryptanalysis playbook. Use when attacking RSA via Coppersmith small roots, recover... |
| 55 | `linux-lateral-movement` | Linux lateral movement playbook. Use after gaining initial access to pivot across Linux hosts via... |
| 56 | `linux-privilege-escalation` | Linux privilege escalation playbook. Use when you have low-privilege shell access and need to esc... |
| 57 | `linux-security-bypass` | Linux security mechanism bypass playbook. Use when facing restricted bash/rbash, read-only or noe... |
| 58 | `llm-prompt-injection` | LLM prompt injection playbook. Use when testing AI/LLM applications for direct injection, indirec... |
| 59 | `macos-process-injection` | macOS process injection playbook. Use when you need to inject code into running or launching macO... |
| 60 | `macos-security-bypass` | macOS security bypass playbook. Use when targeting macOS endpoints and need to bypass TCC, Gateke... |
| 61 | `memory-forensics-volatility` | Memory forensics playbook using Volatility 2/3. Use when analyzing memory dumps for malware analy... |
| 62 | `mobile-ssl-pinning-bypass` | Mobile SSL pinning bypass playbook. Use when intercepting HTTPS traffic from mobile applications ... |
| 63 | `network-protocol-attacks` | Network protocol attack playbook. Use when exploiting layer 2/3 protocols including ARP spoofing,... |
| 64 | `nosql-injection` | NoSQL injection playbook. Use when MongoDB-style operators, JSON query objects, flexible search f... |
| 65 | `ntlm-relay-coercion` | NTLM relay and authentication coercion playbook. Use when capturing and relaying NTLM authenticat... |
| 66 | `oauth-oidc-misconfiguration` | OAuth and OIDC misconfiguration testing playbook. Use when reviewing redirect URI handling, state... |
| 67 | `open-redirect` | Open redirect playbook. Use when URL parameters, form actions, or JavaScript sinks control naviga... |
| 68 | `path-traversal-lfi` | Path traversal and LFI playbook. Use when file paths, download endpoints, include operations, arc... |
| 69 | `prototype-pollution` | Prototype pollution testing for JavaScript stacks. Use when user input is merged into objects (qu... |
| 70 | `prototype-pollution-advanced` | Advanced prototype pollution playbook — server-side RCE, client-side gadgets, filter bypasses, an... |
| 71 | `race-condition` | Race condition and TOCTOU testing for web apps. Use when testing one-time operations, concurrent ... |
| 72 | `recon-and-methodology` | Reconnaissance and methodology playbook. Use when mapping assets, discovering endpoints, fingerpr... |
| 73 | `recon-for-sec` | Entry P1 category router for reconnaissance and methodology. Use when mapping scope, discovering ... |
| 74 | `request-smuggling` | HTTP request smuggling and desynchronization testing. Use when front proxies, CDNs, or load balan... |
| 75 | `reverse-shell-techniques` | Reverse shell techniques playbook. Use when establishing remote shells including language one-lin... |
| 76 | `rsa-attack-techniques` | RSA attack playbook for CTF and real-world cryptanalysis. Use when given RSA parameters (n, e, c)... |
| 77 | `saml-sso-assertion-attacks` | SAML SSO assertion attack playbook. Use when testing signature validation, assertion wrapping, au... |
| 78 | `sandbox-escape-techniques` | Sandbox escape playbook. Use when breaking out of Python sandbox, Lua sandbox, seccomp filter, ch... |
| 79 | `smart-contract-vulnerabilities` | Smart contract vulnerability playbook. Use when auditing Solidity/EVM contracts for reentrancy, i... |
| 80 | `sqli-sql-injection` | SQL injection playbook. Use when input reaches SQL queries, authentication logic, sorting, filter... |
| 81 | `ssrf-server-side-request-forgery` | SSRF playbook. Use when the server fetches URLs, resolves hostnames, imports remote content, or c... |
| 82 | `ssti-server-side-template-injection` | SSTI playbook. Use when template expressions, server-side rendering, preview features, or templat... |
| 83 | `stack-overflow-and-rop` | Stack overflow and ROP playbook. Use when exploiting buffer overflows to hijack control flow via ... |
| 84 | `steganography-techniques` | Steganography detection and extraction playbook. Use when analyzing images (LSB, PNG chunks, JPEG... |
| 85 | `subdomain-takeover` | Subdomain takeover detection and exploitation playbook. Use when targets have dangling CNAME/NS/M... |
| 86 | `symbolic-execution-tools` | Symbolic execution and constraint solving playbook. Use when solving CTF reversing challenges, re... |
| 87 | `symmetric-cipher-attacks` | Symmetric cipher attack playbook. Use when exploiting block cipher mode weaknesses (CBC padding o... |
| 88 | `traffic-analysis-pcap` | Traffic analysis and PCAP forensics playbook. Use when analyzing network captures including Wires... |
| 89 | `tunneling-and-pivoting` | Tunneling and pivoting playbook. Use when establishing network tunnels through compromised hosts ... |
| 90 | `type-juggling` | PHP type juggling and weak comparison (`==`) bypass. Use when authentication, HMAC/signature chec... |
| 91 | `unauthorized-access-common-services` | Unauthorized access playbook for common exposed services. Use when Redis, Rsync, PHP-FPM, AJP/Gho... |
| 92 | `upload-insecure-files` | Insecure file upload playbook. Use when testing upload validation, storage paths, processing pipe... |
| 93 | `vm-and-bytecode-reverse` | Custom VM and bytecode reverse engineering playbook. Use when CTF challenges or protected softwar... |
| 94 | `waf-bypass-techniques` | WAF bypass methodology and generic evasion techniques. Use when a web application firewall blocks... |
| 95 | `web-cache-deception` | Web cache deception and poisoning playbook. Use when CDN, reverse proxy, or application caching m... |
| 96 | `websocket-security` | WebSocket handshake, CSWSH, tooling (wsrepl, ws-harness, Burp), and common flaws. Use when apps u... |
| 97 | `windows-av-evasion` | AV/EDR evasion playbook for Windows. Use when bypassing AMSI, ETW, .NET assembly detection, shell... |
| 98 | `windows-lateral-movement` | Windows lateral movement playbook. Use when pivoting between Windows hosts via PsExec, WMI, WinRM... |
| 99 | `windows-privilege-escalation` | Windows local privilege escalation playbook. Use when you have low-privilege shell access on Wind... |
| 100 | `xslt-injection` | XSLT injection testing: processor fingerprinting, XXE and document() SSRF, EXSLT write primitives... |
| 101 | `xss-cross-site-scripting` | XSS playbook. Use when user-controlled content reaches HTML, attributes, JavaScript, DOM sinks, u... |
| 102 | `xxe-xml-external-entity` | XXE playbook. Use when XML, SVG, OOXML, SOAP, or parser-driven imports may resolve external entit... |

## 🧠 ML/AI 工程 (MLOps)

| # | Skill 名称 | 功能简介 |
|---|-----------|---------|
| 1 | `audiocraft-audio-generation` | PyTorch library for audio generation including text-to-music (MusicGen) and text-to-sound (AudioG... |
| 2 | `axolotl` | Expert guidance for fine-tuning LLMs with Axolotl - YAML configs, 100+ models, LoRA/QLoRA, DPO/KT... |
| 3 | `clip` | OpenAI's model connecting vision and language. Enables zero-shot image classification, image-text... |
| 4 | `dspy` | Build complex AI systems with declarative programming, optimize prompts automatically, create mod... |
| 5 | `evaluating-llms-harness` | Evaluates LLMs across 60+ academic benchmarks (MMLU, HumanEval, GSM8K, TruthfulQA, HellaSwag). Us... |
| 6 | `fine-tuning-with-trl` | Fine-tune LLMs using reinforcement learning with TRL - SFT for instruction tuning, DPO for prefer... |
| 7 | `gguf-quantization` | GGUF format and llama.cpp quantization for efficient CPU/GPU inference. Use when deploying models... |
| 8 | `grpo-rl-training` | Expert guidance for GRPO/RL fine-tuning with TRL for reasoning and task-specific model training |
| 9 | `guidance` | Control LLM output with regex and grammars, guarantee valid JSON/XML/code generation, enforce str... |
| 10 | `huggingface-hub` | Hugging Face Hub CLI (hf) — search, download, and upload models and datasets, manage repos, query... |
| 11 | `llama-cpp` | Runs LLM inference on CPU, Apple Silicon, and consumer GPUs without NVIDIA hardware. Use for edge... |
| 12 | `modal-serverless-gpu` | Serverless GPU cloud platform for running ML workloads. Use when you need on-demand GPU access wi... |
| 13 | `obliteratus` | Remove refusal behaviors from open-weight LLMs using OBLITERATUS — mechanistic interpretability t... |
| 14 | `outlines` | Guarantee valid JSON/XML/code structure during generation, use Pydantic models for type-safe outp... |
| 15 | `peft-fine-tuning` | Parameter-efficient fine-tuning for LLMs using LoRA, QLoRA, and 25+ methods. Use when fine-tuning... |
| 16 | `pytorch-fsdp` | Expert guidance for Fully Sharded Data Parallel training with PyTorch FSDP - parameter sharding, ... |
| 17 | `segment-anything-model` | Foundation model for image segmentation with zero-shot transfer. Use when you need to segment any... |
| 18 | `serving-llms-vllm` | Serves LLMs with high throughput using vLLM's PagedAttention and continuous batching. Use when de... |
| 19 | `stable-diffusion-image-generation` | State-of-the-art text-to-image generation with Stable Diffusion models via HuggingFace Diffusers.... |
| 20 | `unsloth` | Expert guidance for fast fine-tuning with Unsloth - 2-5x faster training, 50-80% less memory, LoR... |
| 21 | `weights-and-biases` | Track ML experiments with automatic logging, visualize training in real-time, optimize hyperparam... |
| 22 | `whisper` | OpenAI's general-purpose speech recognition model. Supports 99 languages, transcription, translat... |

## 🔧 运维管理 (DevOps)

| # | Skill 名称 | 功能简介 |
|---|-----------|---------|
| 1 | `agent-health-check` | Agent 三维度健康自检 — 长期运行稳定性 + 工具调用效率 + 指令遵循质量。定期或按需运行，发现退化风险。 |
| 2 | `auto-dream` | Nightly system health scan and memory maintenance cron job. Scans memories, hooks, cron jobs, and... |
| 3 | `auto-memory-keeper` | Auto-capture hourly session highlights and update daily memory files. Keeps long-term memory cont... |
| 4 | `cron-bulk-management` | 批量管理 cron job 的模型分配、清除、迁移。cronjob tool 的限制及绕过方法。 |
| 5 | `doc-qa` | 通用文档质量校验 — 所有文档（PPT/DOCX/XLSX/PDF/HTML）输出前的自检层。检查格式、内容、排版、一致性，确保交付质量。 |
| 6 | `evening-summary` | Nightly summary cron job — cron completion analysis, system resources, error patterns, and daily ... |
| 7 | `evolution-control` | 进化审批与摘要系统 — memory 写入前的质量过滤与用户审批机制，以及进化摘要查询命令。解决自进化"噪音太多"和"不可控"的问题。 |
| 8 | `evolver` | Self-evolution engine for the cat system. Analyzes error logs, identifies recurring patterns, and... |
| 9 | `feishu-group-setup` | 在 Hermes Gateway 中配置飞书群组角色系统 — 多群多角色注入 |
| 10 | `free-image-generation` | Free image generation integration — Qwen Image (DashScope), Pollinations.ai, Google Gemini Image ... |
| 11 | `hermes-code-mod` | Modifying Hermes Agent core code — paths, gotchas, restart procedures. |
| 12 | `hermes-disaster-recovery` | Hermes Gateway 防灾容灾体系部署 — 进程守护、自动备份、健康检查、日志轮转、一键恢复 |
| 13 | `hermes-system-audit` | Systematic audit and optimization of a Hermes Agent installation — disk cleanup, memory verificat... |
| 14 | `memory-system` | 自研三层记忆恢复系统。解决session重启后"忘记一切"的问题，提供永久记忆、今日记忆、临时记忆的完整架构。 |
| 15 | `selective-proxy` | Inject HTTP proxy only for specific models (google/gemini-*) while keeping others direct. Config-... |
| 16 | `self-evolver` | 自进化引擎 — 错误自动发现→修复→沉淀为规则的闭环系统 |
| 17 | `skill-optimizer` | 技能自我迭代系统。定期评估现有 skill 的效果，自动优化低效 skill，淘汰废弃 skill。确保每个 skill 都在最佳状态运行。Use when: 周度 skill 审计、skill... |
| 18 | `system-info` | 无描述 |
| 19 | `watchdog` | Monitor all OpenClaw cron jobs for failures and auto-fix common errors (model-not-allowed, timeou... |
| 20 | `webhook-subscriptions` | Create and manage webhook subscriptions for event-driven agent activation. Use when the user want... |
| 21 | `weixin-markdown-fix` | Fix WeChat black block/garbled text caused by unconverted Markdown block elements |
| 22 | `zai-quota-monitor` | 无描述 |

## 📄 办公效率 (Productivity)

| # | Skill 名称 | 功能简介 |
|---|-----------|---------|
| 1 | `bookmark-reader` | 无描述 |
| 2 | `google-workspace` | Gmail, Calendar, Drive, Contacts, Sheets, and Docs integration for Hermes. Uses Hermes-managed OA... |
| 3 | `linear` | Manage Linear issues, projects, and teams via the GraphQL API. Create, update, search, and organi... |
| 4 | `nano-pdf` | Edit PDFs with natural-language instructions using the nano-pdf CLI. Modify text, fix typos, upda... |
| 5 | `news-aggregator` | 新闻聚合技能 — 从多个中文源抓取新闻，分类整理输出 |
| 6 | `note-dual-format` | 笔记双格式输出 — 同时生成 Markdown (.md) + 微信公众号风格 HTML (.html)。所有 bookmarks/notes 笔记必须遵循此工作流。 |
| 7 | `notion` | Notion API for creating and managing pages, databases, and blocks via curl. Search, create, updat... |
| 8 | `ocr-and-documents` | Extract text from PDFs and scanned documents. Use web_extract for remote URLs, pymupdf for local ... |
| 9 | `office-pipeline` | Office 文档联动生成 — 一个指令同时输出 PPT + DOCX + XLSX 多种格式。调研报告一键出全套材料。 |
| 10 | `powerpoint` | "Use this skill any time a .pptx file is involved in any way — as input, output, or both. This in... |
| 11 | `quant-trading` | 金融量化分析 — A股行情、技术指标、策略回测、Kronos预测、量能识别、风控预警、自动盯盘 |
| 12 | `reading-notes` | 无描述 |
| 13 | `summarize-pro` | 多格式摘要技能 — 网页/PDF/文本智能摘要，支持多种输出格式 |
| 14 | `weather` | 天气查询技能 — 支持中文城市名，返回简洁天气信息 |
| 15 | `wechat-article-extract-tavily` | 用 Tavily Extract API 抓取微信公众号文章内容，绕过反爬验证码 |
| 16 | `wechat-pb` | 微信公众号 Markdown 排版与发布工具 — 主题渲染、AI 内容增强、一键推送到草稿箱 |
| 17 | `weibo-hot-search` | 抓取微博热搜榜 Top N 话题的可靠方法 |
| 18 | `weixin-article-extract` | 提取微信公众号文章标题/作者/摘要 — 绕过反爬验证的实用方法 |
| 19 | `xlsx-generator` | 专业 XLSX 文件生成 — 用 openpyxl 生成带格式、图表、公式、条件格式的 Excel 文件。支持数据报告、财务报表、项目管理表等场景。 |

## 🎨 创意内容 (Creative)

| # | Skill 名称 | 功能简介 |
|---|-----------|---------|
| 1 | `architecture-diagram` | Generate dark-themed SVG diagrams of software systems and cloud infrastructure as standalone HTML... |
| 2 | `ascii-art` | Generate ASCII art using pyfiglet (571 fonts), cowsay, boxes, toilet, image-to-ascii, remote APIs... |
| 3 | `ascii-video` | "Production pipeline for ASCII art video — any format. Converts video/audio/images/generative inp... |
| 4 | `document-illustrator` | 基于文档内容自动生成配图。AI 智能分析文档结构，归纳核心要点， 为每个主题生成符合特定风格的配图。支持封面图生成和自定义图片比例。 使用场景：当用户需要为文档、文章、笔记生成配图时。 关键词：... |
| 5 | `excalidraw` | Create hand-drawn style diagrams using Excalidraw JSON format. Generate .excalidraw files for arc... |
| 6 | `html-slides` | "生成零依赖、动画丰富的 HTML 演示文稿。单文件输出（内联 CSS/JS），支持从零创建、PPT 转换、风格预览选择。当用户要求做 PPT/演示文稿/slides/deck 时触发。" |
| 7 | `humanizer` | 去 AI 痕迹润色 — 让 AI 生成的文本更自然、更口语化 |
| 8 | `ideation` | "Generate project ideas through creative constraints. Use when the user says 'I want to build som... |
| 9 | `manim-video` | "Production pipeline for mathematical and technical animations using Manim Community Edition. Cre... |
| 10 | `p5js` | "Production pipeline for interactive and generative visual art using p5.js. Creates browser-based... |
| 11 | `popular-web-designs` | 54 production-quality design systems extracted from real websites. Load a template to generate HT... |
| 12 | `ppt-generator` | 无描述 |
| 13 | `songwriting-and-ai-music` | Songwriting craft, AI music generation prompts (Suno focus), parody/adaptation techniques, phonet... |
| 14 | `video-generator` | 无描述 |

## 💻 软件开发 (Software Development)

| # | Skill 名称 | 功能简介 |
|---|-----------|---------|
| 1 | `auto-skill` | 任务完成后自动评估是否值得生成 Skill，值得则自动创建 SKILL.md 并写入记忆索引。实现 Hermes 式的 execute→extract→refine→retrieve 闭环。Us... |
| 2 | `experience-bank` | 经验自动沉淀系统。每次解决问题的方法自动归类为经验卡片，下次遇到类似问题直接匹配复用。与 evolver 联动，错误→修复→经验→规则闭环。Use when: 任务完成时自动触发、遇到已知问题时... |
| 3 | `plan` | Plan mode for Hermes — inspect context, write a markdown plan into the active workspace's `.herme... |
| 4 | `planning-with-files` | Implements Manus-style file-based planning to organize and track progress on complex tasks. Creat... |
| 5 | `proactive-agent` | "Transform AI agents from task-followers into proactive partners that anticipate needs and contin... |
| 6 | `requesting-code-review` | Pre-commit verification pipeline — static security scan, baseline-aware quality gates, independen... |
| 7 | `subagent-driven-development` | Use when executing implementation plans with independent tasks. Dispatches fresh delegate_task pe... |
| 8 | `systematic-debugging` | Use when encountering any bug, test failure, or unexpected behavior. 4-phase root cause investiga... |
| 9 | `task-executor` | Standardized 6-step execution SOP for complex tasks. Ensures traceable, repeatable, and auditable... |
| 10 | `test-driven-development` | Use when implementing any feature or bugfix, before writing implementation code. Enforces RED-GRE... |
| 11 | `writing-plans` | Use when you have a spec or requirements for a multi-step task. Creates comprehensive implementat... |

## 🔬 学术研究 (Research)

| # | Skill 名称 | 功能简介 |
|---|-----------|---------|
| 1 | `arxiv` | Search and retrieve academic papers from arXiv using their free REST API. No API key needed. Sear... |
| 2 | `auto-learner` | 主动知识获取引擎。自动搜索前沿领域、深度学习、形成笔记和规则。与 sniff-interests.md 联动，按领域等级决定探索深度。每日运行，产出保存到 explore/ 和 rules/。U... |
| 3 | `blogwatcher` | Monitor blogs and RSS/Atom feeds for updates using the blogwatcher-cli tool. Add blogs, scan for ... |
| 4 | `deep-analysis` | 结构化深度分析 — 多源检索→交叉验证→结构化归纳→生成带引用的深度报告。行业调研、竞品分析、技术路线梳理的标准化框架。 |
| 5 | `hybrid-search` | Hybrid semantic + keyword search over local notes. Activate when user asks to search notes, find ... |
| 6 | `llm-wiki` | "Karpathy's LLM Wiki — build and maintain a persistent, interlinked markdown knowledge base. Inge... |
| 7 | `persona-modeler` | 人物思维建模 — 输入人名→多源调研→提炼决策模型/表达DNA/心智模型→生成可复用的 persona skill。类似 AutoClaw 女娲 Skill。 |
| 8 | `polymarket` | Query Polymarket prediction market data — search markets, get prices, orderbooks, and price histo... |
| 9 | `research-paper-writing` | End-to-end pipeline for writing ML/AI research papers — from experiment design through analysis, ... |
| 10 | `scholar-assist` | 论文全链路助手 — 检索、阅读、摘要、翻译、引用 |

## 🐙 GitHub 协作 (GitHub)

| # | Skill 名称 | 功能简介 |
|---|-----------|---------|
| 1 | `codebase-inspection` | Inspect and analyze codebases using pygount for LOC counting, language breakdown, and code-vs-com... |
| 2 | `critical-code-reviewer` | Conduct rigorous, adversarial code reviews with zero tolerance for mediocrity. Use when users ask... |
| 3 | `github-auth` | Set up GitHub authentication for the agent using git (universally available) or the gh CLI. Cover... |
| 4 | `github-code-review` | Review code changes by analyzing git diffs, leaving inline comments on PRs, and performing thorou... |
| 5 | `github-issues` | Create, manage, triage, and close GitHub issues. Search existing issues, add labels, assign peopl... |
| 6 | `github-pr-workflow` | Full pull request lifecycle — create branches, commit changes, open PRs, monitor CI status, auto-... |
| 7 | `github-repo-management` | Clone, create, fork, configure, and manage GitHub repositories. Manage remotes, secrets, releases... |

## 👥 团队角色 (Team Roles)

| # | Skill 名称 | 功能简介 |
|---|-----------|---------|
| 1 | `content-meow` | 内容喵 — 内容创作专家，负责文案、文章、营销内容 |
| 2 | `jbot-meow` | 猫仔（jbot）— 团队协调者，接单→评估→分配或自完成 |
| 3 | `data-meow` | 分析喵 — 数据分析师，负责数据分析、可视化、信号检测 |
| 4 | `dev-meow` | 开发喵 — 首席软件架构师，负责编码、调试、系统设计 |
| 5 | `opm-meow` | 运营喵 — 运营经理，负责项目管理、优先级、团队协调 |

## 📥 外部导入 (OpenClaw Imports)

| # | Skill 名称 | 功能简介 |
|---|-----------|---------|
| 1 | `gog` | Google Workspace CLI for Gmail, Calendar, Drive, Contacts, Sheets, and Docs. |
| 2 | `memos-memory-guide` | "Use the MemOS Local memory system to search and use the user's past conversations. Use this skil... |
| 3 | `self-improvement` | "Captures learnings, errors, and corrections to enable continuous improvement. Use when: (1) A co... |
| 4 | `skill-vetter` | Security-first skill vetting for AI agents. Use before installing any skill from ClawdHub, GitHub... |
| 5 | `summarize` | Summarize URLs or files with the summarize CLI (web, PDFs, images, audio, YouTube). |

## 🎬 媒体处理 (Media)

| # | Skill 名称 | 功能简介 |
|---|-----------|---------|
| 1 | `gif-search` | Search and download GIFs from Tenor using curl. No dependencies beyond curl and jq. Useful for fi... |
| 2 | `heartmula` | Set up and run HeartMuLa, the open-source music generation model family (Suno-like). Generates fu... |
| 3 | `openrouter-transcribe` | Transcribe audio files via OpenRouter using audio-capable models (Gemini, GPT-4o-audio, etc). |
| 4 | `songsee` | Generate spectrograms and audio feature visualizations (mel, chroma, MFCC, tempogram, etc.) from ... |
| 5 | `youtube-content` | Fetch YouTube video transcripts and transform them into structured content (chapters, summaries, ... |

## 🍎 Apple 生态 (Apple)

| # | Skill 名称 | 功能简介 |
|---|-----------|---------|
| 1 | `apple-notes` | Manage Apple Notes via the memo CLI on macOS (create, view, search, edit). |
| 2 | `apple-reminders` | Manage Apple Reminders via remindctl CLI (list, add, complete, delete). |
| 3 | `findmy` | Track Apple devices and AirTags via FindMy.app on macOS using AppleScript and screen capture. |
| 4 | `imessage` | Send and receive iMessages/SMS via the imsg CLI on macOS. |

## 🤖 自主 Agent (Autonomous AI Agents)

| # | Skill 名称 | 功能简介 |
|---|-----------|---------|
| 1 | `claude-code` | Delegate coding tasks to Claude Code (Anthropic's CLI agent). Use for building features, refactor... |
| 2 | `codex` | Delegate coding tasks to OpenAI Codex CLI agent. Use for building features, refactoring, PR revie... |
| 3 | `hermes-agent` | Complete guide to using and extending Hermes Agent — CLI usage, setup, configuration, spawning ad... |
| 4 | `opencode` | Delegate coding tasks to OpenCode CLI agent for feature implementation, refactoring, PR review, a... |

## 🎮 游戏 (Gaming)

| # | Skill 名称 | 功能简介 |
|---|-----------|---------|
| 1 | `minecraft-modpack-server` | Set up a modded Minecraft server from a CurseForge/Modrinth server pack zip. Covers NeoForge/Forg... |
| 2 | `pokemon-player` | Play Pokemon games autonomously via headless emulation. Starts a game server, reads structured ga... |

## 🔌 MCP 协议 (MCP)

| # | Skill 名称 | 功能简介 |
|---|-----------|---------|
| 1 | `mcporter` | Use the mcporter CLI to list, configure, auth, and call MCP servers/tools directly (HTTP or stdio... |
| 2 | `native-mcp` | Built-in MCP (Model Context Protocol) client that connects to external MCP servers, discovers the... |

## 📝 笔记管理 (Note Taking)

| # | Skill 名称 | 功能简介 |
|---|-----------|---------|
| 1 | `obsidian` | Read, search, and create notes in the Obsidian vault. |

## 🧪 内测 QA (Dogfood)

| # | Skill 名称 | 功能简介 |
|---|-----------|---------|
| 1 | `dogfood` | Systematic exploratory QA testing of web applications — find bugs, capture evidence, and generate... |

## 📊 数据科学 (Data Science)

| # | Skill 名称 | 功能简介 |
|---|-----------|---------|
| 1 | `jupyter-live-kernel` | Use a live Jupyter kernel for stateful, iterative Python execution via hamelnb. Load this skill w... |

## 📱 社交媒体 (Social Media)

| # | Skill 名称 | 功能简介 |
|---|-----------|---------|
| 1 | `xitter` | Interact with X/Twitter via the x-cli terminal client using official X API credentials. Use for p... |

## 🏠 智能家居 (Smart Home)

| # | Skill 名称 | 功能简介 |
|---|-----------|---------|
| 1 | `openhue` | Control Philips Hue lights, rooms, and scenes via the OpenHue CLI. Turn lights on/off, adjust bri... |

## 🎯 Logo 生成 (Logo Generator)

| # | Skill 名称 | 功能简介 |
|---|-----------|---------|
| 1 | `logo-generator` | Generate professional SVG logos and high-end showcase images. Use when the user wants to: (1) Cre... |

## ☕ 休闲生活 (Leisure)

| # | Skill 名称 | 功能简介 |
|---|-----------|---------|
| 1 | `find-nearby` | Find nearby places (restaurants, cafes, bars, pharmacies, etc.) using OpenStreetMap. Works with c... |

## 📧 邮件管理 (Email)

| # | Skill 名称 | 功能简介 |
|---|-----------|---------|
| 1 | `himalaya` | CLI to manage emails via IMAP/SMTP. Use himalaya to list, read, write, reply, forward, search, an... |

## 相关笔记
- [AutoClaw-自进化与Skill商店](2026-04-17-AutoClaw-自进化与Skill商店.md)
- [hack-skills-给AI装上黑客大脑](2026-04-17-hack-skills-给AI装上黑客大脑.md)
- [Lima轻量级虚拟机管理工具](2026-04-22-Lima轻量级虚拟机管理工具.md)
- [歸藏PPT-Skill-电子杂志风网页演示](2026-04-24-歸藏PPT-Skill-电子杂志风网页演示.md)
- [竞品吸收_OpenCLI](2026-04-28-竞品吸收_OpenCLI.md)
- [竞品吸收笔记-khazix-skills](2026-04-29-竞品吸收笔记-khazix-skills.md)
- [SkillClaw-analysis](2026-05-02-SkillClaw-analysis.md)
- [从零构建AI-CLI方法论-ChainlessChain](2026-05-04-从零构建AI-CLI方法论-ChainlessChain.md)
- [Claude创意连接器9大工具-Blender-MCP深度解析](2026-05-05-Claude创意连接器9大工具-Blender-MCP深度解析.md)
- [github-ai-trending-mattpocock-skills](2026-05-05-github-ai-trending-mattpocock-skills.md)
- [lewislulu-html-ppt-skill-analysis](2026-05-06-lewislulu-html-ppt-skill-analysis.md)
- [addyosmani-agent-skills生产级Agent技能包](2026-05-08-addyosmani-agent-skills生产级Agent技能包.md)
- [Claude-Code工程师放弃Markdown转HTML](2026-05-09-Claude-Code工程师放弃Markdown转HTML.md)
- [OfficeCLI-AI-Agent的Office工具](2026-05-09-OfficeCLI-AI-Agent的Office工具.md)
- [Skill盈利死结与Plugin演进](2026-05-09-Skill盈利死结与Plugin演进.md)
- [skill-building-invoice-automation](2026-05-10-skill-building-invoice-automation.md)
- [softwarecopyright-skill-analysis](2026-05-10-softwarecopyright-skill-analysis.md)
- [nTop-Automate-CLI-完整测试文档](2026-05-12-nTop-Automate-CLI-完整测试文档.md)
- [中文学术去AI味10步Skill框架](2026-05-12-中文学术去AI味10步Skill框架.md)
- [30个网络抓包调试工具速查](2026-05-14-30个网络抓包调试工具速查.md)
- [HTML-Anything-Agent驱动HTML编辑器](2026-05-14-HTML-Anything-Agent驱动HTML编辑器.md)
- [SkillFactory-测试驱动Skill生成工厂](2026-05-14-SkillFactory-测试驱动Skill生成工厂.md)
- [Supertonic-闪电般本地TTS](2026-05-14-Supertonic-闪电般本地TTS.md)
- [数据目录工具全景指南](2026-05-15-数据目录工具全景指南.md)
- [CyberVerse公众号HTML模板分析](orphan/2026-05-03-CyberVerse公众号HTML模板分析.md)
- [国自然申请书AI-Skill流水线](orphan/2026-05-04-国自然申请书AI-Skill流水线.md)
- [数据血缘-lineage-工具全景](orphan/2026-05-09-数据血缘-lineage-工具全景.md)
- [论文写作Skill工具链组合方案](orphan/2026-05-12-论文写作Skill工具链组合方案.md)
- [HTML的不合理有效性-Claude-Code-团队](orphan/2026-05-16-HTML的不合理有效性-Claude-Code-团队.md)
- [20260512-10-skill-学术去ai味框架](orphan/20260512-10-skill-学术去ai味框架.md)
- [build-ai-cli](orphan/build-ai-cli.md)
- [hermes-skill-top10-2026w18](orphan/hermes-skill-top10-2026w18.md)
- [skills-apple](orphan/skills-apple.md)
- [skills-catalog](orphan/skills-catalog.md)
- [skills-data-science](orphan/skills-data-science.md)
- [skills-dogfood](orphan/skills-dogfood.md)
- [skills-email](orphan/skills-email.md)
- [skills-github](orphan/skills-github.md)
- [skills-leisure](orphan/skills-leisure.md)
- [skills-logo-generator-skill](orphan/skills-logo-generator-skill.md)
- [skills-smart-home](orphan/skills-smart-home.md)
- [skills-social-media](orphan/skills-social-media.md)
- [skills-team-roles](orphan/skills-team-roles.md)
- [skills-autonomous-ai-agents](skills-autonomous-ai-agents.md)
- [skills-creative](skills-creative.md)
- [skills-devops](skills-devops.md)
- [skills-gaming](skills-gaming.md)
- [skills-mcp](skills-mcp.md)
- [skills-media](skills-media.md)
- [skills-mlops](skills-mlops.md)
- [skills-note-taking](skills-note-taking.md)
- [skills-openclaw-imports](skills-openclaw-imports.md)
- [skills-productivity](skills-productivity.md)
- [skills-red-teaming](skills-red-teaming.md)
- [skills-research](skills-research.md)
- [skills-software-development](skills-software-development.md)
