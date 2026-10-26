"""Orchestrates ingest -> profile -> AI plan -> clean -> quality -> load."""
import json
from pathlib import Path

from .ai_advisor import suggest_plan
from .cleaner import apply_plan
from .ingest import ingest
from .loader import load_to_sqlite
from .profiler import profile
from .quality import compare, quality_report


def run_pipeline(input_path: str, db_path: str = "warehouse.db", table: str | None = None,
                 use_ai: bool = True, out_dir: str = "output") -> None:
    table = table or Path(input_path).stem
    Path(out_dir).mkdir(exist_ok=True)

    print(f"[1/5] Ingesting {input_path}")
    raw = ingest(input_path)

    print("[2/5] Profiling")
    prof = profile(raw)
    before = quality_report(raw)

    print("[3/5] Generating cleaning plan")
    plan, source = suggest_plan(prof, use_ai=use_ai)
    print(f"      plan source: {source}, {len(plan)} steps")
    for s in plan:
        print(f"      - {s['op']:<18} {str(s.get('column') or ''):<12} {s['reason']}")

    print("[4/5] Cleaning + quality checks")
    clean = apply_plan(raw, plan)
    after = quality_report(clean)
    print(compare(before, after))

    print(f"[5/5] Loading into {db_path}:{table}")
    n = load_to_sqlite(clean, db_path, table)
    print(f"      {n} rows loaded")

    clean.to_csv(Path(out_dir) / f"{table}_clean.csv", index=False)
    (Path(out_dir) / f"{table}_plan.json").write_text(json.dumps(plan, indent=2))
    (Path(out_dir) / f"{table}_profile.json").write_text(json.dumps(prof, indent=2))
