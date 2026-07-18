#!/usr/bin/env python3
"""Insert STAR or CREATE after Worked examples in each topic, then renumber."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MD = ROOT / "AI-Ascent.md"

# method: "STAR" or "CREATE" — never both
# Topics 1-27
METHODS = {
    1: "CREATE",
    2: "STAR",
    3: "CREATE",
    4: "CREATE",
    5: "CREATE",
    6: "STAR",
    7: "CREATE",
    8: "CREATE",
    9: "STAR",
    10: "CREATE",
    11: "STAR",
    12: "STAR",
    13: "STAR",
    14: "CREATE",
    15: "STAR",
    16: "CREATE",
    17: "STAR",
    18: "CREATE",
    19: "STAR",
    20: "CREATE",
    21: "STAR",
    22: "CREATE",
    23: "STAR",
    24: "STAR",
    25: "CREATE",
    26: "CREATE",
    27: "STAR",
}

CONTENT: dict[int, str] = {}

CONTENT[1] = """
## 1.5 CREATE method for an industry before/after brief

Use **CREATE** when you want a clear teaching or analysis brief: **Context**, **Role**, **Expectation**, **Audience**, **Task**, **Examples**.

| Letter | Meaning | What you write |
|--------|---------|----------------|
| **C** | Context | Industry, process, and current friction |
| **R** | Role | Who the AI (or analyst) should act as |
| **E** | Expectation | Quality bar, length, and what must not be invented |
| **A** | Audience | Who will use the brief |
| **T** | Task | Exact deliverable |
| **E** | Examples | One real before/after pair or sample metric |

**Copy-paste CREATE template:**

> **Context:** [industry + workflow] currently runs with [manual/batch pain].  
> **Role:** Act as an operations analyst who knows AI augmentation limits.  
> **Expectation:** Be specific, measurable, and honest about human controls. Do not invent ROI numbers.  
> **Audience:** [ops lead / L&D / executive].  
> **Task:** Produce a one-page before/after map with metrics and ownership.  
> **Examples:** Include one real process step from [paste notes].

**Worked CREATE example:**

> **Context:** Mid-size Indian e-commerce support team, 400 tickets/day, slow returns replies.  
> **Role:** AI-aware process designer.  
> **Expectation:** 1 page, plain language, no fake CSAT gains.  
> **Audience:** Head of Support.  
> **Task:** Before/after map for returns triage with AI draft + human approval.  
> **Examples:** Current average first reply 4 hours, top issue is “where is my refund.”

**Weak vs CREATE:**

- Weak: “Explain AI in retail.”
- CREATE: the brief above with a real process and a metric to improve.
"""

CONTENT[2] = """
## 2.5 STAR method for climbing one rung

Use **STAR** so a ladder plan is complete: **Situation**, **Task**, **Action**, **Result**.

| Letter | Meaning | What you write |
|--------|---------|----------------|
| **S** | Situation | Current rung and why it hurts |
| **T** | Task | Next rung to reach |
| **A** | Action | Steps, owners, and guardrails |
| **R** | Result | Definition of done and metrics |

**Copy-paste STAR template:**

> **Situation:** We are at [rung]. Pain: [time/errors/delays].  
> **Task:** Move only to [next rung].  
> **Action:** [data/process/tool steps]. Humans still [review/approve].  
> **Result:** In [N] weeks, [metric] improves without increasing [risk].

**Worked STAR example:**

> **Situation:** Finance team has clean invoice Sheets (descriptive) but forecasts late stock purchases.  
> **Task:** Add a simple predictive demand view for 20 SKUs.  
> **Action:** Export 12 months of sales, train/use a basic forecast, weekly review by category owner. No auto-purchase.  
> **Result:** Forecast vs actual tracked weekly, stockout rate for those SKUs drops within one quarter.

**Weak vs STAR:**

- Weak: “We need AI agents.”
- STAR: one rung, one metric, one human control.
"""

CONTENT[3] = """
## 3.5 CREATE method for hierarchy design

Use **CREATE** to assign the right layer of intelligence.

| Letter | Meaning | What you write |
|--------|---------|----------------|
| **C** | Context | Process and systems involved |
| **R** | Role | Designer / product owner perspective |
| **E** | Expectation | Clear layer map, no tool-name soup |
| **A** | Audience | Tech + business stakeholders |
| **T** | Task | Map layers and decision rights |
| **E** | Examples | One failure from skipping a layer |

**Copy-paste CREATE template:**

> **Context:** [process] uses [tools/data].  
> **Role:** Act as an AI systems designer.  
> **Expectation:** Separate rules, ML, generative, and agent layers. Name owners.  
> **Audience:** [CTO + ops].  
> **Task:** One-page hierarchy with what each layer may and may not do.  
> **Examples:** Include where tool sprawl already happened.

**Worked CREATE example:**

> **Context:** Support stack: Zendesk, Notion FAQ, ChatGPT side chats, no shared rules.  
> **Role:** AI operating-model lead.  
> **Expectation:** End shadow AI for refunds.  
> **Audience:** Support + IT security.  
> **Task:** Hierarchy: rules for refund caps → classifier for intent → LLM draft → human send.  
> **Examples:** Last month an agent pasted a customer PAN into a public chatbot.
"""

CONTENT[4] = """
## 4.5 CREATE method for choosing AI, ML, or DL

| Letter | Meaning | What you write |
|--------|---------|----------------|
| **C** | Context | Data type, volume, and decision |
| **R** | Role | Practical ML advisor |
| **E** | Expectation | Recommend the simplest fit |
| **A** | Audience | Non-specialist manager |
| **T** | Task | Choose AI / ML / DL and justify |
| **E** | Examples | One tabular and one unstructured case |

**Copy-paste CREATE template:**

> **Context:** We have [data]. Decision: [what]. Constraints: [cost/explainability].  
> **Role:** Act as a pragmatic ML advisor.  
> **Expectation:** Prefer classical ML when enough, deep learning only if needed.  
> **Audience:** [product/ops].  
> **Task:** Recommend approach + why + what to measure.  
> **Examples:** Paste 5 sample fields or describe the input.

**Worked CREATE example:**

> **Context:** Loan pre-screen with age, income, bureau score, product type. Need explainable decline reasons.  
> **Role:** Risk analytics advisor.  
> **Expectation:** No black-box-only recommendation.  
> **Audience:** Credit policy head.  
> **Task:** Choose classical ML vs DL and list required controls.  
> **Examples:** Current rule engine already blocks banned pincodes.
"""

CONTENT[5] = """
## 5.5 CREATE method for explaining ANI vs AGI vs ASI

| Letter | Meaning | What you write |
|--------|---------|----------------|
| **C** | Context | Why the audience confuses the terms |
| **R** | Role | Clear educator |
| **E** | Expectation | No hype, use today’s product examples |
| **A** | Audience | Executives or students |
| **T** | Task | One-page spectrum with examples |
| **E** | Examples | Three ANI products they already use |

**Copy-paste CREATE template:**

> **Context:** Stakeholders call our chatbot “AGI.”  
> **Role:** Act as a plain-language AI educator.  
> **Expectation:** Correct gently, stay practical.  
> **Audience:** [leadership workshop].  
> **Task:** Explain ANI/AGI/ASI with examples and a “what to build now” close.  
> **Examples:** Spam filter, maps routing, ChatGPT support drafts.

**Worked CREATE example:**

> **Context:** Board asks if we are “behind on AGI.”  
> **Role:** CIO briefing writer.  
> **Expectation:** 1 page, calm tone.  
> **Audience:** Board risk committee.  
> **Task:** Show we excel at ANI use cases and watch AGI signals without pausing delivery.  
> **Examples:** Invoice extraction pilot, support draft pilot.
"""

CONTENT[6] = """
## 6.5 STAR method for a strong text-generation prompt

Use **STAR**: **Situation**, **Task**, **Action**, **Result**.

| Letter | Meaning | What you write |
|--------|---------|----------------|
| **S** | Situation | Why this text is needed now |
| **T** | Task | Exact writing job |
| **A** | Action | Role, tone, rules, process |
| **R** | Result | Format and definition of done |

**Copy-paste STAR template:**

> **Situation:** I need [deliverable] for [audience] by [when].  
> **Task:** Draft [text type].  
> **Action:** Act as [role]. Use only [sources]. Tone [x]. Do not invent facts.  
> **Result:** [structure]. End with Assumptions + What to verify.

**Worked STAR example:**

> **Situation:** Product manager updating a skeptical sales team after a delayed release.  
> **Task:** 180-word note that explains delay and next date.  
> **Action:** Calm, no blame, no invented dates. Paste approved release notes only.  
> **Result:** Email body + subject line + 3 FAQ bullets.

**Weak vs STAR:**

- Weak: “Write a status update.”
- STAR: audience, length, source of truth, and verification list.
"""

CONTENT[7] = """
## 7.5 CREATE method for teaching neural networks

| Letter | Meaning | What you write |
|--------|---------|----------------|
| **C** | Context | Learner level and timebox |
| **R** | Role | Patient teacher |
| **E** | Expectation | Intuition first, light math |
| **A** | Audience | Non-engineers |
| **T** | Task | Explain forward pass + learning |
| **E** | Examples | One image or spam analogy |

**Copy-paste CREATE template:**

> **Context:** 20-minute intro for [team].  
> **Role:** Act as a patient AI teacher.  
> **Expectation:** No heavy equations, end with one practice question.  
> **Audience:** [ops/marketing].  
> **Task:** Explain neurons, layers, loss, and overfitting simply.  
> **Examples:** Use spam detection or photo tagging.

**Worked CREATE example:**

> **Context:** HR L&D session before an AI tools workshop.  
> **Role:** Friendly instructor.  
> **Expectation:** One analogy + one caution about overfitting.  
> **Audience:** People managers.  
> **Task:** 8-bullet teaching outline + quiz question.  
> **Examples:** Resume screening model that overfits to one campus.
"""

CONTENT[8] = """
## 8.5 CREATE method for explaining transformers

| Letter | Meaning | What you write |
|--------|---------|----------------|
| **C** | Context | Why the audience cares about transformers |
| **R** | Role | Systems explainer |
| **E** | Expectation | Attention intuition, not research paper |
| **A** | Audience | Practitioners |
| **T** | Task | Explain self-attention + context limits |
| **E** | Examples | Long contract Q&A failure without retrieval |

**Copy-paste CREATE template:**

> **Context:** Team uses LLMs but does not know why long chats degrade.  
> **Role:** Act as an LLM literacy coach.  
> **Expectation:** Focus on attention and context window practicality.  
> **Audience:** [analysts].  
> **Task:** One-page explainer + 3 usage habits.  
> **Examples:** Paste a bad long-chat experience.

**Worked CREATE example:**

> **Context:** Legal assistants paste 80-page PDFs into one chat.  
> **Role:** AI literacy lead.  
> **Expectation:** Push retrieval + chunking habits.  
> **Audience:** Legal ops.  
> **Task:** Explain why attention needs the right context and how to structure asks.  
> **Examples:** Missed indemnity clause because it was never in the prompt window.
"""

CONTENT[9] = """
## 9.5 STAR method for a Stable Diffusion brief

| Letter | Meaning | What you write |
|--------|---------|----------------|
| **S** | Situation | Where the image will be used |
| **T** | Task | What to generate |
| **A** | Action | Style, lighting, constraints, negatives |
| **R** | Result | Count, aspect ratio, selection criteria |

**Copy-paste STAR template:**

> **Situation:** Need visuals for [channel]. Brand mood: [words].  
> **Task:** Generate [N] image options of [subject].  
> **Action:** Style [photo/illustration]. Lighting [x]. Avoid [text/logos/faces].  
> **Result:** Shortlist [N] images at [aspect ratio] ready for design polish.

**Worked STAR example:**

> **Situation:** Warehouse-safety training banner, hopeful and professional.  
> **Task:** 6 options of safe PPE use without a real client site.  
> **Action:** Photoreal, soft daylight, no readable logos, no injured people.  
> **Result:** 3 finals in 16:9 with prompts saved beside files.

**Weak vs STAR:**

- Weak: “Make a warehouse image.”
- STAR: channel, mood, avoid-list, and aspect ratio.
"""

CONTENT[10] = """
## 10.5 CREATE method for explaining how AI learns images

| Letter | Meaning | What you write |
|--------|---------|----------------|
| **C** | Context | Why stakeholders ask “how does it learn?” |
| **R** | Role | Visual AI educator |
| **E** | Expectation | Dataset → training → prompt alignment |
| **A** | Audience | Design + product |
| **T** | Task | End-to-end learning story |
| **E** | Examples | Caption mismatch creating wrong outputs |

**Copy-paste CREATE template:**

> **Context:** Creative team trusts outputs too quickly.  
> **Role:** Act as a responsible image-AI educator.  
> **Expectation:** Cover data, training objective, and verification.  
> **Audience:** [designers].  
> **Task:** One-page “how image models learn” + checklist before publish.  
> **Examples:** Hands/text artifacts from your last campaign draft.

**Worked CREATE example:**

> **Context:** Marketing wants “AI product photos” for a new bottle.  
> **Role:** Brand-safe creative technologist.  
> **Expectation:** Explain why real packaging photos still matter for trust.  
> **Audience:** Brand manager.  
> **Task:** Learning pipeline summary + go/no-go checklist.  
> **Examples:** AI bottle with wrong label text last week.
"""

CONTENT[11] = """
## 11.5 STAR method for AI email drafting

| Letter | Meaning | What you write |
|--------|---------|----------------|
| **S** | Situation | Relationship, stakes, deadline |
| **T** | Task | The ask the email must achieve |
| **A** | Action | Tone, length, must include/avoid |
| **R** | Result | Subject + body ready to paste |

**Copy-paste STAR template:**

> **Situation:** Email [who] about [topic]. Relationship: [new/warm/tense].  
> **Task:** Get [decision/meeting/info].  
> **Action:** Tone [direct/warm/firm]. Max [N] words. One primary ask. No overpromising.  
> **Result:** Subject + body + 2 alternate subjects.

**Worked STAR example:**

> **Situation:** Follow up after demo with interested SMB buyer. Warm, medium stakes.  
> **Task:** Book a 20-minute technical review next week.  
> **Action:** Under 120 words, mention one demo detail, soft CTA.  
> **Result:** Email + 2 subject lines.

**Weak vs STAR:**

- Weak: “Write a follow-up.”
- STAR: relationship, ask, word limit, one concrete detail.
"""

CONTENT[12] = """
## 12.5 STAR method for AI report generation

| Letter | Meaning | What you write |
|--------|---------|----------------|
| **S** | Situation | Reporting period and decision needed |
| **T** | Task | Report type and sections |
| **A** | Action | Evidence rules and tone |
| **R** | Result | Skimmable deliverable + open questions |

**Copy-paste STAR template:**

> **Situation:** [weekly/monthly] report for [audience]. Decision: [what].  
> **Task:** Build [executive/client/ops] report from pasted data only.  
> **Action:** Do not invent metrics. Flag gaps. Calm risk language.  
> **Result:** Summary, wins, risks, asks (owner + date), Assumptions.

**Worked STAR example:**

> **Situation:** Monday ops review. Need weekend-coverage decision.  
> **Task:** 1-page support report from ticket export.  
> **Action:** No invented CSAT. Highlight volume spikes and staffing facts only.  
> **Result:** Brief + decision options A/B with trade-offs.

**Weak vs STAR:**

- Weak: “Make a report from this Sheet.”
- STAR: decision, no-invention rule, and required sections.
"""

CONTENT[13] = """
## 13.5 STAR method for AI presentation design

| Letter | Meaning | What you write |
|--------|---------|----------------|
| **S** | Situation | Audience, time, goal |
| **T** | Task | Card/slide count and topic |
| **A** | Action | Narrative arc and constraints |
| **R** | Result | Outline then slides, with ask slide |

**Copy-paste STAR template:**

> **Situation:** [audience], [N] minutes, goal: [decision/feeling].  
> **Task:** Create a [N]-card deck about [topic].  
> **Action:** Arc [problem→solution→ask]. One idea per card. Benefit headlines.  
> **Result:** Outline first, then cards + speaker notes on the ask.

**Worked STAR example:**

> **Situation:** L&D buyer, 12 minutes tomorrow.  
> **Task:** 12-card pitch for AI Practitioner training.  
> **Action:** Problem → method → curriculum → proof → pricing logic → ask.  
> **Result:** Presentable deck + one-sentence ask on final card.
"""

CONTENT[14] = """
## 14.5 CREATE method for deepfake verification

| Letter | Meaning | What you write |
|--------|---------|----------------|
| **C** | Context | Claim and channel where media appeared |
| **R** | Role | Careful media verifier |
| **E** | Expectation | Steps, not accusations |
| **A** | Audience | Comms / security / self |
| **T** | Task | Verification checklist and verdict options |
| **E** | Examples | Known authentic reference if available |

**Copy-paste CREATE template:**

> **Context:** [image/video/audio] claims [X]. Found on [channel].  
> **Role:** Act as a media-literacy investigator.  
> **Expectation:** Separate visual tells, metadata, and corroboration. Do not overclaim.  
> **Audience:** [comms lead].  
> **Task:** Step checklist + possible outcomes (likely real / uncertain / likely synthetic).  
> **Examples:** Link or describe reverse-search findings.

**Worked CREATE example:**

> **Context:** Urgent “CEO” video asks finance for a wire.  
> **Role:** Fraud-aware verifier.  
> **Expectation:** Escalate process, not panic.  
> **Audience:** Finance ops.  
> **Task:** Verification steps + call-back protocol.  
> **Examples:** Previous deepfake invoice cases in industry news.
"""

CONTENT[15] = """
## 15.5 STAR method for an AI security response brief

| Letter | Meaning | What you write |
|--------|---------|----------------|
| **S** | Situation | Threat or incident signal |
| **T** | Task | Immediate containment job |
| **A** | Action | Steps, owners, communications |
| **R** | Result | Contained state + evidence captured |

**Copy-paste STAR template:**

> **Situation:** [prompt leak / phishing / shadow AI finding].  
> **Task:** Contain and document within [time].  
> **Action:** Disable access, preserve logs, notify [roles], do not blame publicly yet.  
> **Result:** Incident note with timeline, impact, next controls.

**Worked STAR example:**

> **Situation:** Employee pasted customer PII into a public LLM.  
> **Task:** Contain exposure and start incident record today.  
> **Action:** Revoke/rotate related access if needed, collect chat export if available, notify security + DPO path.  
> **Result:** Incident ticket + interim staff guidance on approved tools.
"""

CONTENT[16] = """
## 16.5 CREATE method for an AI ethics / governance memo

| Letter | Meaning | What you write |
|--------|---------|----------------|
| **C** | Context | Use case and risk tier |
| **R** | Role | Governance facilitator |
| **E** | Expectation | Practical controls, not slogans |
| **A** | Audience | Risk + business owners |
| **T** | Task | Mini impact assessment |
| **E** | Examples | Who could be harmed if wrong |

**Copy-paste CREATE template:**

> **Context:** Proposed AI use: [case]. Data class: [public/internal/sensitive].  
> **Role:** Act as a responsible-AI facilitator.  
> **Expectation:** Name harms, controls, owner, and human oversight.  
> **Audience:** [risk committee].  
> **Task:** One-page ethics/governance memo.  
> **Examples:** Include one unfair or privacy failure mode.

**Worked CREATE example:**

> **Context:** Résumé-screening assistant for first shortlist.  
> **Role:** HR + AI governance lead.  
> **Expectation:** AI summarizes, humans decide.  
> **Audience:** CHRO + Legal.  
> **Task:** Impact notes, prohibited uses, review cadence.  
> **Examples:** Bias risk if training data over-represents one college.
"""

CONTENT[17] = """
## 17.5 STAR method for a functional AI pilot

| Letter | Meaning | What you write |
|--------|---------|----------------|
| **S** | Situation | Function pain and baseline |
| **T** | Task | Pilot scope |
| **A** | Action | Workflow, owner, review loop |
| **R** | Result | Success/stop criteria |

**Copy-paste STAR template:**

> **Situation:** In [function], [process] takes [time] with [error type].  
> **Task:** Pilot AI for [narrow step] only.  
> **Action:** Owner [name/role], data path [source], human review [when].  
> **Result:** After [N] weeks, [metric] improves or we stop.

**Worked STAR example:**

> **Situation:** Procurement exceptions take 25 minutes each.  
> **Task:** AI drafts exception summaries for human triage.  
> **Action:** Use invoice + PO text only, no auto-approval.  
> **Result:** Median handling time under 12 minutes on 50 cases, or stop.
"""

CONTENT[18] = """
## 18.5 CREATE method for AI strategy framing

| Letter | Meaning | What you write |
|--------|---------|----------------|
| **C** | Context | Business goals and constraints |
| **R** | Role | Strategy facilitator |
| **E** | Expectation | Portfolio, not a tool shopping list |
| **A** | Audience | Leadership |
| **T** | Task | 90-day strategy sketch |
| **E** | Examples | One quick win + one strategic bet |

**Copy-paste CREATE template:**

> **Context:** Company goal: [retention/cost/growth]. Constraints: [data/talent/risk].  
> **Role:** Act as an AI strategy facilitator.  
> **Expectation:** Quick wins, bets, experiments, owners, measures.  
> **Audience:** [ELT].  
> **Task:** One-page 90-day AI strategy sketch.  
> **Examples:** Name one process already digitized enough to win.

**Worked CREATE example:**

> **Context:** Service org wants retention via faster resolution.  
> **Role:** COO + AI lead ghostwriter.  
> **Expectation:** No model-name theater.  
> **Audience:** Executive leadership.  
> **Task:** Portfolio: agent assist (win), knowledge hygiene (bet), forecasting (experiment).  
> **Examples:** Current average handle time baseline.
"""

CONTENT[19] = """
## 19.5 STAR method for a strong ChatGPT brief

| Letter | Meaning | What you write |
|--------|---------|----------------|
| **S** | Situation | Job and constraints |
| **T** | Task | Deliverable |
| **A** | Action | Mode, tools, rules |
| **R** | Result | Format + verification |

**Copy-paste STAR template:**

> **Situation:** I am [role]. Need [outcome] for [audience].  
> **Task:** Produce [deliverable] in ChatGPT.  
> **Action:** Use [chat/project/file analysis]. Do not invent. Ask up to 5 clarifying questions if critical facts missing.  
> **Result:** [format]. End with Assumptions + What I should verify.

**Worked STAR example:**

> **Situation:** Analyst preparing Monday funnel review.  
> **Task:** Profile CSV then summarize conversion by channel.  
> **Action:** File analysis, flag small denominators, no fake causality.  
> **Result:** Table + 3 hypotheses labeled as hypotheses only.
"""

CONTENT[20] = """
## 20.5 CREATE method for a Gemini / Workspace brief

| Letter | Meaning | What you write |
|--------|---------|----------------|
| **C** | Context | Which Workspace app and file |
| **R** | Role | In-app collaborator |
| **E** | Expectation | Stay grounded in selected content |
| **A** | Audience | Reviewer / teammates |
| **T** | Task | Summarize, rewrite, or extract |
| **E** | Examples | Highlight the messy range/paragraph |

**Copy-paste CREATE template:**

> **Context:** Working in [Docs/Sheets/Gmail]. Content: [what].  
> **Role:** Act as a careful Workspace assistant.  
> **Expectation:** Use only selected content. Preserve names/numbers.  
> **Audience:** [manager].  
> **Task:** [summarize / rewrite / extract actions].  
> **Examples:** Point to rows/paragraphs that are source of truth.

**Worked CREATE example:**

> **Context:** Weekly KPI Sheet with raw exports.  
> **Role:** Ops briefing assistant inside Sheets/Docs.  
> **Expectation:** No invented metrics.  
> **Audience:** Leadership Monday review.  
> **Task:** Wins, risks, asks with proposed owners.  
> **Examples:** Highlight anomaly rows 12–20 for human check.
"""

CONTENT[21] = """
## 21.5 STAR method for a strong Claude brief

| Letter | Meaning | What you write |
|--------|---------|----------------|
| **S** | Situation | Project/files and stakes |
| **T** | Task | Careful analysis or writing job |
| **A** | Action | Source rules and process |
| **R** | Result | Deliverable + gaps list |

**Copy-paste STAR template:**

> **Situation:** Working in Project “[name]” with sources [list].  
> **Task:** Produce [FAQ/memo/rewrite] grounded only in sources.  
> **Action:** Extract → structure → simplify → flag conflicts. Never invent policy.  
> **Result:** [format] + Open questions + Source notes.

**Worked STAR example:**

> **Situation:** HR onboarding Project with policy PDF + welcome email.  
> **Task:** 12-question week-1 FAQ.  
> **Action:** Plain language, flag conflicts, no invented rules.  
> **Result:** FAQ + Day-1 checklist + unclear clauses for Legal.
"""

CONTENT[22] = """
## 22.5 CREATE method for LLM selection

| Letter | Meaning | What you write |
|--------|---------|----------------|
| **C** | Context | Use case and data class |
| **R** | Role | Model selector |
| **E** | Expectation | Compare on evidence, not brand loyalty |
| **A** | Audience | Buyer / team lead |
| **T** | Task | Recommend primary + fallback |
| **E** | Examples | Three eval prompts |

**Copy-paste CREATE template:**

> **Context:** Use case [x], data [public/internal], need [speed/quality/privacy].  
> **Role:** Act as an LLM selection advisor.  
> **Expectation:** Score quality, cost, latency, grounding, ecosystem.  
> **Audience:** [IT + business].  
> **Task:** Recommend primary model/tool and fallback.  
> **Examples:** Attach 3 representative prompts/outputs.

**Worked CREATE example:**

> **Context:** HR policy Q&A must cite current internal docs.  
> **Role:** Enterprise AI advisor.  
> **Expectation:** Grounded system over clever chat.  
> **Audience:** HR + Security.  
> **Task:** Choose stack (assistant + retrieval + review).  
> **Examples:** Three real policy questions with known answers.
"""

CONTENT[23] = """
## 23.5 STAR method for an AI automation scenario

| Letter | Meaning | What you write |
|--------|---------|----------------|
| **S** | Situation | Manual process pain |
| **T** | Task | What to automate first |
| **A** | Action | Trigger, AI step, human checkpoint |
| **R** | Result | Live test criteria |

**Copy-paste STAR template:**

> **Situation:** Manual process [describe]. Pain: [time/errors]. Apps: [list].  
> **Task:** Automate [handoff] without changing business rules.  
> **Action:** Trigger = [event]. AI = [interpret/draft]. Human = [approve]. Log = [fields].  
> **Result:** [N] clean test records + failure alert path.

**Worked STAR example:**

> **Situation:** Leads sit in a form overnight.  
> **Task:** Form → Sheet → Slack → draft welcome (human send).  
> **Action:** Filter invalid email, AI personalizes first line only, sales approves send.  
> **Result:** 3 test leads processed with logs.
"""

CONTENT[24] = """
## 24.5 STAR method for a make.com scenario design

| Letter | Meaning | What you write |
|--------|---------|----------------|
| **S** | Situation | Apps and failure pain |
| **T** | Task | Scenario to build |
| **A** | Action | Modules, filters, error route |
| **R** | Result | Scenario ON criteria |

**Copy-paste STAR template:**

> **Situation:** [App A] to [App B] is manual. Errors: [examples].  
> **Task:** Build make.com scenario for [flow].  
> **Action:** Trigger, filters, field mapping, error email/Slack, Sheet log.  
> **Result:** Pass 3 real tests including one bad record.

**Worked STAR example:**

> **Situation:** Course signup → Notion checklist is copy-paste.  
> **Task:** Webhook/form → Notion page + Slack notify.  
> **Action:** Filter consent=yes, map name/email/course, on error email ops.  
> **Result:** Scenario ON after three successful tests.
"""

CONTENT[25] = """
## 25.5 CREATE method for an n8n agent brief

| Letter | Meaning | What you write |
|--------|---------|----------------|
| **C** | Context | Goal and systems the agent may touch |
| **R** | Role | Agent architect |
| **E** | Expectation | Tools allowlist + approval gates |
| **A** | Audience | Builder + owner |
| **T** | Task | Design agent workflow |
| **E** | Examples | One happy path + one refusal path |

**Copy-paste CREATE template:**

> **Context:** Want an agent that [goal] using [systems].  
> **Role:** Act as an n8n agent architect.  
> **Expectation:** No open-ended tool use. Log every action.  
> **Audience:** [ops engineer].  
> **Task:** Trigger → retrieve → LLM reason → allowed tools → approval → log.  
> **Examples:** Include a case the agent must refuse.

**Worked CREATE example:**

> **Context:** Lead research digest before sales calls.  
> **Role:** n8n builder coach.  
> **Expectation:** Public research only, no auto-email.  
> **Audience:** Sales ops.  
> **Task:** Agent creates CRM note “AI research, verify.”  
> **Examples:** Refuse requests to infer protected characteristics.
"""

CONTENT[26] = """
## 26.5 CREATE method for a personal wrap-up plan

| Letter | Meaning | What you write |
|--------|---------|----------------|
| **C** | Context | What you learned and where you work |
| **R** | Role | Your own coach |
| **E** | Expectation | Concrete 30-day practice, not vague motivation |
| **A** | Audience | Yourself / manager |
| **T** | Task | Personal AI practice plan |
| **E** | Examples | One workflow you will change this month |

**Copy-paste CREATE template:**

> **Context:** Finished AI Ascent topics. My job: [role]. Biggest pain: [x].  
> **Role:** Act as a pragmatic practice coach.  
> **Expectation:** 30-day plan with weekly habits and one measurable win.  
> **Audience:** Me (and optionally my manager).  
> **Task:** Build a wrap-up practice plan.  
> **Examples:** The one process I will improve first.

**Worked CREATE example:**

> **Context:** Support lead, slow follow-ups, no automation yet.  
> **Role:** Practice coach.  
> **Expectation:** Small weekly drills + one make.com/n8n micro-flow.  
> **Audience:** Self.  
> **Task:** 30-day plan: prompts library, one STAR email habit, one automation.  
> **Examples:** Post-call follow-up currently takes 25 minutes.
"""

CONTENT[27] = """
## 27.5 STAR method for your program registration note

| Letter | Meaning | What you write |
|--------|---------|----------------|
| **S** | Situation | Your role and why now |
| **T** | Task | What you want from the program |
| **A** | Action | How you will practice during/after |
| **R** | Result | Outcome you want in 30–60 days |

**Copy-paste STAR template:**

> **Situation:** I am [role] at [org/context]. Current AI friction: [x].  
> **Task:** Join the AI Practitioner program to [goal].  
> **Action:** I will bring [de-identified example], practice weekly, and apply learning to [workflow].  
> **Result:** In [30/60] days I will have [measurable outcome] with clear controls.

**Worked STAR example:**

> **Situation:** Operations analyst, manual weekly KPI narrative takes half a day.  
> **Task:** Learn practical AI + light automation for reporting.  
> **Action:** Use approved tools only, build a reviewed draft workflow, document verification steps.  
> **Result:** KPI narrative under 45 minutes with zero invented metrics.

**Weak vs STAR:**

- Weak: “I want to learn AI.”
- STAR: role, workflow, practice plan, and a measurable result.
"""


def insert_sections(md: str) -> str:
    # Update intro how-to-read
    old_intro = """Each topic follows the same rhythm:

1. **Why this matters**: the practical stakes 
2. **Core concepts**: step-by-step foundations 
3. **Deep dive / frameworks**: models you can reuse 
4. **Worked examples**: concrete scenarios 
5. **Apply today**: a short action path 
6. **Key takeaways**: portable principles 
7. **Media**: topic image plus curated videos"""

    new_intro = """Each topic follows the same rhythm:

1. **Why this matters**: the practical stakes 
2. **Core concepts**: step-by-step foundations 
3. **Deep dive / frameworks**: models you can reuse 
4. **Worked examples**: concrete scenarios 
5. **STAR or CREATE method**: one prompting framework per topic (never both)
6. **Apply today**: a short action path 
7. **Key takeaways**: portable principles 
8. **Media**: topic image plus curated videos

**STAR** = Situation, Task, Action, Result. Use it when you already know the outcome and need a complete brief.

**CREATE** = Context, Role, Expectation, Audience, Task, Examples. Use it when you need a teaching, selection, or design brief with clear expectations."""

    if old_intro in md:
        md = md.replace(old_intro, new_intro)
    else:
        # fallback looser replace
        md = re.sub(
            r"Each topic follows the same rhythm:.*?Use the side panel",
            new_intro + "\n\nUse the side panel",
            md,
            count=1,
            flags=re.S,
        )

    for n in range(1, 28):
        method = METHODS[n]
        section = CONTENT[n].strip() + "\n\n"

        # Find ## n.4 Worked examples ... until ## n.5
        pattern = rf"(## {n}\.4 Worked examples\n.*?\n)(## {n}\.5 )"
        m = re.search(pattern, md, flags=re.S)
        if not m:
            raise SystemExit(f"Could not find topic {n} worked examples block")

        # Insert new  n.5 section, then renumber old 5->6, 6->7, 7->8, 8->9
        insertion = m.group(1) + section + f"## {n}.6 "
        md = md[: m.start()] + insertion + md[m.end() :]

        # Renumber remaining headings for this topic only (careful order high->low)
        # After insertion, old 5 became ## n.6 already for Apply today start.
        # Still need ## n.5 Apply -> already written as n.6 in insertion.
        # Fix: we replaced "## n.5 " with "## n.6 " in the insertion's second part.
        # Remaining: ## n.6 Key -> ## n.7, ## n.7 Media -> ## n.8, ## n.8 Registration -> ## n.9
        md = md.replace(f"## {n}.8 Registration", f"## {n}.9 Registration")
        md = md.replace(f"## {n}.7 Media", f"## {n}.8 Media")
        md = md.replace(f"## {n}.6 Key takeaways", f"## {n}.7 Key takeaways")
        # Apply today should already be ## n.6 from insertion; if any ## n.5 Apply left, fix
        md = md.replace(f"## {n}.5 Apply today", f"## {n}.6 Apply today")

        print(f"topic {n}: {method}")

    return md


def main() -> None:
    md = MD.read_text(encoding="utf-8")
    # Guard: don't double-insert
    if "## 1.5 CREATE method" in md or "## 1.5 STAR method" in md:
        raise SystemExit("STAR/CREATE sections already present. Abort.")
    new_md = insert_sections(md)
    MD.write_text(new_md, encoding="utf-8")
    print("Wrote", MD)


if __name__ == "__main__":
    main()
