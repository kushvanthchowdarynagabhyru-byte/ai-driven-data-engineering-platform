# AI-Driven Data Engineering Platform (base)

A small end-to-end pipeline:

```
ingest -> profile -> AI cleaning plan -> clean -> quality check -> load (SQLite)
```

- **AI advisor** (`aidep/ai_advisor.py`): sends a column profile to Claude and gets back a JSON cleaning plan. Plans are validated against an allow-list of operations, so no model-generated code is executed. Without `ANTHROPIC_API_KEY` it falls back to rule-based suggestions.
- **Cleaner**: applies the plan with pandas.
- **Quality**: before/after completeness and duplicate metrics.
- **Loader**: writes to SQLite.

## Run

```bash
pip install -r requirements.txt
python main.py sample_data/customers.csv --no-ai      # rules only
export ANTHROPIC_API_KEY=sk-...                        # optional
python main.py sample_data/customers.csv               # Claude-planned
```

Outputs: `warehouse.db`, plus `output/<table>_clean.csv`, `_plan.json`, `_profile.json`.

## Next steps
Scheduling (Airflow/cron), schema drift detection, more sources (APIs, databases), a Streamlit dashboard, unit tests.
