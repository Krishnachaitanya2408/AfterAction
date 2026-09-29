# Submission checklist

This checklist is based on the two supplied documents. It does not establish the current deadline, team-size rules, or exact shortlist form; verify those with the organizers.

## Must do before submitting

- [ ] Read `PROJECT_PLAN.md` and understand the design well enough to explain it without a script.
- [ ] Create Hindsight bank and API key; configure `.env`.
- [ ] Run the offline tests and `live_check.py`.
- [ ] Demonstrate actual Hindsight retain, recall and reflect; do not use rehearsal output as proof.
- [ ] Inspect the entire browser UI, including the outcome form and a mobile-width window.
- [ ] Record a new outcome live and show that a subsequent investigation changes.
- [ ] Use a fresh context or retired source to show the applicability boundary.
- [ ] Create a public GitHub repository with README and clean source.
- [ ] Confirm no `.env`, database, customer log, credentials or private screenshots are committed.
- [ ] Provide a live project demonstration. If a hosted URL is mandatory, deploy a hardened version; local-only hosting is the current implementation.
- [ ] Record a 2–5 minute 1080p video and publish it publicly on YouTube.
- [ ] Add real project, video and content links to the submission form.

## Content guide requirements

The problem statement broadly says all members complete content deliverables. The more detailed content guide specifies **one article and one social post per member, and one video per team**. Follow the detailed guide and ask the organizers if their actual submission form says otherwise.

- [ ] Each member publishes an individual English article on a public developer publishing platform.
- [ ] Article length: aim for 1,200–1,500 words, which overlaps the guide's inconsistent 800–1,500 and 1,200–2,000 ranges.
- [ ] **Do not use the word “hackathon” anywhere in the article or social post, including titles and hashtags.** The guide explicitly lists this as disqualifying for those content submissions.
- [ ] Include Hindsight GitHub, documentation and agent-memory links in the article.
- [ ] Add screenshots of the real app and live memory operations; do not expose credentials.
- [ ] Replace all placeholders and verify every factual claim against what you actually ran.
- [ ] Publish the article, then share it as a Link post to one of the specified communities: r/llmdevs, r/sideproject, r/aiagents or r/aimemory, following that community's rules.
- [ ] Each member publishes a social post under 800 characters, with their actual public project repository link.
- [ ] Add article and Hindsight repository links in comments, as requested in the guide.
- [ ] Tag Code.in on LinkedIn and articles as requested; select the correct official account.
- [ ] Publish one public team video on YouTube with a suitable thumbnail. The guide suggests Nano Banana; use team images only with permission.

Nothing has been published or sent on your behalf. Included content is draft material, not evidence that these steps are complete.

## Suggested submission description

AfterAction is an incident-response memory agent for on-call engineers. It uses Hindsight to retain reviewed outcomes, recall similar incident history and explain evidence-backed next steps. Its distinguishing behavior is negative operational memory: remembering failed actions and refusing to reuse evidence when the environment or architecture no longer matches. A local source journal makes the original outcomes inspectable, while a deterministic applicability gate separates recorded evidence from generated guidance. The demo follows a fictional payment API outage through an empty-memory baseline, learned failed actions, a context change and a newly retained outcome. The prototype is read-only and never executes infrastructure commands.

Use this description only after verifying the real Hindsight integration in your environment. Add team-specific details and verified links separately.
