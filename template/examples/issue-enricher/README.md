# Loop Engineering E2E Example: Issue Enricher

> Crawl open-source issue trackers and enrich issues with context.
> A project management use case -- zero paid APIs, fully OS-legal.

## The problem

Your project has 200+ issues. Many are duplicates, stale, or missing context.
You need to enrich each issue with: related issues, linked PRs, code references,
contributor activity, and a concise summary -- using only free, open-source tools.

## Quick start

```bash
cd template/examples/issue-enricher

# Enrich a single issue (dry run, no API calls)
python loop.py "baseline: parse issue body only"

# Enrich with related issue detection
python loop.py "find related issues by keyword overlap"

# Check the state
cat STATE.md
```

## The clever parts

1. **GitHub REST API** -- free for public repos (60 req/hour unauthenticated). No tokens needed.
2. **Regex archaeology** -- `fixes #123`, `closes #456`, `src/foo.py:42`, `function_name()`
3. **Keyword graph** -- build a similarity graph between issues using word overlap (no embeddings needed)
4. **Velocity metrics** -- time-to-first-response, time-to-close, stale detection
5. **robots.txt compliance** -- respects `Crawl-delay`, never hits rate limits
6. **Zero LLM by default** -- the enrichment is pure heuristics. Optional 1x DeepSeek call for summary.

## What this example demonstrates

| Loop phase | File | What it does |
|-----------|------|-------------|
| **Plan** | `loop.py` -> `plan()` | Generates an enrichment strategy from a hypothesis |
| **Execute** | `experiment.py` | Crawls issues, extracts context, measures enrichment depth |
| **Evaluate** | `evaluate.py` | Computes coverage, related-issue precision, fitness |
| **Decide** | `loop.py` -> `decide()` | SHIP / RETRAIN / PIVOT based on metrics |
| **State** | `STATE.md` | Durable memory spine |
| **Genesis** | `genesis.md` | What we're reducing, when to stop, what never to sacrifice |

## Legal compliance

- Uses only GitHub REST API (public endpoints, no auth required)
- Respects `robots.txt` and `Crawl-delay` headers
- Rate-limits to 1 request/second (well under GitHub's 60/hour limit)
- Never stores raw HTML -- only structured JSON from API responses
- All code is Apache 2.0 licensed

## Files

```
issue-enricher/
├── loop.py              <- Four-phase runner
├── experiment.py        <- Issue crawling + enrichment
├── evaluate.py          <- Metric computation
├── data.py              <- Sample issues (20 issues from a real repo)
├── enricher.py          <- Core enrichment engine (regex, heuristics, graph)
├── crawler.py           <- GitHub API crawler (rate-limited, robots.txt compliant)
├── STATE.md             <- Loop state
├── genesis.md           <- Genesis contract
├── SKILL.md             <- Project conventions
├── loop_run_log.jsonl   <- Iteration log
└── README.md            <- This file
```

## Adapt this example

1. Replace `data.py` with your real issue data or point `crawler.py` at your repo
2. Modify `enricher.py` to extract domain-specific context
3. Update `evaluate.py` with your enrichment quality metrics
4. Edit `genesis.md` with your convergence criteria
