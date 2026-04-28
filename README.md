# payroll-verifier

**AI-assisted payroll verification for Swedish BPO — built for audit, not just accuracy.**

Swedish payroll consultants verify payslips by hand against Skatteverket tax tables, arbetsgivaravgift rates, Semesterlagen, and the specific *kollektivavtal* each employer has signed. One consultant can process ~40 payslips a day. This project automates the verification while preserving the audit trail a compliance officer needs to sign off.

All LLM traffic is routed through **Kong AI Gateway** to **OpenRouter**, giving us PII sanitization, token-level cost control, prompt governance, and full observability at the infrastructure layer — plus multi-model flexibility without code changes.

Built in one day at [Hackathon name] by a team of five.

---

## Why this exists

Payroll verification in Sweden is high-volume, rules-heavy, and regulated. The hard part isn't the arithmetic — it's that every verdict has to be traceable to:

- The **tax table version** in effect on the pay period
- The **kollektivavtal clause** being enforced, in the version valid at the time
- The **instruction** the agent followed, and the version of that instruction
- The **model** the agent called, and the gateway policy that governed the call
- The **human reviewer** who accepted or rejected the verdict

Existing tools check numbers. They don't produce audit evidence. For BPO customers with financial-entity clients, that gap is the blocker.

## What it does

1. **Ingests** a payslip in PAXml format (the Swedish payroll XML standard).
2. **Parses** it into a canonical schema (`schema/`).
3. **Runs deterministic rules** for things the law fixes in numbers:
   - A-skatt lookup against Skatteverket's 2026 tables
   - Arbetsgivaravgift (31.42% standard, with age-based exceptions)
   - Semesterlön 12% per Semesterlagen § 16
   - Net salary arithmetic consistency
4. **Runs an LLM verification agent** for things that require interpretation — specifically, kollektivavtal compliance checks driven by versioned natural-language instructions. All LLM calls go through Kong AI Gateway to OpenRouter.
5. **Produces a verdict record** containing the rule version, instruction version, model ID, gateway request ID, OpenRouter generation ID, extracted fields, expected vs actual, motivation in Swedish, and a confidence score.
6. **Presents the verdict** in a React review GUI where a consultant accepts or rejects it.
7. **Captures structured rejection reasons** and proposes a refined instruction as a diff against the current version — so the system learns without a consultant having to write prompts.

Every verdict, every accept/reject, every instruction change, every LLM call is logged with timestamps and version IDs. Reproducible by design.

## Tech stack

| Layer | Tech | Why |
|---|---|---|
| Frontend | React + Vite + TypeScript | Team fluent, ships fast, clean separation from backend |
| Backend API | Python 3.11 + FastAPI | OpenAPI docs for free, async, Pydantic native |
| Schema | Pydantic v2 | Single source of truth shared across rules, agent, and API |
| Rules engine | Pure Python functions | Readable by compliance officers, unit-testable |
| LLM Gateway | Kong AI Gateway (Docker, DB-less) | PII sanitization, prompt-guard, token limits, audit logs |
| LLM Router | OpenRouter | Multi-model access through one OpenAI-compatible API |
| Storage | SQLite | Zero-setup, one file, fine for hackathon volume |
| Instructions | Versioned YAML files | Diffable, git-tracked, human-readable |

## Architecture

```
┌────────────────────────────┐
│ React frontend (Vite + TS) │
└──────────┬─────────────────┘
           │ HTTP/JSON
           ▼
┌────────────────────────────┐
│ FastAPI backend            │
│ /upload  /verdict  /review │
│ /instructions              │
└──────────┬─────────────────┘
           │
     ┌─────┴─────────────┐
     ▼                   ▼
┌─────────────┐   ┌──────────────────┐
│ Parser +    │   │ Rules engine     │
│ canonical   │   │ (pure Python)    │
│ schema      │   └────────┬─────────┘
└─────────────┘            │
                           ▼
                  ┌──────────────────┐
                  │ LLM agent        │
                  │ (versioned YAML  │
                  │ instructions)    │
                  └────────┬─────────┘
                           │ HTTP
                           ▼
                  ┌──────────────────────┐
                  │ Kong AI Gateway      │
                  │ • PII sanitization   │
                  │ • prompt-guard       │
                  │ • token rate-limit   │
                  │ • request/resp logs  │
                  │ • ai-proxy           │
                  └──────────┬───────────┘
                             │ HTTP (OpenAI-compatible)
                             ▼
                  ┌──────────────────────┐
                  │ OpenRouter           │
                  │ → Claude / GPT /     │
                  │   Llama / Mistral /  │
                  │   etc.               │
                  └──────────────────────┘

                  ┌──────────────────────┐
                  │ SQLite: verdicts,    │
                  │ reviews, instruction │
                  │ versions, audit log  │
                  └──────────────────────┘
```

Three design choices worth calling out:

**Deterministic vs LLM split.** Things the law fixes exactly (tax rates, semesterlön %) belong in code — fast, testable, auditable. Things that require reading a contract (kollektivavtal clauses) belong in the agent — but behind a versioned instruction so the behaviour is reproducible.

**Kong AI Gateway in front of every LLM call.** The application never talks to OpenRouter directly. This gives us:
- **PII sanitization before egress.** Personnummer, names, and addresses are stripped at the gateway before prompts leave our perimeter — independent of whether the app code remembered to do it. This is our Dataskyddslagen ch 3 § 10 and GDPR Art 32 control.
- **Prompt-guard.** The gateway rejects prompts that don't match approved templates, so a bug in the agent code can't smuggle unexpected instructions to the model.
- **Token-based rate limiting and cost caps** per tenant — foundation for the per-customer quotas in the production design.
- **Request/response logging** with token counts, latency, model IDs, and a gateway-assigned request ID that we store on the verdict record. One ID joins the verdict to the raw LLM call forever.
- **Provider swap without code changes.** Kong → OpenRouter today; Kong → Bedrock EU tomorrow for production EU residency — same application code.

**OpenRouter as the model router behind Kong.** Kong gives us governance; OpenRouter gives us model flexibility. One line of config swaps Claude for GPT-4 or Llama — useful for cost optimization, provider outages, and future fine-tuning experiments. Both Kong and OpenRouter record their own request IDs, and we log both on every verdict.

**Instruction versioning.** Every instruction is a YAML file with `id`, `version`, `effective_from`, `source`, `applies_to`, `expected`. The verdict records both the instruction ID and its version. When a consultant rejects a verdict, we propose a new version as a diff — the old one stays immutable.

## Repo layout

```
payroll-verifier/
├── schema/              Pydantic models — the shared contract
├── parsers/             PAXml parser
├── rules/               Deterministic rule functions + unit tests
├── agent/               LLM verifier + versioned instruction YAMLs
│   ├── verifier.py
│   ├── gateway.py       Kong AI Gateway client wrapper
│   └── instructions/    Versioned YAML instruction files
├── api/                 FastAPI app
│   ├── main.py
│   └── routes/          /upload, /verdict, /review, /instructions
├── frontend/            React app (Vite + TypeScript)
│   ├── src/
│   └── package.json
├── gateway/             Kong declarative config (kong.yaml)
├── storage/             SQLite helpers, verdict persistence
├── samples/             Test payslips (clean + planted errors)
├── docs/
│   └── governance.md    EU AI Act / GDPR / DORA design notes
└── demo/                Pitch script + backup demo video
```

## Team

Five people, one day, one repo. Ownership by folder:

| Person | Owns | Scope |
|---|---|---|
| **1** | `schema/`, `parsers/`, `storage/`, integration | Canonical Pydantic contract, PAXml parser, SQLite, keeps everyone in sync |
| **2** | `rules/`, `api/routes/` | Deterministic rules + the FastAPI endpoints that expose them |
| **3** | `agent/`, `gateway/` | LLM verifier, instruction versioning, Kong `kong.yaml` |
| **4** | `frontend/` | React app against the OpenAPI spec Person 2 publishes |
| **5** | `docs/`, `demo/`, pitch, integration testing, backup video | Governance one-pager, demo orchestration, the one person who isn't coding |

## Getting started

Requirements: Python 3.11+, Node 20+, Docker (for Kong), OpenRouter API key.

### 1. Start Kong AI Gateway

```bash
export OPENROUTER_API_KEY=sk-or-v1-...

docker run -d --name kong \
  -v "$(pwd)/gateway:/kong/declarative" \
  -e "KONG_DATABASE=off" \
  -e "KONG_DECLARATIVE_CONFIG=/kong/declarative/kong.yaml" \
  -e "KONG_PROXY_LISTEN=0.0.0.0:8000" \
  -e "KONG_ADMIN_LISTEN=0.0.0.0:8001" \
  -e "OPENROUTER_API_KEY=$OPENROUTER_API_KEY" \
  -p 8000:8000 -p 8001:8001 \
  kong/kong-gateway:latest
```

Kong now listens on `localhost:8000` and routes `/llm/chat/completions` to OpenRouter via the `ai-proxy` plugin, with `ai-prompt-guard`, `ai-prompt-decorator`, and PII sanitization applied. See `gateway/kong.yaml` for the declarative config.

Verify Kong is routing correctly:

```bash
curl http://localhost:8000/llm/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Säg hej på svenska."}]}'
```

### 2. Start the FastAPI backend

```bash
cd payroll-verifier
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export KONG_GATEWAY_URL=http://localhost:8000
uvicorn api.main:app --reload --port 8080
```

OpenAPI docs auto-generated at `http://localhost:8080/docs`.

### 3. Start the React frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. Upload a sample from `samples/` and step through the verdict. Every LLM call the agent makes will go through Kong and appear in the gateway logs (`docker logs -f kong`).

## Kong AI Gateway — what we use and why

| Plugin | What it does for us | Why it matters |
|---|---|---|
| `ai-proxy` | Single API surface to OpenRouter (and future providers) | Model/provider swap without code changes |
| `ai-prompt-guard` | Rejects prompts outside approved templates | App bugs can't leak arbitrary prompts to the model |
| `ai-prompt-decorator` | Injects the system prompt + versioned instruction at the gateway | Instruction version is enforced infrastructurally, not in app code |
| PII sanitization | Strips personnummer, names, addresses before egress | Dataskyddslagen / GDPR control at the perimeter |
| `rate-limiting-advanced` (token-based) | Caps token spend per tenant / per hour | Per-customer cost guarantees, DoS protection |
| Request / response logging | Gateway request ID, token counts, latency, model ID | Joined to verdict record → AI Act Art 12 audit log |

The full `kong.yaml` is in [`gateway/kong.yaml`](gateway/kong.yaml) with inline comments explaining each route and plugin binding.

## Why OpenRouter behind Kong

For the hackathon demo we route Kong to OpenRouter because it gives us access to Claude, GPT, Llama, Mistral, and others through one OpenAI-compatible endpoint. This lets us:

- Show the multi-model governance story (same prompt-guard, same PII sanitization, regardless of downstream model)
- Swap models mid-demo if one is slow or rate-limited
- Compare verdicts across models as a "confidence stress test"

**Production note:** OpenRouter routes through its own infrastructure (non-EU). The production path for EU customers would be Kong → Bedrock EU or Kong → a self-hosted model — a config change in `kong.yaml`, no application code touched. This is called out in the governance doc.

## Running the rules

```bash
pytest rules/tests/
```

Each deterministic rule is a pure function over the canonical schema and has its own unit tests with real Skatteverket 2026 reference values.

## API surface

FastAPI auto-generates OpenAPI docs at `/docs`. Core endpoints:

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/upload` | Upload a PAXml payslip, returns parsed canonical view |
| `POST` | `/verify/{payslip_id}` | Run rules + agent, return a verdict |
| `GET` | `/verdict/{verdict_id}` | Fetch a verdict with full lineage |
| `POST` | `/verdict/{verdict_id}/review` | Accept or reject a verdict, optionally propose instruction refinement |
| `GET` | `/instructions` | List all instruction versions |
| `GET` | `/audit` | Audit log view (for the governance demo) |

## Governance

The one thing most hackathon projects skip. See [`docs/governance.md`](docs/governance.md) for our design notes on:

- EU AI Act Art 6 high-risk classification (scoped as high-risk by default)
- GDPR Art 22 compliance via mandatory human review
- Dataskyddslagen ch 3 § 10 handling of personnummer — pseudonymised at ingestion *and* sanitized at Kong before any LLM egress
- DORA Art 30 contract readiness for financial-entity customers
- Audit logging per AI Act Art 12 — rule version, instruction version, model ID, Kong request ID, OpenRouter generation ID, timestamp on every verdict
- Data residency roadmap — OpenRouter for hackathon demo, Bedrock EU or self-hosted for production

In Swedish BPO, an AI that can't be audited can't be sold. We designed for that from the first commit. Kong sits at the chokepoint where the "auditable" claim is actually enforceable — not in application code that a future maintainer can accidentally bypass.

## Scope for the hackathon

This is a one-day build. We deliberately scoped down:

**In scope:**
- One input format (PAXml)
- Four deterministic rules
- One kollektivavtal clause, with two instruction versions to show refinement
- Kong AI Gateway running locally in Docker with ai-proxy (→ OpenRouter) + prompt-guard + PII sanitization
- React review GUI with accept/reject and refinement proposal
- FastAPI backend with OpenAPI docs
- Full verdict lineage including Kong and OpenRouter request IDs

**Out of scope for now:**
- PDF/OCR parsing
- Multi-tenant isolation + per-tenant KMS
- Monthly email drafting to customers
- Full kollektivavtal library
- Production Kong Konnect deployment on EU infrastructure (we use local Docker Kong)
- Bedrock EU routing (config change post-hackathon, no code change)
- User authentication (single-user demo)

The governance document covers the full target design; the code covers the demonstrable slice.

## License

TBD — repo is private during the hackathon.

---

*Lönekoll för svensk BPO — byggd för granskning, inte bara noggrannhet.*
