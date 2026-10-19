# 🔴 安全攻防 (Red Teaming)

> 本分类共 **102** 个 Skills。

[← 返回总览](skills-overview.md)

---

| # | Skill 名称 | 功能简介 |
|---|-----------|---------|
| 1 | `401-403-bypass-techniques` | 401/403 bypass playbook. Use when encountering access-denied responses on admin panels, API endpoints, or restricted paths. Covers path manipulatio... |
| 2 | `active-directory-acl-abuse` | Active Directory ACL abuse playbook. Use when exploiting misconfigured AD permissions including GenericAll, WriteDACL, DCSync rights, shadow creden... |
| 3 | `active-directory-certificate-services` | AD Certificate Services attack playbook. Use when targeting misconfigured AD CS for privilege escalation via ESC1-ESC13 template abuse, NTLM relay ... |
| 4 | `active-directory-kerberos-attacks` | Kerberos attack playbook for Active Directory. Use when targeting AD authentication via AS-REP roasting, Kerberoasting, golden/silver/diamond ticke... |
| 5 | `ai-ml-security` | AI/ML security playbook. Use when assessing model supply chain attacks (pickle RCE, poisoned weights), adversarial examples, model poisoning, model... |
| 6 | `android-pentesting-tricks` | Android pentesting playbook. Use when testing Android applications for SSL pinning bypass, exported component abuse, WebView vulnerabilities, inten... |
| 7 | `anti-debugging-techniques` | Anti-debugging detection and bypass playbook. Use when reversing protected binaries that detect debuggers via ptrace, PEB flags, timing checks, or ... |
| 8 | `api-auth-and-jwt-abuse` | API authentication and JWT abuse playbook. Use when testing bearer tokens, API keys, claim trust, header spoofing, rate limits, and API auth bounda... |
| 9 | `api-authorization-and-bola` | API authorization and BOLA testing playbook. Use when APIs expose object identifiers, nested resources, hidden writable fields, or weak function-le... |
| 10 | `api-recon-and-docs` | API reconnaissance and documentation review playbook. Use when discovering endpoints, schemas, versions, OpenAPI specs, hidden docs, and surface ar... |
| 11 | `api-sec` | Entry P1 category router for API security. Use when choosing between API recon, authorization, token abuse, and hidden-parameter workflows before a... |
| 12 | `arbitrary-write-to-rce` | Arbitrary write to RCE playbook. Use when you have an arbitrary write primitive (from heap exploitation, format string, or OOB write) and need to c... |
| 13 | `auth-sec` | Entry P1 category router for authentication and authorization. Use when testing login flows, sessions, object authorization, JWT, OAuth, CORS, CSRF... |
| 14 | `authbypass-authentication-flaws` | Authentication bypass testing playbook. Use when assessing login flows, password reset logic, account recovery, MFA bypass, token predictability, b... |
| 15 | `binary-protection-bypass` | Binary protection bypass playbook. Use when identifying and bypassing ASLR, PIE, NX/DEP, stack canary, RELRO, FORTIFY_SOURCE, CET, and MTE protecti... |
| 16 | `browser-exploitation-v8` | Browser and V8 exploitation playbook. Use when exploiting JavaScript engine vulnerabilities including JIT type confusion, incorrect bounds eliminat... |
| 17 | `business-logic-vuln` | Entry P1 category router for business logic testing. Use when workflow abuse, race conditions, pricing flaws, or multi-step state attacks matter mo... |
| 18 | `business-logic-vulnerabilities` | Business logic vulnerability playbook. Use when reasoning about workflows, race conditions, price manipulation, coupon abuse, state machines, and m... |
| 19 | `classical-cipher-analysis` | Classical cipher analysis playbook. Use when encountering substitution ciphers, Vigenere, transposition, XOR, or encoded text in CTF challenges tha... |
| 20 | `clickjacking` | Clickjacking playbook. Use when testing whether target pages can be framed, whether X-Frame-Options or CSP frame-ancestors are properly configured,... |
| 21 | `cmdi-command-injection` | Command injection playbook. Use when user input may reach shell commands, process execution, converters, import pipelines, or blind out-of-band com... |
| 22 | `code-obfuscation-deobfuscation` | Code obfuscation analysis and deobfuscation playbook. Use when reversing binaries protected by junk code, opaque predicates, self-modifying code, c... |
| 23 | `container-escape-techniques` | Container escape playbook. Use when operating inside a Docker container, LXC, or Kubernetes pod and need to escape to the host via privileged mode,... |
| 24 | `cors-cross-origin-misconfiguration` | CORS misconfiguration testing playbook. Use when analyzing cross-origin trust, credentialed browser reads, origin reflection, preflight policy bugs... |
| 25 | `crlf-injection` | CRLF injection playbook. Use when user input reaches HTTP response headers, Location redirects, Set-Cookie values, or log files where carriage-retu... |
| 26 | `csp-bypass-advanced` | Advanced Content Security Policy bypass techniques. Use when XSS or data exfiltration is blocked by CSP and you need to find policy weaknesses, tru... |
| 27 | `csrf-cross-site-request-forgery` | CSRF testing playbook. Use when reviewing state-changing web flows, anti-CSRF defenses, SameSite behavior, JSON CSRF, login CSRF, and OAuth state h... |
| 28 | `csv-formula-injection` | CSV/spreadsheet formula injection (DDE, Excel/LibreOffice, Google Sheets IMPORT*). Use when exports, imports, or user fields feed spreadsheets or r... |
| 29 | `dangling-markup-injection` | Dangling markup injection playbook. Use when HTML injection is possible but JavaScript execution is blocked (CSP, sanitizer strips event handlers, ... |
| 30 | `defi-attack-patterns` | DeFi attack pattern playbook. Use when analyzing flash loan attacks, price oracle manipulation, MEV sandwich attacks, governance exploits, bridge v... |
| 31 | `dependency-confusion` | Supply-chain testing via package-manager dependency confusion: when internal package names resolve to attacker-controlled public registries, leadin... |
| 32 | `deserialization-insecure` | Insecure deserialization playbook. Use when Java, PHP, or Python applications deserialize untrusted data via ObjectInputStream, unserialize, pickle... |
| 33 | `dns-rebinding-attacks` | DNS rebinding attack playbook. Use when testing applications that trust DNS resolution for origin checks, interact with internal services from brow... |
| 34 | `email-header-injection` | Email header injection and spoofing playbook. Use when testing contact forms, email APIs, password reset flows, or any feature that constructs SMTP... |
| 35 | `expression-language-injection` | Expression Language injection playbook. Use when Java EL, SpEL, OGNL, or MVEL expressions may evaluate attacker-controlled input in Spring, Struts2... |
| 36 | `file-access-vuln` | Entry P1 category router for file access and upload workflows. Use when testing download endpoints, file paths, local file inclusion, upload flows,... |
| 37 | `format-string-exploitation` | Format string exploitation playbook. Use when printf-family functions receive user-controlled format strings, enabling arbitrary stack reads (%p/%s... |
| 38 | `godmode` | "Jailbreak API-served LLMs using G0DM0D3 techniques — Parseltongue input obfuscation (33 techniques), GODMODE CLASSIC system prompt templates, ULTR... |
| 39 | `graphql-and-hidden-parameters` | GraphQL and hidden parameter testing playbook. Use when exploring introspection, batching, undocumented fields, hidden parameters, schema abuse, an... |
| 40 | `hack` | Entry P0 primary router for HackSkills. Use when the task involves web application testing, API security assessment, recon, vulnerability triage, e... |
| 41 | `hash-attack-techniques` | Hash attack playbook. Use when exploiting length extension, MD5/SHA1 collisions, HMAC timing leaks, birthday attacks, or hash-based proof of work i... |
| 42 | `heap-exploitation` | Heap exploitation playbook. Use when targeting ptmalloc2/glibc heap vulnerabilities including UAF, double free, overflow, off-by-one/null, and leve... |
| 43 | `http-host-header-attacks` | HTTP Host header injection and routing abuse playbook. Use when the application trusts the Host header for generating URLs, routing requests, or ac... |
| 44 | `http-parameter-pollution` | HTTP Parameter Pollution (HPP): duplicate query/body keys parsed differently by servers, proxies, WAFs, and app frameworks. Use when filters and ap... |
| 45 | `http2-specific-attacks` | HTTP/2 protocol-specific attack playbook. Use when the target supports HTTP/2 and you need to exploit binary framing, HPACK compression, h2c upgrad... |
| 46 | `idor-broken-object-authorization` | IDOR and broken object authorization testing playbook. Use when requests expose object identifiers, tenant boundaries, writable fields, or missing ... |
| 47 | `injection-checking` | Entry P1 category router for injection testing. Use when routing between XSS, SQLi, SSRF, XXE, SSTI, command injection, and NoSQL injection workflo... |
| 48 | `insecure-source-code-management` | Source control and artifact exposure (.git, .svn, .hg, backups, .env). Use when recon finds VCS paths, 403 on hidden dirs, or backup/config leaks d... |
| 49 | `ios-pentesting-tricks` | iOS pentesting playbook. Use when testing iOS applications for keychain extraction, URL scheme hijacking, Universal Links exploitation, runtime man... |
| 50 | `jndi-injection` | JNDI injection playbook. Use when Java applications perform JNDI lookups with attacker-controlled names, especially via Log4j2, Spring, or any code... |
| 51 | `jwt-oauth-token-attacks` | JWT and OAuth token attack playbook. Use when validating token trust, signing algorithms, key handling, claim abuse, bearer flows, and OAuth accoun... |
| 52 | `kernel-exploitation` | Linux kernel exploitation playbook. Use when exploiting kernel vulnerabilities (UAF, OOB, race condition, type confusion) for privilege escalation ... |
| 53 | `kubernetes-pentesting` | Kubernetes penetration testing playbook. Use when targeting Kubernetes clusters via API server, RBAC enumeration, service account abuse, etcd acces... |
| 54 | `lattice-crypto-attacks` | Lattice-based cryptanalysis playbook. Use when attacking RSA via Coppersmith small roots, recovering DSA/ECDSA nonces from bias, solving knapsack p... |
| 55 | `linux-lateral-movement` | Linux lateral movement playbook. Use after gaining initial access to pivot across Linux hosts via SSH hijacking, credential harvesting, internal pi... |
| 56 | `linux-privilege-escalation` | Linux privilege escalation playbook. Use when you have low-privilege shell access and need to escalate to root via SUID/SGID binaries, capabilities... |
| 57 | `linux-security-bypass` | Linux security mechanism bypass playbook. Use when facing restricted bash/rbash, read-only or noexec filesystems, AppArmor, SELinux, seccomp filter... |
| 58 | `llm-prompt-injection` | LLM prompt injection playbook. Use when testing AI/LLM applications for direct injection, indirect injection via RAG/browsing, tool abuse, data exf... |
| 59 | `macos-process-injection` | macOS process injection playbook. Use when you need to inject code into running or launching macOS processes via dylib hijacking, DYLD environment ... |
| 60 | `macos-security-bypass` | macOS security bypass playbook. Use when targeting macOS endpoints and need to bypass TCC, Gatekeeper, SIP, sandbox, code signing, or entitlement-b... |
| 61 | `memory-forensics-volatility` | Memory forensics playbook using Volatility 2/3. Use when analyzing memory dumps for malware analysis, credential extraction, process investigation,... |
| 62 | `mobile-ssl-pinning-bypass` | Mobile SSL pinning bypass playbook. Use when intercepting HTTPS traffic from mobile applications that implement certificate pinning, public key pin... |
| 63 | `network-protocol-attacks` | Network protocol attack playbook. Use when exploiting layer 2/3 protocols including ARP spoofing, LLMNR/NBT-NS/mDNS poisoning, WPAD abuse, DHCPv6 a... |
| 64 | `nosql-injection` | NoSQL injection playbook. Use when MongoDB-style operators, JSON query objects, flexible search filters, or backend query DSLs may allow data or lo... |
| 65 | `ntlm-relay-coercion` | NTLM relay and authentication coercion playbook. Use when capturing and relaying NTLM authentication to escalate privileges via SMB, LDAP, HTTP, or... |
| 66 | `oauth-oidc-misconfiguration` | OAuth and OIDC misconfiguration testing playbook. Use when reviewing redirect URI handling, state and nonce validation, PKCE, token audience, callb... |
| 67 | `open-redirect` | Open redirect playbook. Use when URL parameters, form actions, or JavaScript sinks control navigation targets and may redirect users to attacker-co... |
| 68 | `path-traversal-lfi` | Path traversal and LFI playbook. Use when file paths, download endpoints, include operations, archive extraction, or wrapper behavior may expose fi... |
| 69 | `prototype-pollution` | Prototype pollution testing for JavaScript stacks. Use when user input is merged into objects (query parsers, JSON bodies, deep assign), when confi... |
| 70 | `prototype-pollution-advanced` | Advanced prototype pollution playbook — server-side RCE, client-side gadgets, filter bypasses, and detection techniques. Companion to ../prototype-... |
| 71 | `race-condition` | Race condition and TOCTOU testing for web apps. Use when testing one-time operations, concurrent HTTP abuse, rate-limit bypass, Turbo Intruder gate... |
| 72 | `recon-and-methodology` | Reconnaissance and methodology playbook. Use when mapping assets, discovering endpoints, fingerprinting technology, and building a structured testi... |
| 73 | `recon-for-sec` | Entry P1 category router for reconnaissance and methodology. Use when mapping scope, discovering assets, fingerprinting technology, building endpoi... |
| 74 | `request-smuggling` | HTTP request smuggling and desynchronization testing. Use when front proxies, CDNs, or load balancers disagree with the origin on message framing (... |
| 75 | `reverse-shell-techniques` | Reverse shell techniques playbook. Use when establishing remote shells including language one-liners, encrypted shells (OpenSSL/socat/ncat), web sh... |
| 76 | `rsa-attack-techniques` | RSA attack playbook for CTF and real-world cryptanalysis. Use when given RSA parameters (n, e, c) and need to recover plaintext by exploiting weak ... |
| 77 | `saml-sso-assertion-attacks` | SAML SSO assertion attack playbook. Use when testing signature validation, assertion wrapping, audience restrictions, ACS handling, XML trust bound... |
| 78 | `sandbox-escape-techniques` | Sandbox escape playbook. Use when breaking out of Python sandbox, Lua sandbox, seccomp filter, chroot jail, container/Docker, browser sandbox, or n... |
| 79 | `smart-contract-vulnerabilities` | Smart contract vulnerability playbook. Use when auditing Solidity/EVM contracts for reentrancy, integer overflow, access control, delegatecall, fla... |
| 80 | `sqli-sql-injection` | SQL injection playbook. Use when input reaches SQL queries, authentication logic, sorting, filtering, reporting, or DB-specific blind and out-of-ba... |
| 81 | `ssrf-server-side-request-forgery` | SSRF playbook. Use when the server fetches URLs, resolves hostnames, imports remote content, or can be driven toward internal networks, cloud metad... |
| 82 | `ssti-server-side-template-injection` | SSTI playbook. Use when template expressions, server-side rendering, preview features, or templating engines may evaluate attacker-controlled content. |
| 83 | `stack-overflow-and-rop` | Stack overflow and ROP playbook. Use when exploiting buffer overflows to hijack control flow via return address overwrite, ROP chains, ret2libc, re... |
| 84 | `steganography-techniques` | Steganography detection and extraction playbook. Use when analyzing images (LSB, PNG chunks, JPEG DCT, EXIF), audio (spectrogram, DTMF), files (pol... |
| 85 | `subdomain-takeover` | Subdomain takeover detection and exploitation playbook. Use when targets have dangling CNAME/NS/MX records pointing to deprovisioned cloud resource... |
| 86 | `symbolic-execution-tools` | Symbolic execution and constraint solving playbook. Use when solving CTF reversing challenges, recovering keys, bypassing checks, or automating bin... |
| 87 | `symmetric-cipher-attacks` | Symmetric cipher attack playbook. Use when exploiting block cipher mode weaknesses (CBC padding oracle, ECB cut-and-paste, bit flipping), stream ci... |
| 88 | `traffic-analysis-pcap` | Traffic analysis and PCAP forensics playbook. Use when analyzing network captures including Wireshark filters, protocol analysis (HTTP/DNS/FTP/SMTP... |
| 89 | `tunneling-and-pivoting` | Tunneling and pivoting playbook. Use when establishing network tunnels through compromised hosts including SSH tunneling, Chisel, Ligolo-ng, socat,... |
| 90 | `type-juggling` | PHP type juggling and weak comparison (`==`) bypass. Use when authentication, HMAC/signature checks, or token validation uses loose equality, numer... |
| 91 | `unauthorized-access-common-services` | Unauthorized access playbook for common exposed services. Use when Redis, Rsync, PHP-FPM, AJP/Ghostcat, Hadoop YARN, H2 Console, or similar managem... |
| 92 | `upload-insecure-files` | Insecure file upload playbook. Use when testing upload validation, storage paths, processing pipelines, preview behavior, overwrite risks, and uplo... |
| 93 | `vm-and-bytecode-reverse` | Custom VM and bytecode reverse engineering playbook. Use when CTF challenges or protected software implement custom virtual machines with proprieta... |
| 94 | `waf-bypass-techniques` | WAF bypass methodology and generic evasion techniques. Use when a web application firewall blocks injection payloads (SQLi, XSS, RCE) and you need ... |
| 95 | `web-cache-deception` | Web cache deception and poisoning playbook. Use when CDN, reverse proxy, or application caching may serve sensitive authenticated content to other ... |
| 96 | `websocket-security` | WebSocket handshake, CSWSH, tooling (wsrepl, ws-harness, Burp), and common flaws. Use when apps use real-time channels, chat, notifications, or WS-... |
| 97 | `windows-av-evasion` | AV/EDR evasion playbook for Windows. Use when bypassing AMSI, ETW, .NET assembly detection, shellcode execution, process injection, API hooking, an... |
| 98 | `windows-lateral-movement` | Windows lateral movement playbook. Use when pivoting between Windows hosts via PsExec, WMI, WinRM, DCOM, RDP, pass-the-hash, overpass-the-hash, or ... |
| 99 | `windows-privilege-escalation` | Windows local privilege escalation playbook. Use when you have low-privilege shell access on Windows and need to escalate via token abuse, Potato e... |
| 100 | `xslt-injection` | XSLT injection testing: processor fingerprinting, XXE and document() SSRF, EXSLT write primitives, PHP/Java/.NET extension RCE surfaces. Use when u... |
| 101 | `xss-cross-site-scripting` | XSS playbook. Use when user-controlled content reaches HTML, attributes, JavaScript, DOM sinks, uploads, or multi-context rendering paths. |
| 102 | `xxe-xml-external-entity` | XXE playbook. Use when XML, SVG, OOXML, SOAP, or parser-driven imports may resolve external entities, files, or internal network resources. |

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
- [skills-overview](skills-overview.md)
- [skills-productivity](skills-productivity.md)
- [skills-research](skills-research.md)
- [skills-software-development](skills-software-development.md)
