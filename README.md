# AgentForge

**Production-grade agentic automation with falsification-first validation.**

AgentForge is a self-contained framework for AI-assisted engineering workflows. It treats agent execution the way a research lab treats experiments: every run is validated, every change is detected, and every output is falsified before it ships.

---

## Why This Exists

Most agentic workflows optimize for speed. AgentForge optimizes for **rigor**.

If you use AI to write code, generate artifacts, or automate analysis, you already know the failure modes:
- Silent regressions from unvalidated changes
- Infinite loops on ambiguous tool calls
- Outputs that look correct but aren't

AgentForge answers with a simple structure: **validate → detect change → falsify → ship.**

---

## Core Capabilities

| Module | What It Does |
|---|---|
| **Iterative validation loop** | Single-agent run → validate → refine → retry with hard cap |
| **Parallel subagent refinement** | Multi-agent parallel execution → schema validation → score-based selection |
| **Change detection monitor** | Hash-based change detection: NEW / CHANGED / UNCHANGED states |
| **Silent no-op cron** | Scheduled jobs that fire only when inputs actually change |
| **Artifact manager** | Write/read/list artifacts with metadata and stable SHA-256 hashing |
| **Schema validators** | JSON, CSV, and text validation with required keys, type checks, regex, and size bounds |

---

## Verified Behaviors

These are not claims — they are observed outcomes from end-to-end verification:

1. **Validation pipeline** — CSV/JSON/text artifacts validated against schemas
2. **Change detection** — NEW → fire, CHANGED → fire, UNCHANGED → silent
3. **Silent no-op** — second identical monitor run produces empty stdout, zero agent execution
4. **Parallel subagent pattern** — N tasks dispatched in one call, validated, best result selected
5. **One retry only** — hard cap prevents infinite loops

---

## When to Use AgentForge

- You run AI-assisted coding or research workflows and need **artifact-level rigor**
- You want **change detection** so cron jobs only fire when inputs actually change
- You need **parallel subagent execution** with schema-enforced outputs
- You want **silent no-op** scheduling to avoid wasting tokens on unchanged runs
- You believe agent outputs should be **falsified, not just generated**

---

## When Not to Use It

- You want fast prototyping without validation overhead
- Your workflow is entirely manual or doesn't produce discrete artifacts
- You need real-time agentic interaction rather than batch artifact pipelines

---

## Architecture

```
agentforge/
├── README.md
├── SYSTEM_VERIFIED.md             # End-to-end verification report
├── final_analysis_report.md       # Sample verified artifact
├── result_method_{a,b,c}.csv      # Sample verified artifacts
└── src/
    ├── validate_artifact.py       # JSON/CSV/text schema validator
    ├── artifact_hash.py           # Stable SHA-256 hashing
    ├── change_detector.py         # Hash store with NEW/UNCHANGED/CHANGED
    ├── artifact_manager.py        # Write/read/list artifacts with metadata
    └── monitor_demo.py            # Working cron monitor with silent no-op
```

---

## Efficiency Optimizations

| Optimization | Effect |
|---|---|
| Batch dispatch | All N subtasks sent in one `delegate_task` call |
| Leaf-only roles | No wasted orchestration overhead |
| Schema-enforced outputs | Catches failures immediately |
| One retry only | Hard cap prevents infinite loops |
| Score-based selection | Automatically picks best result |
| Silent no-op cron | Zero tokens spent on unchanged runs |
| Tight contexts | Less context per subtask = faster execution |

---

## Requirements

- Python 3.10+
- Git
- Any agent runtime that supports `delegate_task` with `output_schema`

No external API keys. No cloud dependencies. Runs locally.

---

## Verification

All behaviors above were verified in a live end-to-end run producing:
- `final_analysis_report.md`
- `result_method_{a,b,c}.csv`
- `SYSTEM_VERIFIED.md`

Run `python src/monitor_demo.py` to see silent no-op in action.

---

## License

MIT
