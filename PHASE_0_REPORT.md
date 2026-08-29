# PHASE 0 DISCOVERY AND ARCHITECTURE REPORT
## our-ai-demo V0

---

### ENVIRONMENT STATUS
- **Working Directory**: `/c/Users/REDDY/projects/our-ai-demo` (completely empty)
- **Operating System**: Windows 11 Enterprise (MINGW64_NT-10.0-26200)
- **Available Tools**: 
  - Python 3.14.7
  - Node.js v24.19.0
  - npm 11.17.0
  - Git
  - Docker Desktop
- **System Resources**: ~8GB RAM (~1GB free), Intel Core i5-8265U CPU @ 1.60GHz
- **Repository Status**: Not initialized (no .git directory)
- **Environment Files**: None present
- **User Configuration**: Standard Claude Code setup in `C:\Users\REDDY\.claude\`

### ARCHITECTURE STATUS
- Clean slate - no existing code, architecture, or dependencies
- Fresh start opportunity for optimal technology choices

### PRODUCT SCOPE
Per master prompt requirements:
- Build reusable AI business/customer-support agent for demonstration
- Use existing AI model/API (not building our own foundation model)
- Critical principle: AI must NOT claim action success without verified business state change
- Support multiple business types: SaaS, e-commerce, subscription, online education, agencies, services
- V0 scope: Simulated business environment (no real client dependencies)
- Core flow: Customer Message → Understand → Classify Intent → Plan → Select Tool → Execute → Observe → Verify → Replan/Escalate → Generate Response

### AI PROVIDER STRATEGY
- Abstract provider interface for swappability (Anthropic, OpenAI, etc.)
- Do NOT train/custom build models for V0
- API keys via environment variables (never committed)
- Initial implementation: Anthropic Claude API (consistent with Claude Code usage)
- Interface methods: `generate_response()`, `classify_intent()`, `select_action()`, `structured_output()`

### TECH STACK RECOMMENDATIONS
- **Backend**: Python + FastAPI (modern, lightweight, excellent for APIs)
- **Frontend**: Minimal HTML/CSS/JS chat interface (pragmatic for demo)
- **Database**: SQLite (zero-config, file-based, sufficient for demo scale)
- **AI Provider**: Abstract layer with Anthropic Claude as initial provider
- **Tooling**: Standard Python packaging (virtualenv, requirements.txt)

### PROJECT STRUCTURE PROPOSAL
```
our-ai-demo/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI entrypoint
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── chat.py          # Chat endpoints
│   │       └── health.py        # Health check
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py            # Environment configuration
│   │   ├── ai_provider.py       # AI provider abstraction
│   │   ├── simulator.py         # Simulated business environment
│   │   ├── orchestrator.py      # Main agent loop (understand→plan→act→verify)
│   │   ├── tools/               # Allowlisted tool registry
│   │   │   ├── __init__.py
│   │   │   ├── base.py          # Base tool interface
│   │   │   ├── check_payment_status.py
│   │   │   ├── check_subscription_status.py
│   │   │   ├── reactivate_subscription.py
│   │   │   ├── get_product_or_plan.py
│   │   │   └── ...              # Additional tools
│   │   ├── verifier.py          # Deterministic state verification
│   │   └── audit_logger.py      # Structured audit logging
│   └── models/
│       ├── __init__.py
│       ├── customer.py
│       ├── payment.py
│       ├── subscription.py
│       └── audit_log.py
├── data/
│   └── demo.db                  # SQLite database
├── tests/
│   ├── __init__.py
│   ├── test_health.py
│   ├── test_chat.py
│   └── test_orchestrator.py
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
└── docker-compose.yml           # Optional: consistent dev environment
```

### AGENCY AGENTS PLAN
- Use specialist agents selectively for material improvements
- Potential roles:
  - Backend Developer: API/orchestrator implementation
  - Frontend Developer: Chat interface
  - UI/UX Designer: Professional, clean demo UI
  - Code Reviewer: Quality assurance
  - Testing Engineer: Comprehensive test suite
  - Security Specialist: Security review
- Claude Code remains primary orchestrator
- Avoid unnecessary agent complexity

### SECURITY PLAN
- Environment variables for all secrets (API keys, etc.)
- `.gitignore` includes `.env`, `.env.example` provided without real values
- Strict input validation on all tool parameters
- Tool allowlist - only pre-approved, registered tools executable
- No arbitrary code execution (no eval, exec, subprocess with user input)
- Basic request validation and sanitization
- Safe error handling (no stack traces or internal details exposed)
- Minimal PII storage in simulated environment
- Dependency vulnerability scanning (safety.py or similar)

### TESTING PLAN
Mandatory test coverage:
1. Health endpoint: `GET /v1/health` returns 200 OK
2. Normal customer message: End-to-end flow validation
3. Pricing questions: Accurate responses from configured knowledge
4. Payment issues: Successful resolution paths
5. Subscription issues: Reactivation flows with verification
6. Successful tool execution: Proper state changes and audit logs
7. Failed tool execution: Graceful handling and replanning
8. Verification success: Confirmed state matches goals
9. Verification failure: Detected mismatches and appropriate response
10. Replanning: Alternative paths when initial actions fail
11. Escalation: Human handoff when no safe solution exists
12. Invalid tool input: Proper validation errors
13. Unknown entities: Graceful handling of missing customers/transactions
14. AI provider failure: Fallback behavior when API unavailable
15. Missing configuration: Clear startup errors for missing env vars
- End-to-end test validating: UNDERSTAND → PLAN → ACT → OBSERVE → VERIFY → REPLAN (where applicable)

### PHASE 0 EXECUTION PLAN
1. Initialize git repository with initial commit
2. Create directory structure per proposal
3. Set up Python virtual environment and dependencies
4. Create `.gitignore` and `.env.example` templates
5. Write initial `README.md` with project overview and setup instructions
6. Implement minimal health check endpoint (`GET /v1/health`)
7. Verify basic application runs and responds to health checks
8. STOP and await explicit user approval before Phase 1 implementation

### PHASE 0 ACCEPTANCE CRITERIA
- [x] Environment inspected and documented
- [ ] Git repository initialized (`git init`)
- [ ] Project directory structure created
- [ ] Development environment configured (venv, requirements.txt)
- [ ] `.gitignore` and `.env.example` created
- [ ] Initial `README.md` with project overview
- [ ] Health check endpoint implemented and functional
- [ ] No core feature implementation (reserved for Phase 1)

### RISKS IDENTIFIED
1. **Environment Inconsistencies**: WSL/Windows path handling complexities
2. **External API Dependency**: Latency, cost, and failure points with AI providers
3. **Scope Creep**: Tendency to over-engineer versus building minimal viable demo
4. **Simulation Fidelity**: Ensuring simulated business behaves realistically for convincing demo
5. **Verification Robustness**: Building verification that doesn't become brittle or false-positive prone
6. **Security Oversights**: Accidental secret commits or vulnerability introduction
7. **Tool Proliferation**: Adding too many tools before validating core loop

### QUESTIONS / DECISIONS PENDING USER INPUT
1. **Frontend Implementation**: Simple static HTML/CSS/JS vs React/Vue for chat interface?
2. **AI Provider Approach**: Start with Anthropic-only or design multi-provider abstraction from day one?
3. **Simulation Scope**: Depth of simulated business data for V0 (customers, plans, transactions)?
4. **Initial Tool Set**: Which 3-4 tools to implement first for maximum demo value?
5. **Deployment Strategy**: Dockerize immediately or keep simple local Python execution?
6. **Testing Framework**: Standard `pytest` or unittest for Python test suite?

---
**STATUS**: Phase 0 discovery complete. Awaiting explicit user approval to proceed to Phase 1 implementation.