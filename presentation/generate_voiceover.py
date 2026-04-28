#!/usr/bin/env python3
"""
Generate high-quality female voiceover for ComplianceGuard presentation
using OpenRouter's gpt-4o-mini-tts (April 2026) with nova voice.
Uses the /api/v1/audio/speech endpoint — returns MP3 directly, no ffmpeg needed.
Uses only Python standard library — no pip dependencies needed.

Model choice: openai/gpt-4o-mini-tts-2025-12-15
  - OpenAI's newest dedicated TTS model (released Apr 2026 on OpenRouter)
  - Supports 'instructions' parameter for voice style/tone control
  - Returns direct MP3 — no PCM16 streaming or WAV conversion required
  - Priced at $0.60/M characters (very cost-efficient)

Voice: nova
  - Warm, clear, professional female voice
  - Best for confident business/technology narration
"""

import os, json, urllib.request, urllib.error

API_KEY = "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"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://github.com/Morteza-Rastgoo/payroll-verifier",
    "X-Title": "ComplianceGuard Presentation",
}

# ── Model & voice configuration ──────────────────────────────────────────────
MODEL = "openai/gpt-4o-mini-tts-2025-12-15"
VOICE = "nova"   # warm, clear, professional female voice
VOICE_INSTRUCTIONS = (
    "You are a professional female presenter narrating a technology hackathon "
    "demonstration for a business audience. Speak clearly, confidently, and at a "
    "natural conversational pace — not too fast, not slow. Emphasise key terms "
    "naturally. Sound knowledgeable, articulate, and engaging. "
    "Do not add words or commentary beyond what is written."
)

# Slide scripts — natural, confident female narrator tone
SLIDES = {
    "slide_01_title": (
        "Today we're presenting ComplianceGuard — an AI-powered payroll verification system "
        "built for the modern BPO firm that must operate inside the boundaries of the EU AI Act and GDPR. "
        "Let's get into it."
    ),
    "slide_02_problem": (
        "Business Process Outsourcing firms process millions of sensitive financial documents every single year. "
        "And right now, they're walking a legal tightrope. "
        "Since August 2024, the EU AI Act classifies payroll and tax processing AI as High-Risk. "
        "That means every AI decision must be traceable, explainable, and auditable — by law. "
        "On top of that, most existing AI pipelines send raw employee data — IBANs, names, home addresses — "
        "directly to cloud language models, with zero redaction. "
        "That is a GDPR violation waiting to happen."
    ),
    "slide_03_difficulties": (
        "Why can't existing solutions just be patched to fix this? Because the problems are structural. "
        "Today's AI tools are black boxes — no audit log, no human override, no plain-language explanation "
        "for employees who've been auto-declined. "
        "Each violation of Article 12, 14, or 86 of the EU AI Act is an independent legal liability. "
        "And the tools are siloed: OCR lives here, policy checking lives there, tax assignment lives somewhere else. "
        "There is no unified compliance layer sitting across all of them."
    ),
    "slide_04_consequences": (
        "The stakes are real. Non-compliance with the EU AI Act carries penalties of up to 30 million euros "
        "or 6% of global annual turnover. GDPR adds another 20 million on top. "
        "Worse, regulators have the power to suspend your AI systems entirely — "
        "which for a BPO firm means operational shutdown. "
        "And a single publicised breach is enough to lose client contracts immediately. "
        "The window to get ahead of this is right now — in 2025 and 2026."
    ),
    "slide_05_solution": (
        "This is ComplianceGuard. A three-layer AI orchestration system where each layer has a defined legal role. "
        "Layer One: The Guide. This is the employee-facing portal. "
        "OCR scans the receipt, pre-fills the form, and validates document quality — with GDPR data minimisation built in. "
        "Layer Two: The Auditor. This is the finance manager's dashboard. "
        "It surfaces policy violations — think meal limit breaches or weekend alcohol claims — "
        "and requires a human to approve or reject every flagged decision, satisfying Article 14. "
        "Layer Three: The Tax Expert. Final sign-off, tax slab verification, "
        "and the generation of a compliance-sealed audit trail ready for regulators. "
        "And binding all three layers together is the Kong AI Gateway — "
        "which ensures that PII never, ever reaches the language model."
    ),
    "slide_06_architecture": (
        "Here's the flow. A receipt comes in. EasyOCR extracts the text. "
        "Kong's PII Sanitiser masks every identifier — names become USER 01, IBANs become placeholders. "
        "Only then does the cleaned text reach the LangGraph agent chain. "
        "Every request is logged by Kong, creating an immutable audit trail. "
        "And Kong's semantic guardrail plugin blocks any prompt injection or off-scope query "
        "at the gateway level — before it even reaches the AI."
    ),
    "slide_07_benefits": (
        "The outcome is a system that is privacy-first by architecture, not by policy promise. "
        "Zero PII reaches the language model — ever. "
        "Every decision has a 100% auditable log. "
        "High-risk overrides require human sign-off with a written reason. "
        "And every employee gets a plain-language explanation of every automated decision. "
        "And the operational benefit: receipt to audit log in seconds, replacing days of manual review."
    ),
    "slide_08_demo_layer1": (
        "Let's walk the app. This is Layer One — the Employee Submission Portal. "
        "An employee drags and drops their receipt. The OCR engine scans it in real time. "
        "The AI Guide Agent pre-fills the form — date detected, amount detected, category assigned. "
        "But notice the Vendor Name field is highlighted in amber — "
        "the AI couldn't read it from the receipt, and the employee is prompted to correct it before submission. "
        "At the bottom of every screen you'll see the GDPR transparency notice: "
        "your data is sanitised via Kong Gateway — no identifiers are stored in the model."
    ),
    "slide_09_demo_layer2": (
        "This is Layer Two — the Internal Auditor Dashboard, designed for a finance manager. "
        "The violation feed is risk-scored. High-risk receipts are at the top — "
        "this one exceeds the fifty-pound meal limit. Medium risk here — a weekend submission. "
        "Low risk ones are auto-approved. "
        "When the auditor opens a flagged item, they see a side-by-side view of the redacted receipt "
        "and the AI's policy analysis. "
        "Notice the override panel: Article 14 of the EU AI Act requires a written justification "
        "before any human override is accepted. No reason, no override."
    ),
    "slide_10_demo_layer3": (
        "This is Layer Three — the Tax and Compliance Hub for the senior Azets tax specialist. "
        "The AI has pre-selected the tax slab — Standard Rate 20% — with a 94% confidence score. "
        "The specialist can accept or adjust. "
        "Below that is the audit trail terminal: redaction applied, policy checked, tax assigned — "
        "each event timestamped and immutable. This is Article 12 in action. "
        "And at the bottom, the Article 86 explanation panel: a plain-language summary of exactly "
        "why this specific tax classification was made — exportable directly to tax authorities. "
        "One click on Issue Compliance Seal locks the record and generates the final certificate."
    ),
    "slide_11_summary": (
        "Three cognitive layers. Zero PII reaching the language model. "
        "Four EU AI Act articles satisfied. And a 100% immutable audit trail. "
        "ComplianceGuard — the future of BPO payroll is automated, private, and compliant. "
        "Thank you."
    ),
}

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def generate_audio(text: str) -> bytes:
    """
    Call OpenRouter /api/v1/audio/speech and return raw MP3 bytes.
    The 'instructions' parameter steers tone/style without adding text.
    """
    payload = {
        "model": MODEL,
        "input": text,
        "voice": VOICE,
        "instructions": VOICE_INSTRUCTIONS,
        "response_format": "mp3",
    }
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/audio/speech",
        data=body,
        headers=HEADERS,
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return resp.read()


def main():
    print(f"🎙️  Generating ComplianceGuard voiceover")
    print(f"   Model : {MODEL}")
    print(f"   Voice : {VOICE}  (warm, professional female)")
    print(f"📁  Output: {OUTPUT_DIR}\n")

    generated = []
    failed = []

    for slide_id, text in SLIDES.items():
        print(f"  ▶ {slide_id}  ({len(text)} chars)...", end=" ", flush=True)
        try:
            mp3_bytes = generate_audio(text)
            if len(mp3_bytes) < 100:
                raise RuntimeError(f"Response too small ({len(mp3_bytes)} bytes) — likely an API error")

            out_path = os.path.join(OUTPUT_DIR, f"{slide_id}.mp3")
            with open(out_path, "wb") as f:
                f.write(mp3_bytes)

            kb = len(mp3_bytes) // 1024
            print(f"✓  {kb} KB  [mp3]")
            generated.append((slide_id, out_path, kb))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")[:200]
            print(f"✗  HTTP {e.code}: {body}")
            failed.append(slide_id)
        except Exception as e:
            print(f"✗  {e}")
            failed.append(slide_id)

    print(f"\n{'=' * 60}")
    print(f"✅  {len(generated)} / {len(SLIDES)} files generated")
    for sid, path, kb in generated:
        print(f"   ✓ {os.path.basename(path)}  ({kb} KB)")
    if failed:
        print(f"\n⚠️  Failed ({len(failed)}):")
        for sid in failed:
            print(f"   ✗ {sid}")


if __name__ == "__main__":
    main()
