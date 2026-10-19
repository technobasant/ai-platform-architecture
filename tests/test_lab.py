"""The lab's scoring helpers: how a reply becomes a query, how a query is refused, and when
an answer counts as correct. No database or model needed."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lab"))

import pytest  # noqa: E402
import yaml  # noqa: E402

run = pytest.importorskip("run")


def test_a_fenced_query_is_extracted_and_a_decline_is_none() -> None:
    assert run.extract_sql("```sql\nSELECT 1;\n```") == "SELECT 1"
    assert run.extract_sql("WITH t AS (SELECT 1) SELECT * FROM t") == "WITH t AS (SELECT 1) SELECT * FROM t"
    assert run.extract_sql("UNANSWERABLE") is None


def test_more_than_one_statement_is_refused() -> None:
    assert run.guard("SELECT 1") is None
    assert run.guard("SELECT 1; SELECT set_config('x', '1', false)") == "more than one statement"


def test_numbers_match_to_one_decimal_and_strings_and_dates_exactly() -> None:
    assert run.matches(["12"], [[12]])
    assert run.matches(["1.3"], [[1.26]])
    assert not run.matches(["12"], [[1570]])
    assert run.matches(["web"], [["web", 22]])
    assert run.matches(["2026-09-15"], [["2026-09-15", 9]])
    assert not run.matches(["12"], [])


def test_only_the_first_row_counts() -> None:
    assert not run.matches(["web"], [["ios", 30], ["web", 22]])


rewrite = pytest.importorskip("rewrite")


CORPUS = yaml.safe_load((Path(__file__).resolve().parents[1] / "lab" / "escapes.yml").read_text())


@pytest.mark.parametrize("case", CORPUS["refused"], ids=lambda c: c["why"])
def test_the_rewrite_refuses_what_would_escape_the_scope(case: dict) -> None:
    rewritten, why = rewrite.scope(case["sql"], 7)
    assert rewritten is None and why


@pytest.mark.parametrize("sql", CORPUS["scoped"])
def test_the_rewrite_scopes_ordinary_shapes(sql: str) -> None:
    rewritten, why = rewrite.scope(sql, 7)
    assert why is None and "WHERE account_id = 7" in rewritten


def test_the_rewrite_scopes_every_table_the_query_reads() -> None:
    rewritten, why = rewrite.scope("SELECT COUNT(*) FROM users JOIN accounts USING (account_id)", 7)
    assert why is None
    for name in ("accounts", "users", "user_daily_activity"):
        assert f"{name} AS (SELECT * FROM usage.{name} WHERE account_id = 7)" in rewritten
