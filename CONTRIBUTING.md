# Contributing to Growth Workflow OS

PRs welcome from growth engineers and operators.

## Setup

```bash
git clone https://github.com/Das-rebel/growth-workflow-os.git
cd growth-workflow-os
pip install -r requirements.txt
cp config/.env.example config/.env
python3 run_pipeline.py  # verify
```

## Testing

```bash
python3 -m pytest tests/
```

## Adding New Signal Sources

1. Create collector in `signal_collectors/`
2. Add to `SIGNAL_SOURCES` config in `config/`
3. Document in the collector docstring

## Architecture Notes

- **signal_collectors/** — RSS, arXiv, manual, Reddit feeds
- **inference_engines/** — Groq/Mistral LLM inference + operator context
- **strategic_memory/** — SQLite: signals, theses, predictions
- **operating_memos/** — Weekly brief generation
- **decision_systems/** — AI/human routing rules
- **workflow_architecture/** — Workflow redesign patterns

## Commit Convention

Follow conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`

## Questions

Open a GitHub Discussion.