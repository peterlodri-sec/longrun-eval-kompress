# Loop Engineering

This project follows the [Loop Engineering paradigm](https://addyosmani.com/blog/loop-engineering/).

## The ecosystem

| Piece | What | Link |
|-------|------|------|
| Addy Osmani's essay | The canonical text — 5 building blocks + memory | [addyosmani.com](https://addyosmani.com/blog/loop-engineering/) |
| Cobus Greyling's reference impl | npm tools (loop-audit, loop-init, loop-cost) | [github.com/cobusgreyling](https://github.com/cobusgreyling/loop-engineering) |
| LangChain: The Art of Loop Engineering | 4 stacked loops (Agent → Verification → Event-Driven → Hill Climbing) | [langchain.com](https://www.langchain.com/blog/the-art-of-loop-engineering) |
| LoopKit | Python-native starter kit, Telegram bot, council | [github.com/peterlodri-sec](https://github.com/peterlodri-sec/loopkit) |

## The four-tier loop stack (LangChain)

| Tier | Loop | LoopKit primitive | Role in kompress |
|------|------|-------------------|------------------|
| L1 | Agent | `Loop.run()` | training/eval iteration |
| L2 | Verification | `evals/heretic.py` | adversarial grader |
| L3 | Event-driven | Telegram bot | triggers on checkpoint events |
| L4 | Hill-climbing | LLM Council + trace rewriting | decides SHIP/RETRAIN/PIVOT |

## The correctable loop invariant
If the evaluation metric doesn't improve in 3 iterations, stop and pivot. Applied to the self-labeling chain:
- v3→v4: large jump (0.942→0.967) — continue
- v4→v5: slight regression (0.967→0.961) — **stop**

## Key quotes
> "You shouldn't be prompting coding agents anymore. You should be designing loops that prompt your agents." -- Peter Steinberger

> "I don't prompt Claude anymore. I have loops running that prompt Claude." -- Boris Cherny (Anthropic)

## Runnable examples

Six complete, runnable examples in `template/examples/`:

| Example | Domain | Loop explores | Convergence |
|---------|--------|---------------|-------------|
| `prompt-compression` | NLP | Compression strategies for sentiment prompts | accuracy >= 0.85, compression <= 0.70 |
| `log-summarizer` | DevOps | Log summarization while retaining critical fields | retention >= 0.90, compression <= 0.60 |
| `url-slug-optimizer` | Web | Slug generation balancing readability vs brevity | readability >= 0.40, length <= 45 chars |
| `issue-enricher` | Project mgmt | Issue enrichment with cross-refs and keywords | precision >= 0.60, coverage >= 0.50 |
| `commit-optimizer` | Dev workflow | Conventional commit messages from git diffs | score >= 60/100, grammar >= 0.70 |
| `ralph-loop` | Philosophy | Ultra cavemanified loop. one file. just vibes. | vibes |

Each runs the full four-phase cycle: Plan -> Execute -> Evaluate -> Decide.
The ralph-loop is intentionally minimal -- one file, no separation of concerns.

See [Ralph-Loop](Ralph-Loop.md) for the deep dive on ralph.
