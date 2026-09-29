# AfterAction project plan

## Decision
Build an incident-response memory agent for the on-call engineer responsible for a payment API. The narrow workflow is investigation → recall previous attempts → propose evidence-backed next steps → record the verified outcome → recall the new lesson on the next incident.

The distinguishing idea is **negative operational memory with an applicability gate**. A runbook says what to try. AfterAction also remembers what failed, the reason it failed, and the environment in which that evidence is valid. Contradictory outcomes are surfaced for review instead of silently choosing a winner.

## Why this use case
The supplied problem statements explicitly include incident response under Engineering & DevOps. Incidents have observable outcomes, so learning can be demonstrated without subjective personalization. An engineer can inspect the evidence behind a suggestion. A small team can adopt a read-only companion before trusting automation. This also fits the builder's experience with containers, load testing, and production debugging.

Alternatives considered: deal intelligence has a weaker short-demo feedback loop; generic support is crowded; accessibility audit memory is interesting but needs a credible labeled finding dataset and a more specialized evaluation. Incident response offers a clear, reproducible before/after story. This is a design judgment, not evidence of market uniqueness.

## Judging alignment
| Supplied criterion | Weight | Evidence in this project |
|---|---:|---|
| Innovation | 30% | Failed-action memory, explicit environment/architecture gates, contradictory-outcome detection |
| Hindsight | 25% | Real retain/recall/reflect HTTP adapter; no local retrieval fallback in live mode; visible call trace |
| Implementation | 20% | Persistent SQLite journal, outbox-style retry, validation, source-linked decisions, automated tests |
| Experience | 15% | One-screen investigation, baseline comparison, memory ledger, guided scenario |
| Impact | 10% | One on-call workflow; plausible pilot and measurable operational outcomes |

## Implementation plan
1. Build a portable Python 3.11+ application with a browser UI and no third-party Python dependencies.
2. Persist human-confirmed episodes in SQLite, retaining a stable document ID in Hindsight.
3. Recall candidates from Hindsight, resolve them to source episodes, and gate by service, environment, architecture, and explicit retirement.
4. Rank applicable successful attempts, warn about failed attempts, and abstain on conflicts.
5. Ask Hindsight reflect for a narrative using only eligible lesson tags; keep the source-derived decision panel separate from model-generated prose.
6. Provide a deliberately simple deterministic rehearsal backend, visibly labeled as not Hindsight.
7. Test failure learning, scope isolation, contradictions, persistence, redaction, retry behavior, and real HTTP adapter contracts using a fake API server.
8. Package source, Docker option, setup instructions, a guided demo, evaluation instructions, and content drafts.

## 60-second demo story
A fictional payment API is timing out during a promotion. With no memory, AfterAction requests evidence and gives a generic investigation checklist. Retain three synthetic incident outcomes. Investigate again: restarting all workers is flagged because it previously caused reconnect pressure; capping concurrency becomes a candidate based on a previous successful attempt. Change architecture from direct Postgres connections to PgBouncer: the old lessons are withheld. Record a new outcome for this architecture, and see it appear on the next investigation.

## Scope and honest claims
No command execution, Kubernetes integration, production deployment, real customer data, automatic incident detection, or proven reduction in resolution time. This is a working local prototype with a real external integration requiring credentials. Exact-context gating is conservative and is not a complete causal model. The rehearsal path is not an AI model or a substitute for demonstrating Hindsight.

## Pilot hypothesis
Invite 3–5 engineers to replay sanitized closed incidents. Measure evidence correctness, applicability errors, contradiction detection, and time to find a relevant previous attempt. Compare blind incident-only responses with memory-assisted responses on the same cases. Report raw cases and failures, not a claimed percentage improvement based on the synthetic demo.
