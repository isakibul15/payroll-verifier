# payroll-verifier

**AI-assisted payroll verification for Swedish BPO — built for audit, not just accuracy.**

Swedish payroll consultants verify payslips by hand against Skatteverket tax tables, arbetsgivaravgift rates, Semesterlagen, and the specific *kollektivavtal* each employer has signed. One consultant can process ~40 payslips a day. This project automates the verification while preserving the audit trail a compliance officer needs to sign off.

All LLM traffic is routed through **Kong AI Gateway**, giving us PII sanitization, token-level cost control, prompt governance, and full observability at the infrastructure layer — exactly what EU AI Act Art 12 logging and DORA Art 30 oversight require.

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
4. **Runs an LLM verification agent** for things that require interpretation — specifically, kollektivavtal compliance checks driven by versioned natural-language instructions. All LLM calls go through Kong AI Gateway.
5. **Produces a verdict record** containing the rule version, instruction version, model version, gateway request ID, extracted fields, expected vs actual, motivation in Swedish, and a confidence score.
6. **Presents the verdict** in a review GUI where a consultant accepts or rejects it.
7. **Captures structured rejection reasons** and proposes a refined instruction as a diff against the current version — so the system learns without a consultant having to write prompts.

Every verdict, every accept/reject, every instruction change, every LLM call is logged with timestamps and version IDs. Reproducible by design.

## Architecture

```
PAXml payslip
    │
    ▼
┌─────────┐     ┌──────────────────┐
│ Parser  │────▶│ Canonical schema │ (Pydantic)
└─────────┘     └────────┬─────────┘
                         │
           ┌─────────────┴─────────────┐
           ▼                           ▼
  ┌──────────────────┐      ┌──────────────────────┐
  │ Deterministic    │      │ LLM verification     │
  │ rules engine     │      │ agent (versioned     │
  │ (pure Python)    │      │ instructions, YAML)  │
  └────────┬─────────┘      └──────────┬───────────┘
           │                           │
           │                           ▼
           │              ┌──────────────────────┐
           │              │ Kong AI Gateway      │
           │              │ • PII sanitization   │
           │              │ • prompt-guard       │
           │              │ • token rate-limit   │
           │              │ • request/resp logs  │
           │              │ • model routing      │
           │              └──────────┬───────────┘
           │                         │
           │                         ▼
           │              ┌──────────────────────┐
           │              │ LLM provider(s)      │
           │              │ Anthropic / Bedrock  │
           │              └──────────┬───────────┘
           │                         │
           └─────────────┬───────────┘
                         ▼
              ┌──────────────────┐
              │ Verdict record   │ (SQLite)
              │ + full lineage   │
              │ + gateway req ID │
              └────────┬─────────┘
                       ▼
              ┌──────────────────┐
              │ Review GUI       │ (Streamlit)
              │ + refinement     │
              │ loop             │
              └──────────────────┘
```

Three design choices worth calling out:

**Deterministic vs LLM split.** Things the law fixes exactly (tax rates, semesterlön %) belong in code — fast, testable, auditable. Things that require reading a contract (kollektivavtal clauses) belong in the agent — but behind a versioned instruction so the behaviour is reproducible.

**Kong AI Gateway in front of every LLM call.** The application never talks to a model provider directly. This gives us:
- **PII sanitization before egress.** Personnummer, names, and addresses are stripped at the gateway before prompts leave our perimeter — independent of whether the app code remembered to do it. This is our Dataskyddslagen ch 3 § 10 and GDPR Art 32 control.
- **Prompt-guard.** The gateway rejects prompts that don't match approved templates, so a bug in the agent code can't smuggle unexpected instructions to the model.
- **Token-based rate limiting and cost caps** per tenant — foundation for the per-customer quotas in the production design.
- **Request/response logging with token counts, latency, model IDs, and a gateway-assigned request ID** that we store on the verdict record. One ID joins the verdict to the raw LLM call forever.
- **Provider swap without code changes** — Anthropic today, Bedrock EU tomorrow, same application code. This matters for the EU data-residency story.

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
├── gateway/             Kong declarative config (kong.yaml)
├── gui/                 Streamlit review interface
├── storage/             SQLite helpers, verdict persistence
├── samples/             Test payslips (clean + planted errors)
├── docs/
│   └── governance.md    EU AI Act / GDPR / DORA design notes
└── demo/                Pitch script + backup demo video
```

## Team

Five people, one day, one repo. Ownership by folder:

| Area | Owner | Scope |
|---|---|---|
| `schema/`, `parsers/`, integration | Person 1 | Canonical model, PAXml parser, keeps everything connected |
| `rules/` | Person 2 | Deterministic rules + tests |
| `agent/`, `gateway/` | Person 3 | LLM verifier, instruction versioning, Kong config |
| `gui/`, `storage/` | Person 4 | Streamlit app, verdict persistence |
| `docs/`, `demo/`, pitch | Person 5 | Governance framing, demo orchestration, stage |

## Getting started

Requirements: Python 3.11+, Docker (for Kong), an API key for the LLM provider.

### 1. Start Kong AI Gateway (locally, DB-less)

```bash
docker run -d --name kong \
  -v "$(pwd)/gateway:/kong/declarative" \
  -e "KONG_DATABASE=off" \
  -e "KONG_DECLARATIVE_CONFIG=/kong/declarative/kong.yaml" \
  -e "KONG_PROXY_LISTEN=0.0.0.0:8000" \
  -e "KONG_ADMIN_LISTEN=0.0.0.0:8001" \
  -e "ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY" \
  -p 8000:8000 -p 8001:8001 \
  kong/kong-gateway:latest
```

Kong now listens on `localhost:8000` and routes `/llm/*` to the configured provider with the `ai-proxy`, `ai-prompt-guard`, `ai-prompt-decorator`, and PII sanitization plugins applied. See `gateway/kong.yaml` for the declarative config.

### 2. Run the app

```bash
git clone https://github.com/IamSupun/payroll-verifier.git
cd payroll-verifier
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export KONG_GATEWAY_URL=http://localhost:8000
streamlit run gui/app.py
```

Then upload a sample from `samples/` and step through the verdict. Every LLM call the agent makes will go through Kong and appear in the gateway logs (`docker logs -f kong`).

## Kong AI Gateway — what we use and why

| Plugin | What it does for us | Why it matters |
|---|---|---|
| `ai-proxy` | Single API surface, swap between Anthropic / Bedrock / etc. | EU data residency swap without code changes |
| `ai-prompt-guard` | Rejects prompts outside approved templates | App bugs can't leak arbitrary prompts to the model |
| `ai-prompt-decorator` | Injects the system prompt + versioned instruction at the gateway | Instruction version is enforced infrastructurally, not in app code |
| PII sanitization | Strips personnummer, names, addresses before egress | Dataskyddslagen / GDPR control at the perimeter |
| `rate-limiting-advanced` (token-based) | Caps token spend per tenant / per hour | Per-customer cost guarantees, DoS protection |
| Request / response logging | Gateway request ID, token counts, latency, model ID | Joined to verdict record → AI Act Art 12 audit log |

The full `kong.yaml` is in [`gateway/kong.yaml`](gateway/kong.yaml) with inline comments explaining each route and plugin binding.

## Running the rules

```bash
pytest rules/tests/
```

Each deterministic rule is a pure function over the canonical schema and has its own unit tests with real Skatteverket 2026 reference values.

## Governance

The one thing most hackathon projects skip. See [`docs/governance.md`](docs/governance.md) for our design notes on:

- EU AI Act Art 6 high-risk classification (scoped as high-risk by default)
- GDPR Art 22 compliance via mandatory human review
- Dataskyddslagen ch 3 § 10 handling of personnummer — pseudonymised at ingestion *and* sanitized at Kong before any LLM egress
- DORA Art 30 contract readiness for financial-entity customers
- Audit logging per AI Act Art 12 — rule version, instruction version, model version, Kong request ID, timestamp on every verdict
- Data residency in EU (Bedrock EU via Kong, routing swap without code changes)

In Swedish BPO, an AI that can't be audited can't be sold. We designed for that from the first commit. Kong sits at the chokepoint where the "auditable" claim is actually enforceable — not in application code that a future maintainer can accidentally bypass.

## Scope for the hackathon

This is a one-day build. We deliberately scoped down:

**In scope:**
- One input format (PAXml)
- Four deterministic rules
- One kollektivavtal clause, with two instruction versions to show refinement
- Kong AI Gateway running locally in Docker with ai-proxy + prompt-guard + PII sanitization
- Review GUI with accept/reject and refinement proposal
- Full verdict lineage including Kong request IDs

**Out of scope for now:**
- PDF/OCR parsing
- Multi-tenant isolation + per-tenant KMS
- Monthly email drafting to customers
- Full kollektivavtal library
- Production Kong Konnect deployment on EU infrastructure (we use local Docker Kong)
- Semantic routing across multiple LLMs (single model in the demo)

The governance document covers the full target design; the code covers the demonstrable slice.

## License

TBD — repo is private during the hackathon.

---

*Lönekoll för svensk BPO — byggd för granskning, inte bara noggrannhet.*
