# Verification report

## Executed checks

- Python 3.12: application imports and compilation passed.
- Node JavaScript syntax check: `node --check afteraction/static/app.js` passed.
- `python -m unittest discover -s tests -v`: 30 tests passed.
- Actual local HTTP startup at port 8000 succeeded.
- Static homepage and HEAD request, JSON validation, unsupported paths, Host/Origin checks and required mutation headers tested against a running HTTP server.
- Article checked at 1,353 words; social draft at 610 characters before replacing the repository placeholder. Neither draft contains the prohibited event word.

The 30 tests include repeated domain behavior against both the rehearsal provider and a localhost fake Hindsight API. They are not 30 independent real-world incidents and are not an AI-quality benchmark.

## Behavior covered

| Case | Expected result | Status |
|---|---|---|
| Empty memory | No suggested historical fix | Passed |
| Failed production restart | Warning citing failed source | Passed |
| Successful bounded intervention | Candidate action citing source | Passed |
| Staging success | Not treated as production success | Passed |
| Architecture change | Old fixes withheld | Passed |
| New architecture outcome | New source can guide that context | Passed |
| Opposite outcomes for identical action | Conflict, no candidate suggestion | Passed |
| Retired source | Withheld from future decisions | Passed |
| Restart application | Source history persists | Passed |
| Repeated sample seed | No duplicate source episodes | Passed |
| Hindsight retain failure | Local source preserved for retry | Passed with fake provider |
| Hindsight recall failure | No silent local fallback | Passed with fake provider |
| Local-only unsynced episode | Not promoted to live evidence | Passed with fake provider |
| Reflect scope | Restricted to eligible lesson IDs | Passed with fake provider |

## Not executed

- Credentialed Hindsight Cloud or self-hosted integration. No account key was supplied. Run `live_check.py`, then inspect actual returned facts and reflection.
- Browser screenshot/layout and full interactive browser tests. Playwright was available, but the browser binary was absent and its download failed. No screenshot is supplied or claimed. Inspect the UI on desktop and mobile widths before recording.
- Docker build/runtime, Windows launcher execution, macOS execution, public hosting, real production incident data, security penetration testing, or operational impact measurements.

## Manual acceptance sequence

1. Start in rehearsal mode. Ensure the banner makes that explicit.
2. Compare before loading outcomes: no applicable source history.
3. Load outcomes and compare: one failed action warning, one candidate action. Inspect source IDs.
4. Switch architecture: no applicable direct-connection fix.
5. Submit a reviewed outcome for the new architecture; compare again.
6. Record the opposite outcome for the exact action name: Needs review replaces the candidate.
7. Retire a source, refresh, and verify it is excluded.
8. Open Memory ledger, export JSON, restart the server and verify persistence.
9. Configure a dedicated Hindsight bank. Run `live_check.py` and repeat steps 2–8 with actual memory calls.
10. Capture screenshots and a 1080p video only after verifying all live behavior.

When evaluating on real sanitized incidents, track source correctness, wrong-context suggestions, missed contradictory evidence, and time to locate a relevant previous attempt. Keep the individual cases and failures visible. Do not extrapolate the synthetic walkthrough into MTTR claims.
