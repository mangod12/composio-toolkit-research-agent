# Composio Toolkit Research Agent

Submission artifact for Composio's AI Product Ops Intern take-home.

## What this does

This repo contains a deterministic research pipeline for classifying 100 requested apps by:

- category and one-line description
- likely auth model
- self-serve vs gated access
- API surface
- MCP/toolkit buildability verdict
- evidence URL
- confidence and human-review flags

The goal is not to pretend the agent is perfect. The goal is to show a repeatable workflow, source-grounded first pass, pattern extraction, and a manual verification loop.

## Differentiator

Most submissions can produce a 100-row table. This one adds a product-ops decision layer: each app gets a `priority_score` and `launch_motion`, turning raw research into a recommended build queue for Composio. That makes the output operationally useful: it separates "build now", "build after OAuth setup", "prototype wrapper", and "qualify through outreach" work.

## Run

```bash
python scripts/research_agent.py
```

Outputs:

- `data/results.csv`
- `data/verified_sample.csv`
- `data/summary.json`
- `index.html`

## Agent design

The pipeline uses the assignment's app list, official docs hints, source URL heuristics, lightweight page fetching, and deterministic classification rules. It prefers official developer/API docs over blogs or forums. Every row gets a confidence rating and uncertain rows are marked for human review.

Manual verification is represented in `data/verified_sample.csv`: 20 apps across easy, OAuth-heavy, gated, and unclear cases were spot-checked against official docs.

## Reviewer note

This is a fast 6-8 hour assignment-style build. Rows marked `Medium` or `Low` should be treated as candidates for deeper follow-up before production toolkit implementation.
