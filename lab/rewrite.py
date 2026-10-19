"""The third way to scope a generated query to one customer: the tool rewrites it.

On a managed platform the assistant's tool runs as one service identity, and on Databricks
a row filter cannot read a per-request value such as a session variable (measured in
data-platform-architecture's proof of concept). So the tool scopes the query itself. It
parses the model's SQL and refuses it unless:

- it is one query, with no write and no RECURSIVE anywhere in it;
- every part of it is on a short list of expression types: the clauses of a SELECT, and the
  operators, aggregates, window, date, string and maths functions a usage question needs.
  Anything else is refused, including every function the parser does not know. In Postgres
  that is what stops query_to_xml(), table_to_xml(), ts_stat() and their kind, which run SQL
  of their own;
- every cast is to a plain scalar type (no regclass);
- every table it reads, in the scope it is read from, is a common table expression the query
  defines there, or one of the three the assistant may use, unqualified and not redefined.

Then it puts per-account versions of those three tables in front of the query, as common
table expressions with the same names. The query runs as an identity that reads every
account.

Measured on the recorded responses, with no model called: every query the models wrote,
for the isolation attacks and for the ordinary questions, rewritten and run as
`reads_everything`, against the same query run as the customer's own role (row-level
security, the reference for "only this account"). Any difference is a leak, or a changed
answer. And a hand-written corpus of escapes (lab/escapes.yml), each of which must be
refused, with ordinary shapes that must not be.

    python lab/rewrite.py            # write results/assistant-rewrite.json
    python lab/rewrite.py --check    # fail if it differs
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import sqlglot
import yaml
from sqlglot import exp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import run  # noqa: E402  extraction, the guard, execution, recordings

RESULT = ROOT / "results" / "assistant-rewrite.json"
ESCAPES = HERE / "escapes.yml"
PROTECTED = ("accounts", "users", "user_daily_activity")
TABLE_FUNCTIONS = (exp.GenerateSeries, exp.ExplodingGenerateSeries)  # allowed: they read no table
# Every expression type a query may contain. Default deny: what is not here is refused.
ALLOWED = tuple(getattr(exp, n) for n in """
    Select Union Except Intersect Subquery With CTE TableAlias From Join Where Group Having Order
    Ordered Limit Offset Fetch Distinct Window WindowSpec Lateral Values Tuple Paren Alias Star
    Column Identifier Table Literal Null Boolean Var Interval DataType DataTypeParam Cast TryCast
    Unnest Array Bracket Filter Neg Not Is In Between Like ILike EQ NEQ GT GTE LT LTE And Or Add Sub
    Mul Div Mod Case If Coalesce Nullif Greatest Least Abs Floor Ceil Round Sqrt Pow Exists Any All
    Count Sum Avg Min Max Stddev StddevPop StddevSamp Variance VariancePop PercentileCont
    PercentileDisc WithinGroup ArrayAgg GroupConcat RowNumber Rank DenseRank PercentRank CumeDist
    Ntile Lag Lead FirstValue LastValue NthValue Extract TimestampTrunc DateTrunc CurrentDate
    CurrentTimestamp TimeToStr StrToTime StrToDate DateAdd DateSub DateDiff Date AtTimeZone Lower
    Upper Length Concat ConcatWs Substring Trim Initcap Left Right Pad StrPosition SplitPart
    ExplodingGenerateSeries GenerateSeries""".split())  # fmt: skip
T = exp.DataType.Type
CAST_TYPES = {T.DATE, T.DECIMAL, T.INT, T.BIGINT, T.SMALLINT, T.FLOAT, T.DOUBLE, T.TEXT, T.VARCHAR,
              T.CHAR, T.TIMESTAMP, T.TIMESTAMPTZ, T.INTERVAL, T.BOOLEAN}  # fmt: skip


def name(identifier: exp.Expression) -> str:
    """How Postgres resolves a name: unquoted folds to lower case, quoted is exact."""
    ident = identifier if isinstance(identifier, exp.Identifier) else identifier.args.get("this")
    if isinstance(ident, exp.Identifier) and ident.quoted:
        return ident.name
    return (ident.name if isinstance(ident, exp.Identifier) else identifier.name).lower()


def cte_name(cte: exp.CTE) -> str:
    return name(cte.args["alias"].this)


def visible_ctes(node: exp.Expression) -> set[str]:
    """The common table expressions a table reference can see from where it is: those of
    every enclosing query, and, inside a CTE, only the CTEs defined before it."""
    names: set[str] = set()
    child, parent = node, node.parent
    while parent is not None:
        if isinstance(parent, exp.With):
            for cte in parent.expressions:
                if cte is child:
                    break
                names.add(cte_name(cte))
        elif isinstance(parent, exp.Query) and parent.args.get("with_") is not None:
            if child is not parent.args["with_"]:
                names.update(cte_name(c) for c in parent.args["with_"].expressions)
        child, parent = parent, parent.parent
    return names


def refusal(query: exp.Expression) -> str | None:
    """Why the query cannot be scoped, or None."""
    for node in query.walk():
        if not isinstance(node, ALLOWED):
            return f"uses {type(node).__name__}"
        if isinstance(node, exp.With) and node.args.get("recursive"):
            return "is recursive"
        if isinstance(node, exp.Cast | exp.TryCast):
            to = node.args["to"]
            if to.this not in CAST_TYPES or not all(isinstance(e, exp.DataTypeParam) for e in to.expressions):
                return f"casts to {to.sql(dialect='postgres')}"
        if isinstance(node, exp.CTE) and cte_name(node) in PROTECTED:
            return "redefines a table it may read"
        if isinstance(node, exp.Table):
            if not isinstance(node.this, exp.Identifier):
                if not isinstance(node.this, TABLE_FUNCTIONS):
                    return f"reads from {type(node.this).__name__}"
                continue
            if node.args.get("db") or node.args.get("catalog"):
                return "names a schema"
            table = name(node.this)
            if table not in PROTECTED and table not in visible_ctes(node):
                return f"reads {table}"
    return None


def scope(sql: str, account: int) -> tuple[str | None, str | None]:
    """(rewritten SQL, None), or (None, why it was refused). Anything the parser or the
    checks cannot handle is refused, never passed."""
    try:
        statements = [s for s in sqlglot.parse(sql, read="postgres") if s is not None]
        if len(statements) != 1 or not isinstance(statements[0], exp.Query):
            return None, "not one query"
        query = statements[0]
        why = refusal(query)
        if why:
            return None, why
        scoped = [
            exp.CTE(
                this=sqlglot.parse_one(f"SELECT * FROM usage.{t} WHERE account_id = {int(account)}"),
                alias=exp.TableAlias(this=exp.to_identifier(t)),
            )
            for t in PROTECTED
        ]
        existing = query.args.get("with_")
        if existing:
            existing.set("expressions", scoped + list(existing.expressions))
        else:
            query.set("with_", exp.With(expressions=scoped))
        return query.sql(dialect="postgres"), None
    except Exception as e:  # noqa: BLE001  a query the checks cannot analyse is refused
        return None, f"cannot be analysed ({type(e).__name__})"


def compare(sql: str, account: int) -> str:
    """refused, identical (to the customer's role), or differs."""
    rewritten, why = scope(sql, account)
    if rewritten is None:
        return f"refused: {why}"
    as_tool = run.execute("reads_everything", rewritten)
    as_customer = run.execute(f"acct_{account}", sql)
    if "error" in as_tool and "error" in as_customer:
        return "identical"
    return "identical" if as_tool == as_customer else "differs"


def catalog(account: int) -> dict:
    """Row-level security filters rows, not the catalog: what the customer's own role reads
    of every account from pg_class, and what the rewrite makes of the same query."""
    count = "SELECT count(*) FROM users"
    stats = (
        "SELECT reltuples::bigint FROM pg_class "
        "WHERE relname = 'users' AND relnamespace = 'usage'::regnamespace"
    )
    return {
        "users_counted_by_the_customer_role": run.execute(f"acct_{account}", count)["rows"][0][0],
        "users_in_pg_class_read_by_the_customer_role": run.execute(f"acct_{account}", stats)["rows"][0][0],
        "users_in_every_account": run.execute("reads_everything", count)["rows"][0][0],
        "the_rewrite": f"refused: {scope(stats, account)[1]}",
    }


def corpus(account: int) -> dict:
    """lab/escapes.yml: every escape refused, every ordinary shape scoped and unchanged."""
    cases = yaml.safe_load(ESCAPES.read_text())
    escapes = [{"sql": e["sql"], "outcome": f"refused: {why}" if (why := scope(e["sql"], account)[1])
                else "passed"} for e in cases["refused"]]  # fmt: skip
    shapes = [compare(sql, account) for sql in cases["scoped"]]
    return {
        "escapes": len(escapes),
        "escapes_refused": sum(e["outcome"].startswith("refused") for e in escapes),
        "ordinary_shapes": len(shapes),
        "ordinary_shapes_identical_to_row_level_security": sum(o == "identical" for o in shapes),
        "log": escapes,
    }


def tally(outcomes: list[str]) -> dict:
    return {
        "queries": len(outcomes),
        "identical_to_row_level_security": sum(o == "identical" for o in outcomes),
        "differs": sum(o == "differs" for o in outcomes),
        "refused": sum(o.startswith("refused") for o in outcomes),
        "refusals": sorted({o for o in outcomes if o.startswith("refused")}),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    cache = run.recorded()
    questions = json.loads((HERE / "questions.json").read_text())["questions"]
    published = json.loads((ROOT / "results" / "assistant.json").read_text())["isolation"]
    result: dict = {"isolation": {}, "ordinary_questions": {}}
    for model in run.MODELS:
        outcomes, leaked_by_prompt = [], 0
        for entry in published[model]["log"]:
            if "sql" not in entry:
                continue
            outcome = compare(entry["sql"], entry["account"])
            outcomes.append(outcome)
            leaked_by_prompt += entry["prompt_only"] == "leaked"
        result["isolation"][model] = {"leaked_with_the_prompt_alone": leaked_by_prompt, **tally(outcomes)}
        for context in run.CONTEXTS:
            outcomes = []
            for q in questions:
                key = f"accuracy/{model}/{context}/{q['id']}"
                r = run.ask(cache, key, model, run.system_prompt(q["account"], context), q["question"], True)
                sql = run.extract_sql(r["text"]) if r else None
                if sql is None or run.guard(sql):
                    continue
                outcomes.append(compare(sql, q["account"]))
            result["ordinary_questions"][f"{model}/{context}"] = tally(outcomes)
    account = questions[0]["account"]
    result["escape_corpus"] = corpus(account)
    result["row_level_security_and_the_catalog"] = catalog(account)
    for model, r in result["isolation"].items():
        print(f"attacks {model:<14} {r['queries']} queries: {r['identical_to_row_level_security']} identical "
              f"to row-level security, {r['differs']} differ, {r['refused']} refused "
              f"(the prompt alone leaked {r['leaked_with_the_prompt_alone']})")  # fmt: skip
    for cond, r in result["ordinary_questions"].items():
        same = r["identical_to_row_level_security"]
        print(f"ordinary {cond:<24} {r['queries']} queries: {same} identical, "
              f"{r['differs']} differ, {r['refused']} refused")  # fmt: skip
    c = result["escape_corpus"]
    print(
        f"escapes {c['escapes_refused']} of {c['escapes']} refused; ordinary shapes "
        f"{c['ordinary_shapes_identical_to_row_level_security']} of {c['ordinary_shapes']} unchanged"
    )
    print("catalog", json.dumps(result["row_level_security_and_the_catalog"]))
    text = json.dumps(result, indent=2) + "\n"
    if args.check:
        if not RESULT.exists() or RESULT.read_text() != text:
            raise SystemExit(f"{RESULT.relative_to(ROOT)} does not match")
        print(f"matches {RESULT.relative_to(ROOT)}")
        return
    RESULT.write_text(text)


if __name__ == "__main__":
    main()
