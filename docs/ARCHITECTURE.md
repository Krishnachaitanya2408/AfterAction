# Architecture and boundaries

AfterAction is a single-operator local application. Python serves static browser assets and JSON endpoints. A SQLite journal stores reviewed source episodes and the last synchronized Hindsight target. The configured provider implements retain, recall and reflect. The application contains no arbitrary command-execution tool.

## Evidence flow

In live mode, recall searches Hindsight with strict service and environment tags. Returned source metadata/context/chunks are resolved to stable local episode IDs. Only episodes synchronized to the current base URL and bank can be used. The deterministic gate checks service, environment, architecture and retirement. The panel groups actions by normalized exact name and displays success, failure, inconclusive or conflicting outcomes.

Reflect receives the current incident and the source-derived panel. Its retrieval tags intersect the current service/environment with eligible lesson IDs; unscoped mental models are excluded. Reflection is visibly advisory and cannot alter the source-derived panel. The app does not parse generated text into executable commands. A shared bank with existing global directives should not be used; create a dedicated bank.

Retention writes the local journal first, then makes a synchronous request. Only a confirmed success marks the current target as synchronized. A failed request leaves an inspectable local record for manual retry. A changed bank automatically requires re-sync. Rehearsal records never count as Hindsight-synchronized records.

## HTTP surface

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/state` | GET | Mode, source ledger, sample incident, trace and pending count |
| `/api/export` | GET | Download local source ledger as JSON |
| `/api/investigate` | POST | Incident context and `use_memory` → comparison side |
| `/api/lessons` | POST | Reviewed outcome with `confirmed: true` → retained record |
| `/api/seed` | POST | Idempotently add the three fictional sample records |
| `/api/sync` | POST | Retry unsynchronized source records |
| `/api/retire` | POST | Suppress a source ID in future local decisions |

POST requires `Content-Type: application/json` and `X-AfterAction: 1`. Input size is bounded. Mutation/investigation requests are serialized with a nonblocking lock; a concurrent request receives 409. Only explicit static paths are served. Responses apply a restrictive content-security policy; user text is escaped in the UI. The app checks Host and Origin and binds to loopback by default. These controls do not replace authentication for deployment.

## Hindsight contract

The adapter uses POST routes relative to `/v1/default/banks/{bank_id}`:

- `/memories`: `items` with source content, context, timestamp, metadata, document_id and tags; `async: false`.
- `/memories/recall`: query, strict scope tags, raw fact types and source chunks.
- `/reflect`: query, tag groups, bounded response length and included supporting facts.

The interface was checked against official Hindsight API documentation. Fake-server tests verify wire shapes and handling; actual compatibility must be confirmed with `live_check.py` against the user's deployment. No claim of a completed credentialed run is made.

## Extension priorities

For a real pilot: add authenticated users with per-organization banks, a reviewed incident import pipeline, structured action identifiers, version ranges and expiry, durable asynchronous retention jobs, telemetry and labeled retrieval evaluations. Only consider action execution after defining approvals and rollback semantics. These are future work, not current features.
