# CPTC12 - AI Lead & Web Role Checklist

---

## 1. Enumerate & test the client's AI/ML systems

**Discovery - hunt for AI touchpoints**
- Guest-facing chatbot / virtual assistant (support, booking, FAQ)
- Search & recommendation engines (rides, food, upsells)
- Dynamic pricing / demand forecasting
- Computer vision: ride-photo tagging, face recognition for entry/passes, license-plate reading in lots
- Fraud / anomaly detection on ticketing & payments
- Voice assistants / smart kiosks
- Any API endpoint that proxies to an LLM (look for `/chat`, `/ai`, `/assistant`, `/completions`, model names, streaming/token-style responses)
- Third-party AI SaaS integrations (inspect JS, API calls, response headers)

**Fingerprint what you find**
- Identify model/provider where possible (response style, error formats, headers, token limits)
- Map the endpoint: 
    - auth required? 
    - rate limited? 
    - input/output format? 
    - tool/function calling?
- What the AI can read or do on the backend

**Test against OWASP Top 10 for LLM Applications**
-  **LLM01 Prompt Injection** - direct jailbreaks + *indirect* (instructions planted in data the model ingests: uploaded docs, web pages, RAG sources)
-  **LLM02 Sensitive Info Disclosure** - coax out other users' data, PII, secrets, internal info
-  **LLM07 System Prompt Leakage** - extract the hidden system prompt / instructions
-  **LLM05 Improper Output Handling** - AI output flows into a sink: XSS, SQLi, SSRF, command injection downstream
-  **LLM06 Excessive Agency** - can the assistant take actions it shouldn't (place orders, change bookings, read accounts)? Abuse function/tool calling
-  **LLM08 Vector/Embedding Weaknesses** - RAG poisoning, retrieving docs across tenants
-  **LLM04 Data/Model Poisoning** - any user-influenced training or feedback loop
-  **LLM10 Unbounded Consumption** - resource/cost exhaustion, prompt flooding, model DoS
-  **LLM09 Misinformation** - induce harmful/incorrect output with business impact
-  **LLM03 Supply Chain** - exposed model artifacts, API keys, third-party AI deps

**High-impact AI angles for a park**
- Chatbot: account takeover or booking manipulation via excessive agency / IDOR *through* the assistant
- Prompt injection to leak another guest's PII or reservation data
- System-prompt or API-key leakage from the assistant
- Insecure output handling: chatbot reply rendered unsanitized - stored XSS
- Guardrail bypass to reach backend functions the UI doesn't expose

---

## 2. AI testing tooling & technique

- **garak** - LLM vulnerability scanner (open source)
- **PyRIT** - adversarial LLM testing framework
- **promptfoo** - prompt-injection / red-team test harness
- Burp Community / ZAP + `curl` - hit the AI API directly, replay, fuzz
- A curated set of jailbreak / injection payloads

**Technique notes**
- Always try *indirect* injection, not just direct
- Chain it: AI flaw → backend access. Treat the assistant as a pivot, not an endpoint
- Test the API *beneath* the chat UI directly
- Capture exact prompt + response as evidence

---

## 3. Web & API tooling

- Burp Suite **Community**
- OWASP ZAP
- ffuf / feroxbuster / dirsearch (content discovery)
- sqlmap (injection)
- nuclei (+ templates)
- wfuzz / Arjun (parameter discovery)
- nikto, whatweb, wappalyzer (fingerprinting)
- gobuster / amass / subfinder (subdomain/vhost enum)
- jwt_tool (JWT attacks)
- Postman or `curl`/`httpie` (API work)
- mitmproxy (mobile/API traffic)
- seclists (wordlists)
- Browser dev tools + FoxyProxy

---

## 4. Web & API knowledge prep

- OWASP **Web Security Testing Guide (WSTG)**
- OWASP **Top 10** categories + how to test each
- OWASP **API Security Top 10** 
- OWASP **Top 10 for LLM Applications** if the park has a guest chatbot
- Per-class attacks:
  - Broken access control / IDOR
  - Authentication & session flaws (weak login, JWT, session fixation)
  - Injection (SQLi, command, SSTI, XXE)
  - XSS (reflected / stored / DOM)
  - SSRF
  - Insecure deserialization
  - Security misconfig (default creds, verbose errors, exposed admin)
  - File upload / path traversal
  - CORS misconfig
  - Business-logic abuse (ticketing / payments / loyalty)

---

## 5. Theme-based web attack surface (Butters Family Farm)

Likely web/API targets *(educated guess)*:
- Ticketing / e-commerce / online store
- Guest portal or loyalty/rewards accounts
- Mobile app backend / public APIs
- Staff or ride-operations dashboards / admin panels
- Reservation / booking / scheduling systems
- Kiosk or POS-adjacent web interfaces
- Guest-facing chatbot / AI assistant
- Marketing site / CMS (WordPress etc.)

---

## 6. Web testing workflow

**Setup**
- Read scope + rules of engagement; list in-scope web apps/URLs
- Configure Burp/ZAP proxy, scope, and target list

**Recon / mapping**
- Enumerate all web apps and endpoints
- Spider + content discovery (ffuf/feroxbuster)
- Fingerprint tech stack (whatweb/wappalyzer)
- Parameter + API endpoint discovery
- Note auth flows, roles, and trust boundaries

**Attack**
- Access control / IDOR (cheap, high-impact - start here)
- Authentication & session
- Injection (SQLi/command/SSTI)
- XSS / SSRF / file upload
- Business-logic abuse (ticketing/payments/loyalty)
- Misconfig & default creds
- API checks (BOLA/BFLA, mass assignment, rate limits)
