# Composio Toolkit Research Agent

Submission artifact for Composio's AI Product Ops Intern take-home assignment.

## Links

- Live case study: https://rawcdn.githack.com/mangod12/composio-toolkit-research-agent/abd6b001fcc8ea49eff9d47f4f5c7760dc801e73/index.html
- Source repo: https://github.com/mangod12/composio-toolkit-research-agent
- GitHub Pages mirror: https://mangod12.github.io/composio-toolkit-research-agent/

Use the RawCDN link for review because it is pinned to the final submitted commit. The GitHub Pages mirror may lag while GitHub Pages finishes rebuilding.

## One-Minute Interview Pitch

I built a reproducible research agent for Composio's 100-app toolkit research task. The agent classifies each app by category, auth method, self-serve vs gated access, API surface, MCP/tooling signal, buildability verdict, blocker, evidence URL, confidence, and human-review need.

The main point is not the table itself. The main point is the workflow: I turned a manual research problem into a repeatable pipeline, added a verification loop, reported misses honestly, and added a product-ops build queue so Composio can decide which integrations to build first.

## What Problem This Solves

Composio turns apps into tools that AI agents can call. Before building a toolkit for an app, the team needs to know:

- whether developer credentials are self-serve or gated
- whether the app has public REST, GraphQL, CLI, or unclear API access
- what auth model is required
- whether existing MCP/tooling signals already exist
- whether the toolkit can be built now or needs outreach/account setup
- which apps are the highest-confidence easy wins

Doing this manually across hundreds of apps does not scale. This project is a small version of that workflow.

## Final Output

The generated case study includes:

- a headline summary of the 100-app scan
- auth and buildability patterns
- a recommended build queue
- category-level buildability matrix
- 20-app manual verification sample
- first-pass misses and caveats
- full 100-row evidence table
- runnable reproduction command

## How To Run

```bash
python scripts/research_agent.py
```

The script writes:

- `data/results.csv`
- `data/verified_sample.csv`
- `data/summary.json`
- `index.html`

Runtime is roughly 2 minutes on my machine because the script does lightweight fetch probes against many external documentation pages. A production version should parallelize fetches and cache page probes.

## Repository Structure

```text
.
|-- data/
|   |-- apps.csv                 # 100-app input set
|   |-- results.csv              # generated 100-row research output
|   |-- summary.json             # generated aggregate metrics and build queue
|   `-- verified_sample.csv      # generated 20-app verification sample
|-- scripts/
|   `-- research_agent.py        # research/classification/report generator
|-- index.html                   # generated single-page case study
`-- README.md                    # process and interview explanation
```

## How The Agent Works

The pipeline is deterministic and source-grounded. It is not pretending that an LLM magically knows everything.

1. Load the 100 apps from `data/apps.csv`.
2. Attach the best known evidence URL for each app, preferably official developer/API docs.
3. Probe each evidence URL with a lightweight fetch.
4. Infer auth model using explicit overrides and page-text signals.
5. Infer API surface using reviewed overrides and docs-page signals.
6. Mark self-serve vs gated using known access constraints.
7. Assign a buildability verdict and blocker.
8. Assign confidence and human-review flags.
9. Generate summary metrics and a build queue.
10. Generate the final HTML case study.

## Key Classification Rules

The script uses several explicit rule groups:

- `EVIDENCE_URLS`: official docs or best available evidence for each app
- `AUTH_OVERRIDES`: app-specific auth cases such as Twilio, Telegram, Stripe, Binance, NotebookLM
- `GATED_APPS`: apps that need approval, partner access, paid accounts, merchant accounts, or unclear public docs
- `API_SURFACE_OVERRIDES`: reviewed corrections for apps where naive page-text matching can misclassify REST vs GraphQL
- `EXISTING_MCP`: known or likely MCP/tooling signals
- `VERIFIED_APPS`: 20-app manual verification sample

This structure makes the agent auditable. If a classification is wrong, there is a clear place to correct the rule.

## Differentiator

Most submissions can produce a 100-row table. This project adds a product-ops decision layer.

Each app gets:

- `priority_score`: an implementation-readiness score
- `launch_motion`: the next operational action

The launch motions are:

- Build now: self-serve API and simple credential path
- Build after OAuth app/scopes are mapped
- Prototype wrapper, then validate real user demand
- Qualify first: outreach, partner access, or paid account needed

This turns raw research into a build queue. That is closer to what a Product Ops intern would actually help with: not just collecting information, but helping decide what work should happen next.

## Current Findings

From the generated summary:

- 100 apps analyzed
- 80 apps are self-serve or trial likely
- 20 apps are gated or approval constrained
- OAuth2 is the most common auth pattern: 47 apps
- API key/token patterns are next: 31 apps
- 45 apps are buildable with auth setup
- 33 apps are ready for toolkit work
- 20 apps need outreach or account setup
- 2 apps are better treated as wrappers

The strongest easy-win categories are support/helpdesk, productivity/project management, developer tools, data/SEO/scraping, and self-serve SaaS APIs.

The main blocker is not API complexity. The common blocker is access: app review, developer tokens, partner programs, enterprise tenants, merchant credentials, or paid/admin account gates.

## Verification Loop

The assignment asked for accuracy, not just output volume. I used three layers:

1. Deterministic rules and official evidence URLs
2. Lightweight docs fetch probes
3. Manual spot-checking of 20 representative apps

The verification sample includes easy APIs, OAuth-heavy tools, gated APIs, enterprise/ads/fintech cases, CLI/wrapper cases, and unclear AI/media apps.

Sample result:

- 18 of 20 manually checked rows were clear matches against linked docs.
- 2 of 20 were kept as partials needing follow-up.

The important correction from the verification loop: the first pass treated some product pages as potentially API-ready. After manual checks, the stricter rule became: if public API docs are not clearly discoverable, mark the app gated/unclear and flag it for human review.

## Known Limitations

This is a 6-8 hour assignment-style build, not a production integration intelligence system.

Limitations:

- It does not create paid accounts.
- It does not complete OAuth app reviews.
- It does not enter partner programs.
- It does not prove every endpoint works with real credentials.
- It uses sequential fetch probes, so runtime can be slow.
- Some classifications require business context, not only public docs.
- `priority_score` is implementation-readiness, not market demand.

These are not hidden. The case study surfaces medium/low-confidence rows and human-review flags.

## If Asked Why I Did Not Use Composio SDK

Answer:

The assignment allowed an agent, script, or pipeline. Given the timebox, I prioritized accuracy, reproducibility, and a clear verification loop. Composio SDK/MCP would be a good next iteration: the same input/output structure could be wrapped as a Composio-powered research agent that calls browser, search, docs, and spreadsheet tools.

## If Asked What I Would Improve Next

I would improve the system in this order:

1. Parallelize and cache docs fetches.
2. Add browser-use checks for pages that block simple HTTP fetches.
3. Store evidence snippets, not only evidence URLs.
4. Add per-field verification status, not only per-app verification status.
5. Add demand scoring if customer request frequency is available.
6. Add a Composio SDK/MCP wrapper around the same research workflow.
7. Export a machine-readable JSON contract for downstream toolkit planning.

## If Asked About The Priority Score

The priority score is not a claim about customer demand. It is an implementation-readiness score.

It rewards:

- high confidence
- clear public API surface
- self-serve credentials
- simpler auth path
- existing MCP/tooling signals
- immediate buildability

Apps with the same score should be treated as a readiness tier, not as a perfectly ordered roadmap.

## If Asked About Gated Apps

Gated apps are not failures. The assignment explicitly says that if an app is behind payment, partnership, or approval, identifying that with evidence is the correct finding.

Examples:

- Google Ads needs OAuth and developer-token approval.
- LinkedIn Ads is permissioned/review gated.
- Amazon Selling Partner has LWA, AWS, seller/vendor, and app-review setup.
- PitchBook is enterprise/commercial access gated.
- NotebookLM does not expose a general consumer public API.

## If Asked What I Personally Built

I built:

- the research pipeline
- the classification rules
- the generated CSV outputs
- the summary and build queue logic
- the HTML case study generator
- the manual verification sample
- the final deployable single-page artifact

AI tooling helped accelerate the work, but the rules, caveats, verification, and product-ops framing are explainable from the repo.

## Main Interview Defense

The best way to explain the project:

> I treated the assignment as a product-ops workflow, not a spreadsheet task. The agent creates the first-pass research, the verification loop catches overconfident classifications, and the final output tells Composio what to build now, what needs OAuth setup, what can be wrapped, and what needs outreach first.

That is the core differentiator.
