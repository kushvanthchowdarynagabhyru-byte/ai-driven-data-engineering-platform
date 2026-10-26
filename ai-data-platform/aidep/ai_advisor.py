"""AI advisor: produces a cleaning plan (list of operations) from a data profile.

Uses Claude when ANTHROPIC_API_KEY is set; otherwise falls back to simple rules.
The plan is validated against an allow-list, so the model never runs arbitrary code.
"""
import json
import os

ALLOWED_OPS = {
    "drop_duplicates",
    "strip_whitespace",
    "lowercase",
    "title_case",
    "fill_null_median",
    "fill_null_mode",
    "parse_date",
    "validate_email",
    "clip_range",
}

MODEL = "claude-sonnet-5-5"

PROMPT = """You are a data engineer. Given this dataset profile, return a JSON cleaning plan.
Respond with ONLY a JSON list of objects: {{"op": <op>, "column": <name or null>, "params": {{}}, "reason": <short text>}}.
Allowed ops: {ops}.
- drop_duplicates: column null
- clip_range: params {{"min": number, "max": number}}
Profile:
{profile}
"""


def _rule_based_plan(profile: dict) -> list[dict]:
    plan = []
    plan.append({"op": "drop_duplicates", "column": None, "params": {"ignore_id": True},
                 "reason": "Remove duplicate records (ignoring id columns)"})
    for col, info in profile["columns"].items():
        name = col.lower()
        is_text = info["dtype"] in ("object", "str", "string")
        if is_text:
            plan.append({"op": "strip_whitespace", "column": col, "params": {}, "reason": "Trim stray spaces"})
        if "email" in name:
            plan.append({"op": "lowercase", "column": col, "params": {}, "reason": "Normalise emails"})
            plan.append({"op": "validate_email", "column": col, "params": {}, "reason": "Null out invalid emails"})
        elif name in ("name", "country", "city"):
            plan.append({"op": "title_case", "column": col, "params": {}, "reason": "Consistent casing"})
        if "date" in name:
            plan.append({"op": "parse_date", "column": col, "params": {}, "reason": "Standardise dates to ISO"})
        if not is_text and info["null_count"] > 0:
            plan.append({"op": "fill_null_median", "column": col, "params": {}, "reason": "Impute missing numbers"})
        if name == "age":
            plan.append({"op": "clip_range", "column": col, "params": {"min": 0, "max": 120}, "reason": "Plausible ages"})
    return plan


def _claude_plan(profile: dict) -> list[dict]:
    import anthropic

    client = anthropic.Anthropic()
    msg = client.messages.create(
        model=MODEL,
        max_tokens=2000,
        messages=[{"role": "user", "content": PROMPT.format(ops=sorted(ALLOWED_OPS), profile=json.dumps(profile, indent=2))}],
    )
    text = msg.content[0].text.strip()
    if text.startswith("```"):
        text = text.strip("`").removeprefix("json").strip()
    return json.loads(text)


def _validate(plan: list[dict], profile: dict) -> list[dict]:
    clean = []
    for step in plan:
        if not isinstance(step, dict) or step.get("op") not in ALLOWED_OPS:
            continue
        col = step.get("column")
        if col is not None and col not in profile["columns"]:
            continue
        step.setdefault("params", {})
        step.setdefault("reason", "")
        clean.append(step)
    return clean


def suggest_plan(profile: dict, use_ai: bool = True) -> tuple[list[dict], str]:
    """Return (plan, source) where source is 'claude' or 'rules'."""
    if use_ai and os.getenv("ANTHROPIC_API_KEY"):
        try:
            return _validate(_claude_plan(profile), profile), "claude"
        except Exception as e:  # network/parse errors -> fall back
            print(f"[advisor] AI plan failed ({e}); using rules.")
    return _validate(_rule_based_plan(profile), profile), "rules"
