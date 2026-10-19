"""What the usage assistant costs per answer and per month, from its measured token counts
and list prices.

Three outputs:

  per_answer   USD per answer on each priced model
  monthly      USD per month at the brief's question volumes
  query_engine USD per month for a SQL warehouse of the smallest size kept awake for the
               assistant's queries, at the hours assumed, against the brief's ceiling
  break_even   answers per hour at which a dedicated GPU instance costs the same as paying
               per token: arithmetic on prices only. Whether one instance can serve that
               rate, with a model good enough for the feature, is not measured here.

    python cost/model.py            # print, and write results/cost.json
    python cost/model.py --check    # fail if results/cost.json is out of date
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "results" / "cost.json"
MTOK = 1_000_000


def load() -> tuple[dict, dict]:
    here = Path(__file__).parent
    return (yaml.safe_load((here / "prices.yml").read_text()),
            yaml.safe_load((here / "workloads.yml").read_text()))  # fmt: skip


def call_cost(model: dict, input_tokens: float, output_tokens: float) -> float:
    return (input_tokens * model["input"] + output_tokens * model["output"]) / MTOK


def answer_cost(model: dict, feature: dict) -> float:
    per_call = call_cost(model, feature["input_tokens_per_call"], feature["output_tokens_per_call"])
    return per_call * feature["calls_per_answer"]


def run() -> dict:
    prices, workloads = load()
    models, features = prices["models"], workloads["features"]
    per_answer = {f: {m: round(answer_cost(models[m], features[f]), 6) for m in models} for f in features}
    monthly = {
        f: {
            m: {
                tier: round(answer_cost(models[m], spec) * n, 2)
                for tier, n in spec["answers_per_month"].items()
            }
            for m in models
        }  # fmt: skip
        for f, spec in features.items()
    }
    feature = features[workloads["break_even_feature"]]
    break_even = {
        gpu: {
            "usd_per_hour": g["usd_per_hour"],
            "requests_per_hour": {
                m: round(g["usd_per_hour"] / answer_cost(models[m], feature)) for m in models
            },
        }
        for gpu, g in prices["gpus"].items()
    }
    engine, hours = prices["query_engine"], workloads["query_engine"]
    per_hour = engine["smallest_warehouse_dbu_per_hour"]["value"] * engine["serverless_sql_per_dbu"]["value"]
    query_engine = {
        "usd_per_hour": round(per_hour, 2),
        "monthly_usd": {k: round(per_hour * h) for k, h in hours["hours_awake_per_month"].items()},
        "ceiling_usd_per_month": hours["ceiling_usd_per_month"],
    }
    return {"prices_retrieved": prices["retrieved"], "per_answer": per_answer, "monthly": monthly,
            "query_engine": query_engine,
            "break_even_feature": workloads["break_even_feature"], "break_even": break_even}  # fmt: skip


def report(r: dict) -> str:
    lines = [f"List prices retrieved {r['prices_retrieved']}."]
    for f, costs in r["per_answer"].items():
        lines += ["", f"{f}: USD per answer"]
        for m, usd in sorted(costs.items(), key=lambda kv: kv[1]):
            lines.append(f"  {m:<24} ${usd:.5f}")
    q = r["query_engine"]
    awake = ", ".join(f"{k} ${v:,}" for k, v in q["monthly_usd"].items())
    lines += ["", f"The smallest SQL warehouse kept awake for the queries (${q['usd_per_hour']}/h): "
              f"{awake} a month, against a ${q['ceiling_usd_per_month']:,} ceiling"]  # fmt: skip
    lines += ["", f"Self-hosting break-even, {r['break_even_feature']}: requests per hour"]
    for gpu, b in r["break_even"].items():
        cells = ", ".join(f"{m} {n:,}" for m, n in b["requests_per_hour"].items())
        lines.append(f"  {gpu} (${b['usd_per_hour']}/h): {cells}")
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    r = run()
    print(report(r))
    text = json.dumps(r, indent=2) + "\n"
    if args.check:
        if not RESULT.exists() or RESULT.read_text() != text:
            sys.exit("results/cost.json is out of date: run python cost/model.py")
        print("\nmatches results/cost.json")
        return
    RESULT.parent.mkdir(exist_ok=True)
    RESULT.write_text(text)


if __name__ == "__main__":
    main()
