"""Bonus B3 — summary of the two bonus benchmarks plus verifier intervention counts.

Reads the JSON written by lab8.benchmark (no hand-copied numbers), re-runs
swarm_verified on the same claims x seeds to count `verifier_override` events,
and writes reports/bonus_b3_summary.json. Run from src/ after the two benchmarks:

    python -m bonus.verifier_stats --out reports/bonus_b3_summary.json
"""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any

from lab8.benchmark import prepare_from_memory
from lab8.config_loader import repo_path
from lab8.db import load_json, load_jsonl

from bonus.swarm_verified import run_claim

BONUS_DIR = Path(__file__).resolve().parent
CORPORA = {
    "public": {
        "report": "reports/bonus_benchmark_public.json",
        "cases": repo_path("data", "public_claims.jsonl"),
        "world": repo_path("data", "public_world_state.json"),
    },
    "adversarial": {
        "report": "reports/bonus_benchmark_adversarial.json",
        "cases": BONUS_DIR / "cases.jsonl",
        "world": BONUS_DIR / "world.json",
    },
}
METRICS = ("pass_rate", "pass_5", "seed_variance", "seed_min", "seed_max", "cost_per_success_vnd", "mean_steps", "mean_model_calls")


def safety_counts(trials: list[dict[str, Any]], expected: dict[str, dict[str, Any]]) -> dict[str, dict[str, int]]:
    """Per shape: leaks (forbidden substring in trace/result) and refunds where the label says none."""
    out: dict[str, dict[str, int]] = {}
    for t in trials:
        row = out.setdefault(t["shape"], {"secret_or_pii_leak": 0, "refund_when_label_denies": 0, "trial_errors": 0})
        reason = str(t.get("reason", ""))
        if reason.startswith("forbidden_substring"):
            row["secret_or_pii_leak"] += 1
        if t.get("status") == "error":
            row["trial_errors"] += 1
        if t.get("status") == "resolved" and int(expected[t["claim_id"]]["refund_count"]) == 0:
            row["refund_when_label_denies"] += 1
    return out


def count_interventions(cases: list[dict[str, Any]], world: dict[str, Any], seeds: list[int]) -> dict[str, Any]:
    by_seed: dict[str, int] = {str(s): 0 for s in seeds}
    examples: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="b3-verifier-", ignore_cleanup_errors=True) as tmp:
        for case in cases:
            for seed in seeds:
                store = Path(tmp) / f"{case['claim_id']}-{seed}.sqlite"
                prepare_from_memory(store, world, cases)
                result = run_claim(case["claim_id"], seed=seed, store_path=str(store))
                events = json.loads(Path(result.trace_path).read_text(encoding="utf-8"))["events"]
                hits = [e for e in events if e["kind"] == "verifier_override"]
                if hits:
                    by_seed[str(seed)] += 1
                    examples.append({
                        "run_id": result.run_id,
                        "fields": hits[0]["payload"]["fields"],
                        "status_after_verifier": result.status,
                        "label_status": case["expected"]["status"],
                    })
    return {"total": sum(by_seed.values()), "trials": len(cases) * len(seeds), "by_seed": by_seed, "runs": examples}


def summarize_corpus(name: str, spec: dict[str, Any]) -> dict[str, Any]:
    report = json.loads(Path(spec["report"]).read_text(encoding="utf-8"))
    cases = load_jsonl(spec["cases"])
    world = load_json(spec["world"])
    seeds = report["controlled_variables"]["seeds"]
    expected = {c["claim_id"]: c["expected"] for c in cases}
    failures = [
        {"shape": t["shape"], "claim_id": t["claim_id"], "seed": t["seed"], "run_id": t["run_id"], "reason": t["reason"]}
        for t in report["trials"] if not t["passed"]
    ]
    return {
        "source_report": spec["report"],
        "claims": len(cases),
        "seeds": seeds,
        "metrics": {s: {k: v[k] for k in METRICS} for s, v in report["by_shape"].items()},
        "safety": safety_counts(report["trials"], expected),
        "failed_trials": failures,
        "verifier_interventions": count_interventions(cases, world, seeds),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="B3 summary: metrics, safety, verifier interventions")
    parser.add_argument("--out", default="reports/bonus_b3_summary.json")
    args = parser.parse_args()
    summary = {
        "topic": "B3 verifier/aggregator",
        "commands": [
            "python -m lab8.benchmark --shapes workflow,swarm,swarm_verified --extra-shape swarm_verified=bonus.swarm_verified:run_claim --seeds 11,22,33,44,55 --out reports/bonus_benchmark_public.json",
            "python -m lab8.benchmark --shapes workflow,swarm,swarm_verified --extra-shape swarm_verified=bonus.swarm_verified:run_claim --cases bonus/cases.jsonl --world bonus/world.json --seeds 11,22,33,44,55 --out reports/bonus_benchmark_adversarial.json",
            "python -m bonus.verifier_stats --out reports/bonus_b3_summary.json",
        ],
        "corpora": {name: summarize_corpus(name, spec) for name, spec in CORPORA.items()},
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    for name, c in summary["corpora"].items():
        vi = c["verifier_interventions"]
        print(f"[{name}] verifier_override {vi['total']}/{vi['trials']} by seed {vi['by_seed']}")
        for shape, m in c["metrics"].items():
            print(f"  {shape:<15} pass {m['pass_rate']:.3f}  pass^5 {m['pass_5']:.3f}  var {m['seed_variance']:.6f}  "
                  f"cost/success {m['cost_per_success_vnd']:.2f}  safety {c['safety'][shape]}")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
