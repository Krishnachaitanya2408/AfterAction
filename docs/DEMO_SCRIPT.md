# Demo recording script

Target: 3–4 minutes, 1080p or better, screen recording with narration. Replace placeholders with actual team details. Record the real Hindsight mode after `live_check.py` succeeds. Never show the `.env` file or API key.

## Preparation

Use a dedicated demo bank. For the clearest first comparison use a fresh local database and empty bank. Start the app, open the browser, enlarge text, close unrelated tabs and notifications. Rehearse with synthetic records only. Retain and reflect can take time; do not disguise rehearsal output as live AI output.

## 0:00–0:25 — Introduce the problem

Screen: Investigation page, header visibly says HINDSIGHT LIVE.

“Hi, I'm Raghuchandra. This is AfterAction, a memory companion for an on-call engineer. A runbook remembers what to try. I wanted the agent to also remember what made an incident worse, and when that experience no longer applies.”

## 0:25–0:55 — Show the starting point

Screen: Keep the sample payment incident and click Compare without / with memory before loading records.

“These are fictional checkout timeouts with database connection pressure. With no recorded history, there is no evidence-backed fix. The app starts with a generic investigation checklist and asks for more evidence.”

## 0:55–1:40 — Retain and recall

Screen: Load 3 sample outcomes; show the Memory activity retain rows and memory ledger. Return to Investigation and compare again.

“Now I am retaining three reviewed outcomes in Hindsight. In the production example, restarting every worker made connection pressure worse. A later bounded concurrency change helped. There is also a staging example where a restart worked. The app must not treat staging evidence as a production success.”

Screen: Show warning and candidate action, expand source records and raw Hindsight facts.

“Hindsight retrieves the history. The source-derived panel links each action back to an outcome record. The generated reflection explains what to check next. The candidate is still a hypothesis, not permission to change production.”

## 1:40–2:10 — Show where memory should stop

Screen: Change architecture to `pgbouncer`, compare again.

“The system has changed. The old direct-connection evidence may no longer apply. AfterAction withholds those actions instead of sounding confident because it found a similar incident.”

## 2:10–3:05 — Close the feedback loop

Screen: Record outcome tab. Set architecture `pgbouncer`, symptom `Checkout timeouts during promotion with saturated database connections`, action `Inspect PgBouncer pool wait time before changing worker limits`, outcome Helped, explanation `Synthetic exercise: pool wait time exposed the bottleneck; read-only inspection narrowed the investigation.` Confirm and retain. Return to Investigation with the same architecture and compare.

“This is the learning loop: a reviewed result becomes evidence for the next investigation. Memory persists across sessions. The agent does not train new model weights; it changes its next response using retained experience.”

## 3:05–3:30 — Finish honestly

Screen: Memory activity showing retain, recall, reflect; then source ledger.

“The key idea is to remember failed attempts and their conditions, not just successful runbooks. This prototype is read-only. Next I would evaluate it with sanitized incident histories from engineers and measure applicability errors before considering automation.”

Optional if time allows: record an opposite outcome for the exact same action name, then show Needs review. Do not claim a reduction in incident resolution time: no operational benchmark has been performed.

## Video title ideas

- My incident agent remembers the fixes that failed
- Building an incident memory loop with Hindsight
- When yesterday's fix becomes today's bad advice
- Why my incident agent sometimes refuses to recommend a fix
- From failed attempts to useful operational memory
