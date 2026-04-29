
# 🏗️ Master Prompt: Three-Layer AI Compliance Interface Architect

**Role:** You are a Senior UX/UI Engineer specializing in **BPO Enterprise Software** and **Compliance-Driven Design**. Your goal is to generate three separate, functional React/Tailwind interfaces that interact with a **Rust (Axum) backend** proxied through a **Kong AI Gateway**.

**Common Technical Foundations:**
- **Backend Sync:** Interfaces must expect data in JSON format consistent with Rust structs (Serde).
- **Security:** No raw PII is displayed; all sensitive strings are received as placeholders (e.g., `[USER_01]`) from the Kong AI Gateway.
- **Framework:** React with Tailwind CSS, using Lucide-React for iconography.

---

## 🎨 Global Compliance Principles (Apply to all Layers)
1. **Article 50 (Transparency):** Every screen must display a "Processed by Compliance AI v1.2" badge.
2. **Article 12 (Traceability):** Every action (click, upload, override) must be prepared to be sent to a `/log` endpoint.
3. **GDPR (Data Minimization):** Only show the specific fields required for that layer's role.

---

## 🟢 Layer 1: The Employee "Submission Portal"
**Persona:** A remote employee uploading business receipts.
**Core Work:** Ensuring high-quality data ingestion and instant feedback.

* **User Flow:** Upload $\rightarrow$ OCR Scan Animation $\rightarrow$ AI Validation $\rightarrow$ Fix/Submit.
* **Key UI Components:**
    * **Intelligent Uploader:** A drag-and-drop zone that triggers a "Scanning" state.
    * **Validation Sidebar:** A real-time checklist powered by the **"Guide Agent."**
        * *Dynamic Alerts:* "Date found," "Amount found," "⚠️ Missing Vendor Name."
    * **Transparency Disclosure:** A persistent footer: *"Your data is sanitized via Kong Gateway. No personal identifiers are stored in the AI model."*
* **Prompt for UI Model:** *"Create a mobile-first React component for receipt submission. Focus on high-visibility feedback. When the OCR finishes, show a 'Smart Form' where the AI has pre-filled fields, but highlights missing ones in orange."*

---

## 🟡 Layer 2: The Company "Internal Auditor" Dashboard
**Persona:** A Manager or Finance Admin at the client company.
**Core Work:** Reviewing policy violations and performing Human-in-the-Loop (HITL) checks.

* **User Flow:** Dashboard Overview $\rightarrow$ Flagged Receipt Review $\rightarrow$ Policy Justification $\rightarrow$ Approve/Escalate.
* **Key UI Components:**
    * **Violation Feed:** A list of receipts flagged by the **"Auditor Agent"** (e.g., "Exceeds £50 Meal Limit," "Weekend Alcohol").
    * **Side-by-Side Reviewer:** On the left, the redacted receipt image; on the right, the AI's policy analysis.
    * **Human Override Tool (Art. 14):** A button to "Ignore Flag" with a mandatory text area for the human to provide a reason.
* **Prompt for UI Model:** *"Generate a desktop-optimized dashboard for a Finance Auditor. Use a table with 'Risk Levels' (Low, Medium, High). Include an 'Explain Decision' button that opens a modal showing exactly which company policy was triggered."*

---

## 🔴 Layer 3: The BPO "Compliance & Tax" Hub
**Persona:** A Senior Tax Specialist at Azets.
**Core Work:** Final regulatory sign-off, tax slab verification, and audit trail archiving.

* **User Flow:** Batch Review $\rightarrow$ Tax Slab Verification $\rightarrow$ Audit Log Inspection $\rightarrow$ Final Digital Seal.
* **Key UI Components:**
    * **Tax Slab Selector:** A pre-selected dropdown (e.g., "Standard Rate 20%") with a "Confidence Score" indicator next to it.
    * **Regulatory Audit Log (Art. 12):** A dedicated tab showing a JSON-style or "terminal" view of the interaction history: `[Redaction Applied] -> [Policy Checked] -> [Tax Assigned]`.
    * **Explainability Panel (Art. 86):** A plain-language summary of why the AI assigned a specific tax status, ready to be exported to the tax authorities.
* **Prompt for UI Model:** *"Generate a high-density 'Expert Mode' interface. It should feel like a financial tool. Prioritize the 'Audit Trail' visibility. Include a 'Final Seal' button that generates a compliance certificate in JSON format."*

---

## 🛠️ Technical Integration Logic
* **API Calls:** Use `fetch` or `axios` to call the Rust endpoints (e.g., `/api/v1/employee/upload`, `/api/v1/audit/review`).
* **State Management:** Use a global state to track the `session_id` and the `compliance_meta` object across all three layers.
* **Error Handling:** If the Rust backend returns a `403 Forbidden` (triggered by Kong's Prompt Guard), show a security warning to the user.

***

### How to use this prompt effectively:
1.  **If building all three at once:** Paste this entire prompt into your LLM.
2.  **If building one by one:** Copy the **Global Principles** + the **Specific Layer** details into your LLM for focused code generation.

**Pro Hackathon Tip:** When you demo this, show the **Layer 3 Audit Log** first. Judges love seeing the "Traceability" because it proves you actually solved the "Compliance" part of the challenge, not just the "Payroll" part!