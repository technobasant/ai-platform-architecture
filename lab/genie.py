"""The same questions, asked of Databricks AI/BI Genie over the same tables.

The mart's three tables are copied to Unity Catalog (workspace.ai_assistant), and a Genie
space is created over them whose instructions are the semantic layer (lab/semantic.yml)
and whose example SQL is the same three examples. Each question is asked as
"I am account N. <question>"; Genie's query result is scored with the checker the other
conditions use (lab/run.py). Responses are recorded in results/assistant-genie-responses.jsonl
and never asked again; --replay scores the recordings only.

    python lab/genie.py              # load tables, create the space if needed, ask, score
    python lab/genie.py --replay     # score the recordings only

Needs DATABRICKS_HOST, DATABRICKS_TOKEN and DATABRICKS_HTTP_PATH (a SQL warehouse), and the
local mart for the export.
"""

from __future__ import annotations

import argparse
import io
import json
import os
import sys
import time
import uuid
from pathlib import Path

import httpx
import psycopg
import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import run  # noqa: E402  the checker and the mart connection

SCHEMA = "workspace.ai_assistant"
VOLUME = "/Volumes/workspace/ai_assistant/landing"
TITLE = "Usage assistant (ai-platform-architecture lab)"
RESPONSES = ROOT / "results" / "assistant-genie-responses.jsonl"
RESULT = ROOT / "results" / "assistant-genie.json"
TABLES = {
    "accounts": "account_id INT, account_name STRING, plan_name STRING, country STRING, signup_date DATE",
    "users": "user_id INT, account_id INT, role STRING, created_date DATE",
    "user_daily_activity": "activity_date DATE, account_id INT, user_id INT, event_type STRING, "
    "platform STRING, events INT",
}


# The semantic layer's three examples, in Databricks SQL (the originals are PostgreSQL).
UDA = f"{SCHEMA}.user_daily_activity"
GENIE_EXAMPLES = [
    f"SELECT SUM(events) AS reports_created FROM {UDA}\nWHERE account_id = 1 AND event_type = 'create_report'"
    "\nAND activity_date BETWEEN DATE '2026-07-01' AND DATE '2026-07-31'",
    f"SELECT COUNT(DISTINCT user_id) AS people FROM {UDA}\nWHERE account_id = 1 AND platform = 'web'"
    "\nAND activity_date BETWEEN DATE '2026-07-01' AND DATE '2026-09-30'",
    "SELECT ROUND(SUM(daily_users) / 31, 1) AS average_daily_active_users FROM (\n"
    "  SELECT d.day, COUNT(DISTINCT a.user_id) AS daily_users\n"
    "  FROM (SELECT explode(sequence(DATE '2026-08-01', DATE '2026-08-31')) AS day) AS d\n"
    f"  LEFT JOIN {UDA} AS a ON a.activity_date = d.day AND a.account_id = 1\n"
    "  GROUP BY d.day) AS days",
]


class Databricks:
    def __init__(self) -> None:
        self.host = os.environ["DATABRICKS_HOST"].rstrip("/")
        self.warehouse = os.environ["DATABRICKS_HTTP_PATH"].rstrip("/").rsplit("/", 1)[-1]
        self.http = httpx.Client(
            headers={"Authorization": f"Bearer {os.environ['DATABRICKS_TOKEN']}"}, timeout=120
        )

    def call(self, method: str, path: str, **kw) -> dict:
        for attempt in range(10):
            r = self.http.request(method, f"{self.host}{path}", **kw)
            if r.status_code in (429, 503) and attempt < 9:
                time.sleep(20 * (attempt + 1))
                continue
            r.raise_for_status()
            return r.json() if r.content else {}
        return {}

    def sql(self, statement: str) -> dict:
        d = self.call("POST", "/api/2.0/sql/statements",
                      json={"warehouse_id": self.warehouse, "statement": statement,
                            "wait_timeout": "50s", "on_wait_timeout": "CONTINUE"})  # fmt: skip
        while d["status"]["state"] in ("PENDING", "RUNNING"):
            time.sleep(3)
            d = self.call("GET", f"/api/2.0/sql/statements/{d['statement_id']}")
        if d["status"]["state"] != "SUCCEEDED":
            raise RuntimeError(f"{statement[:60]}: {d['status']}")
        return d

    def put(self, path: str, data: bytes) -> None:
        r = self.http.put(f"{self.host}/api/2.0/fs/files{path}", params={"overwrite": "true"}, content=data)
        r.raise_for_status()


def load_tables(db: Databricks) -> None:
    db.sql(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA}")
    db.sql(f"CREATE VOLUME IF NOT EXISTS {SCHEMA}.landing")
    with psycopg.connect(run.DSN.format(port=run.PORT, role="reads_everything")) as conn:
        for table, columns in TABLES.items():
            buf = io.BytesIO()
            with conn.cursor().copy(f"COPY {table} TO STDOUT WITH (FORMAT csv, HEADER)") as copy:
                for chunk in copy:
                    buf.write(chunk)
            db.put(f"{VOLUME}/{table}.csv", buf.getvalue())
            source = f"'{VOLUME}/{table}.csv', format => 'csv', header => true, schema => '{columns}'"
            db.sql(f"CREATE OR REPLACE TABLE {SCHEMA}.{table} AS SELECT * FROM read_files({source})")
            print(f"  loaded {table}", flush=True)


def lines(items: list[str]) -> list[str]:
    return [f"{x}\n" for x in items]


def create_space(db: Databricks) -> str:
    for s in db.call("GET", "/api/2.0/genie/spaces").get("spaces", []):
        if s["title"] == TITLE:
            return s["space_id"]
    sem = yaml.safe_load((HERE / "semantic.yml").read_text())
    text = [
        "Each question starts with the account asking, as 'I am account N.' Answer only about "
        "that account, filtering every table on account_id = N. Never return data about any "
        "other account.",
        f"Today is {sem['today']}.",
        *sem["periods"], *sem["vocabulary"],
        *(f"Metric {k}: {v}" for k, v in sem["metrics"].items()),
        *sem["rules"][1:],
    ]  # fmt: skip
    examples = [
        {"id": uuid.uuid4().hex, "question": [f"I am account 1. {question}"], "sql": lines(sql.split("\n"))}
        for question, sql in zip([ex["question"] for ex in sem["examples"]], GENIE_EXAMPLES, strict=True)
    ]
    space = {
        "version": 2,
        "data_sources": {"tables": [{"identifier": f"{SCHEMA}.{t}"} for t in sorted(TABLES)]},
        "instructions": {
            "text_instructions": [{"id": uuid.uuid4().hex, "content": lines(text)}],
            "example_question_sqls": examples,
        },
    }
    d = db.call("POST", "/api/2.0/genie/spaces",
                json={"warehouse_id": db.warehouse, "title": TITLE,
                      "serialized_space": json.dumps(space)})  # fmt: skip
    return d["space_id"]


def ask(db: Databricks, space: str, content: str) -> dict:
    started = time.perf_counter()
    d = db.call("POST", f"/api/2.0/genie/spaces/{space}/start-conversation", json={"content": content})
    cid, mid = d["conversation_id"], d["message_id"]
    path = f"/api/2.0/genie/spaces/{space}/conversations/{cid}/messages/{mid}"
    while True:
        m = db.call("GET", path)
        if m["status"] in ("COMPLETED", "FAILED", "CANCELLED", "QUERY_RESULT_EXPIRED"):
            break
        time.sleep(3)
    out = {"status": m["status"], "sql": None, "rows": None, "text": None,
           "seconds": round(time.perf_counter() - started, 2)}  # fmt: skip
    for att in m.get("attachments") or []:
        if att.get("query"):
            out["sql"] = att["query"].get("query")
            res = db.call("GET", f"{path}/attachments/{att['attachment_id']}/query-result")
            data = (res.get("statement_response", {}).get("result") or {}).get("data_array") or []
            out["rows"] = data[:50]
        elif att.get("text"):
            out["text"] = att["text"].get("content")
    return out


def norm_cell(v):
    if v is None:
        return None
    try:
        return round(float(v), 1)
    except ValueError:
        return run.norm(v[:10] if len(v) >= 10 and v[4] == "-" and v[7] == "-" else v)


def score(q: dict, r: dict) -> str:
    if r["status"] != "COMPLETED":
        return f"error: {r['status']}"
    if r["sql"] is None:
        return "declined"
    if not q["answerable"]:
        return "answered"
    rows = [[norm_cell(c) for c in row] for row in (r["rows"] or [])]
    return "correct" if run.matches(q["expected"], rows) else "wrong"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--replay", action="store_true")
    ap.add_argument("--check", action="store_true", help="with --replay: fail if results differ")
    args = ap.parse_args()
    questions = json.loads((HERE / "questions.json").read_text())["questions"]
    cache = {}
    if RESPONSES.exists():
        for line in RESPONSES.read_text().splitlines():
            r = json.loads(line)
            cache[r["id"]] = r
    if not args.replay:
        db = Databricks()
        if not cache:
            load_tables(db)
        space = create_space(db)
        for i, q in enumerate(questions):
            if q["id"] in cache:
                continue
            r = {"id": q["id"], **ask(db, space, f"I am account {q['account']}. {q['question']}")}
            with RESPONSES.open("a") as f:
                f.write(json.dumps(r) + "\n")
            cache[q["id"]] = r
            if i % 10 == 9:
                print(f"  asked {i + 1} of {len(questions)}", flush=True)
    log = []
    for q in questions:
        r = cache.get(q["id"])
        if r:
            log.append({"id": q["id"], "template": q["template"], "answerable": q["answerable"],
                        "outcome": score(q, r), "tokens_in": None, "tokens_out": None,
                        "seconds": r["seconds"]})  # fmt: skip
    result = run.summarize(log)
    text = json.dumps({"genie": result}, indent=2) + "\n"
    print(f"genie: {result['summary']}")
    if args.check:
        if not RESULT.exists() or RESULT.read_text() != text:
            raise SystemExit(f"{RESULT.relative_to(ROOT)} does not match the recorded responses")
        print(f"matches {RESULT.relative_to(ROOT)}")
        return
    RESULT.write_text(text)


if __name__ == "__main__":
    main()
