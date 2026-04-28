# ComplianceGuard — 4-Minute Voiceover Script
**Azets × Kong Hackathon 2026**

> **Total duration:** ~4 min 10 sec · ~500 words spoken at 120 wpm  
> Each slide has a timing target. Advance the slide at the ▶ marker.

---

## ▶ Slide 1 — Title *(~10 seconds)*

> *"Today we're presenting ComplianceGuard — an AI-powered payroll verification system built for the modern BPO — Business Process Outsourcing — firm, that must operate inside the boundaries of the EU Artificial Intelligence Act and GDPR — the General Data Protection Regulation. Let's get into it."*

---

## ▶ Slide 2 — The Problem *(~28 seconds)*

> *"BPO firms process millions of sensitive financial documents every single year. And right now, they're walking a legal tightrope.*
>
> *Since August 2024, the EU AI Act classifies payroll and tax processing AI as High-Risk. That means every AI decision must be traceable, explainable, and auditable — by law.*
>
> *On top of that, most existing AI pipelines send raw employee data — IBANs, International Bank Account Numbers, names, home addresses — directly to cloud language models, with zero redaction. That is a GDPR violation waiting to happen."*

---

## ▶ Slide 3 — Difficulties *(~28 seconds)*

> *"Why can't existing solutions just be patched to fix this? Because the problems are structural.*
>
> *Today's AI tools are black boxes — no audit log, no human override, no plain-language explanation for employees who've been auto-declined. Each violation of Article 12, 14, or 86 of the EU AI Act is an independent legal liability.*
>
> *And the tools are siloed: OCR lives here, policy checking lives there, tax assignment lives somewhere else. There is no unified compliance layer sitting across all of them."*

---

## ▶ Slide 4 — Consequences *(~24 seconds)*

> *"The stakes are real. Non-compliance with the EU AI Act carries penalties of up to 30 million euros or 6% of global annual turnover. GDPR adds another 20 million on top.*
>
> *Worse, regulators have the power to suspend your AI systems entirely — which for a BPO firm means operational shutdown. And a single publicised breach is enough to lose client contracts immediately.*
>
> *The window to get ahead of this is right now — in 2025 and 2026."*

---

## ▶ Slide 5 — Our Solution *(~32 seconds)*

> *"This is ComplianceGuard. A three-layer AI orchestration system where each layer has a defined legal role.*
>
> *Layer One: The Guide. This is the employee-facing portal. OCR — Optical Character Recognition — scans the receipt, pre-fills the form, and validates document quality — with GDPR data minimisation built in.*
>
> *Layer Two: The Auditor. This is the finance manager's dashboard. It surfaces policy violations — think meal limit breaches or weekend alcohol claims — and requires a human to approve or reject every flagged decision, satisfying Article 14.*
>
> *Layer Three: The Tax Expert. Final sign-off, tax slab verification, and the generation of a compliance-sealed audit trail ready for regulators.*
>
> *And binding all three layers together is the Kong AI Gateway — which ensures that PII never, ever reaches the language model."*

---

## ▶ Slide 6 — Architecture *(~22 seconds)*

> *"Here's the flow. A receipt comes in. EasyOCR extracts the text. Kong's PII — Personally Identifiable Information — Sanitiser masks every identifier — names become USER_01, IBANs become placeholders. Only then does the cleaned text reach the LangGraph agent chain.*
>
> *Every request is logged by Kong, creating an immutable audit trail. And Kong's semantic guardrail plugin blocks any prompt injection or off-scope query at the gateway level — before it even reaches the AI."*

---

## ▶ Slide 7 — DEMO TIME! *(~5 seconds)*

> *"Enough theory — let's see it live."*

---

## ▶ Slide 8 — Demo: Layer 1, Employee Portal *(~26 seconds)*

> *"Let's walk the app. This is Layer One — the Employee Submission Portal.*
>
> *An employee drags and drops their receipt. The OCR engine scans it in real time. The AI Guide Agent pre-fills the form — date detected, amount detected, category assigned. But notice the Vendor Name field is highlighted in amber — the AI couldn't read it from the receipt, and the employee is prompted to correct it before submission.*
>
> *At the bottom of every screen you'll see the GDPR transparency notice: your data is sanitised via Kong Gateway — no identifiers are stored in the model."*

---

## ▶ Slide 9 — Demo: Layer 2, Auditor Dashboard *(~26 seconds)*

> *"This is Layer Two — the Internal Auditor Dashboard, designed for a finance manager.*
>
> *The violation feed is risk-scored. High-risk receipts are at the top — this one exceeds the fifty-pound meal limit. Medium risk here — a weekend submission. Low risk ones are auto-approved.*
>
> *When the auditor opens a flagged item, they see a side-by-side view of the redacted receipt and the AI's policy analysis. Notice the override panel: Article 14 of the EU AI Act requires a written justification before any human override is accepted. No reason, no override."*

---

## ▶ Slide 10 — Demo: Layer 3, Tax & Compliance Hub *(~26 seconds)*

> *"This is Layer Three — the Tax and Compliance Hub for the senior Azets tax specialist.*
>
> *The AI has pre-selected the tax slab — Standard Rate 20% — with a 94% confidence score. The specialist can accept or adjust.*
>
> *Below that is the audit trail terminal: redaction applied, policy checked, tax assigned — each event timestamped and immutable. This is Article 12 in action.*
>
> *And at the bottom, the Article 86 explanation panel: a plain-language summary of exactly why this specific tax classification was made — exportable directly to tax authorities.*
>
> *One click on Issue Compliance Seal locks the record and generates the final certificate."*

---

## ▶ Slide 11 — Key Benefits *(~20 seconds)*

> *"So why does ComplianceGuard win? It is privacy-first by architecture, not by policy promise. Zero PII reaches the LLM — Large Language Model — ever. Every decision has a one-hundred-percent auditable log. High-risk overrides require human sign-off with a written reason. And every employee gets a plain-language explanation of every automated decision.*
>
> *And the operational benefit: receipt-to-audit-log in seconds, replacing days of manual review."*

---

## ▶ Slide 12 — Summary *(~8 seconds)*

> *"Three cognitive layers. Zero PII reaching the LLM. Four EU AI Act articles satisfied. And a 100% immutable audit trail.*
>
> *ComplianceGuard — the future of BPO payroll is automated, private, and compliant. Thank you."*

---

## Timing Breakdown

| Slide | Topic                  | Time  |
|-------|------------------------|-------|
| 1     | Title                  | 0:10  |
| 2     | The Problem            | 0:28  |
| 3     | Difficulties           | 0:28  |
| 4     | Consequences           | 0:24  |
| 5     | Solution               | 0:32  |
| 6     | Architecture           | 0:22  |
| 7     | DEMO TIME!             | 0:05  |
| 8     | Demo — Layer 1         | 0:26  |
| 9     | Demo — Layer 2         | 0:26  |
| 10    | Demo — Layer 3         | 0:26  |
| 11    | Key Benefits           | 0:20  |
| 12    | Summary                | 0:08  |
| **Total** |                   | **3:55** |

> **Tip:** Deliver each line at a calm, confident pace. Pause 1 second between paragraphs. This gives you ~10 seconds of natural breathing room to land cleanly at 4:00.
