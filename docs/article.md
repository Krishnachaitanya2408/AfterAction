# I Made Hindsight Remember the Fixes That Failed

A previous fix can be the wrong suggestion for the next incident. I built AfterAction around that problem: an incident-response agent should remember failed attempts and the conditions around them, not just collect successful runbooks.

The workflow is intentionally narrow. An on-call engineer describes an incident, reviews relevant previous outcomes, and records what happened after an intervention. That recorded experience can change the next investigation. The prototype never executes infrastructure commands.

## The missing half of an incident history

A useful postmortem usually includes the resolution. The path to that resolution can be just as valuable: the restart that increased connection pressure, the configuration change that had no effect, or the fix that worked in staging but failed under production load.

I wanted those outcomes to remain visible to the agent. More importantly, I wanted their boundaries to remain visible. “This worked before” is an incomplete statement unless the system can also explain where, when, and under which architecture it worked.

The example bundled with AfterAction is fictional. A payment API experiences checkout timeouts while database connections are saturated. Restarting all workers worsens reconnect pressure in one recorded production incident. A later concurrency change helps. A separate staging incident reports a successful restart.

Those records create a useful test: can the system preserve the failed production attempt without treating the staging success as evidence that restarting production is a good idea?

## Where Hindsight belongs

I use [Hindsight's persistent agent memory](https://github.com/vectorize-io/hindsight) for three operations. Retain stores reviewed outcomes. Recall searches for relevant experience. Reflect produces an explanation grounded in the applicable evidence.

The local application is a small Python server with a browser interface and SQLite source journal. Keeping the original outcome record locally makes it possible to show the engineer exactly what was reported. Hindsight supplies the memory retrieval and model-backed reflection; the journal supplies inspectable source records and synchronization state.

This separation matters. In live mode, a local record does not become evidence merely because it exists. Hindsight must return a resolvable reference to it. If the memory service is unavailable, the application reports the failure instead of quietly switching to local search and presenting that result as a successful AI response.

The [Hindsight API documentation](https://hindsight.vectorize.io/) provides the integration contract. AfterAction uses direct HTTP calls so its local setup needs only Python's standard library.

## Retain outcomes rather than recommendations

The first design decision is about what enters memory. A generated recommendation is not a verified experience. Storing the agent's own suggestion as though it worked would create a feedback loop in which repetition looks like evidence.

AfterAction therefore retains outcomes through an explicit review form. The engineer records the incident context, attempted action, observed result, explanation and timestamp. The outcome must be marked helped, failed or inconclusive. A confirmation checkbox separates the act of reviewing guidance from the act of asserting that something happened.

Each retained episode gets a stable source identifier. The adapter includes that identifier in the document ID, context and metadata, so recall has multiple ways to preserve provenance. These fields come directly from `afteraction/memory.py`:

```python
'context': 'AfterAction source ' + row['id'],
'document_id': row['id'],
'metadata': {'lesson_id': row['id']},
```

The application saves locally before making the external retention request. If that request fails, the source remains available and pending synchronization. Retrying does not require the engineer to retype the incident from memory. A stable document ID also gives retries a consistent source identity.

This is deliberately simpler than a production job queue. There is a visible retry operation, and the README describes the limitations of synchronous retention and lost acknowledgements.

## Similarity is not applicability

Finding a similar incident is only the start. An agent can retrieve an accurate historical fact and still make a poor recommendation if it applies the fact to the wrong system.

AfterAction filters live recall by service and environment. Then a deterministic gate checks the resolved source records against the current context. The core check in `afteraction/domain.py` is short:

```python
mismatches = [
    k for k in ('service', 'environment', 'architecture')
    if row[k] != current[k]
]
```

The gate also excludes records explicitly retired by the operator. This means an old episode can remain in the ledger for inspection without remaining eligible for future recommendations.

Architecture is currently a human-supplied compatibility label. In the sample, `direct-postgres` and `pgbouncer` are different labels. Changing the current incident to the latter withholds the old direct-connection lessons. That is conservative, and it is useful for demonstrating the boundary, but it is not a complete model of dependency versions or system compatibility.

I would rather expose that limitation than hide it behind a confidence score. The application does not have the evidence to calculate a calibrated probability that a previous fix will work.

## Let contradictions interrupt the recommendation

The next decision is how to handle disagreement. If one outcome says an action helped and another says it failed, simply selecting the newest record would discard potentially important context.

The prototype groups applicable episodes by normalized action name. Opposite outcomes move the action into a review category rather than the suggested-action category:

```python
if {'helped', 'failed'} <= outcomes:
    conflicts.append(item)
```

The engineer sees the source identifiers and explanations on both sides. That creates a reason to ask what changed: load, deployment version, connection limits, or something not captured in the current schema.

Exact action-name matching is a limitation. “Restart all payment workers” and “Recycle the worker deployment” will not necessarily be grouped as the same action. Structured action identifiers would be a useful next step. Silently claiming semantic contradiction detection would overstate what the code does.

## Keep generated explanation separate from recorded evidence

The interface distinguishes the source-derived decision panel from Hindsight's generated reflection. The panel displays applicable successful attempts, previous failures, inconclusive outcomes and conflicts. The reflection explains the evidence and suggests an additional read-only check.

Reflect is scoped to the eligible lesson identifiers. That narrows the context after the applicability gate, instead of asking a model to remember every exclusion while searching unrestricted history. Generated prose still requires review; source filtering does not make a language model infallible.

This is the practical value I wanted from [agent memory](https://vectorize.io/what-is-agent-memory): retained experience can change the next response, while the user can inspect why it changed. The learning is in the accumulated experience and retrieval loop, not a claim that the application fine-tunes model weights.

## What the walkthrough does and does not prove

The same sample incident can be compared before and after retaining the fictional outcomes. With no applicable history, the application uses a generic investigation checklist. After the outcomes are available, it can show the previously failed restart and the earlier useful concurrency intervention. Changing architecture withholds those records; recording a reviewed outcome for the new architecture creates new applicable evidence.

The offline suite checks that behavior, along with persistence, retirement, conflicting outcomes, validation and failed external writes. A fake HTTP server exercises the adapter contract. Those tests are not a substitute for a credentialed Hindsight run. The package includes a separate live acceptance command, and real provider behavior must be checked before publishing a walkthrough.

There is also a visibly labeled rehearsal mode. It uses deterministic token overlap so someone can inspect the workflow without credentials. It is not an AI model, and its output is not evidence of Hindsight performance.

I have not measured reduced resolution time or tested this with real production incident histories. The next useful evaluation would ask engineers to replay sanitized closed incidents and inspect whether the recalled lessons were relevant, applicable and correctly attributed.

## What I would carry into the next version

Three choices are worth preserving: retain reviewed outcomes instead of predictions, separate applicability from similarity, and make contradictory evidence interrupt advice. They are small implementation decisions with direct consequences for what an engineer sees during an investigation.

The next version needs richer compatibility constraints, better action identifiers and a real evaluation set. Until then, AfterAction has a clear boundary: it helps an engineer reason from previous experience, while leaving the decision and the intervention with that engineer.
