"""Build the question set: customers' questions about their own usage, with the answer
each should get, computed by reference SQL on the mart.

24 templates, each asked for up to three accounts picked with a fixed seed, skipping an
account where the answer would be zero, missing or tied (one template, active_jul_not_sep,
qualifies only one account); and 10 questions the mart cannot answer, each asked for two
accounts, where the right reply is UNANSWERABLE.

    python lab/questions.py            # write lab/questions.json (the mart must be running)
    python lab/questions.py --check    # fail if lab/questions.json differs
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

import psycopg

HERE = Path(__file__).resolve().parent
OUT = HERE / "questions.json"
ADMIN = "host=127.0.0.1 port=55442 user=postgres dbname=postgres options='-c search_path=usage'"

SEP = "activity_date BETWEEN DATE '2026-09-01' AND DATE '2026-09-30'"
AUG = "activity_date BETWEEN DATE '2026-08-01' AND DATE '2026-08-31'"
JUL = "activity_date BETWEEN DATE '2026-07-01' AND DATE '2026-07-31'"
Q3 = "activity_date BETWEEN DATE '2026-07-01' AND DATE '2026-09-30'"
UDA = "user_daily_activity"

# (id, question, reference SQL). The answer is the first column of the first row. "Which"
# questions select the item and its metric, ordered; a tie between the first two is skipped.
TEMPLATES = [
    ("reports_created_sep", "How many reports did we create in September?",
     f"SELECT SUM(events) FROM {UDA} WHERE account_id = {{a}} AND event_type = 'create_report' AND {SEP}"),
    ("events_last_week", "How many events did we have last week?",
     f"SELECT SUM(events) FROM {UDA} WHERE account_id = {{a}} "
     "AND activity_date BETWEEN DATE '2026-09-21' AND DATE '2026-09-27'"),
    ("people_sep", "How many people used the product in September?",
     f"SELECT COUNT(DISTINCT user_id) FROM {UDA} WHERE account_id = {{a}} AND {SEP}"),
    ("people_mobile_sep", "How many people used the mobile apps in September?",
     f"SELECT COUNT(DISTINCT user_id) FROM {UDA} WHERE account_id = {{a}} "
     f"AND platform IN ('ios', 'android') AND {SEP}"),
    ("busiest_day_sep", "Which day in September had the most active users?",
     f"SELECT activity_date, COUNT(DISTINCT user_id) FROM {UDA} WHERE account_id = {{a}} AND {SEP} "
     "GROUP BY 1 ORDER BY 2 DESC"),
    ("top_feature_sep", "What was our most used feature last month?",
     f"SELECT event_type, SUM(events) FROM {UDA} WHERE account_id = {{a}} AND {SEP} "
     "GROUP BY 1 ORDER BY 2 DESC"),
    ("admin_dashboards_aug", "How many dashboards did our admins view in August?",
     f"SELECT SUM(d.events) FROM {UDA} AS d JOIN users AS u USING (user_id) "
     f"WHERE d.account_id = {{a}} AND u.role = 'admin' AND d.event_type = 'view_dashboard' AND d.{AUG}"),
    ("events_change_aug_sep",
     "By how much, in percent, did our total events change from August to September?",
     f"SELECT ROUND(100.0 * (s - g) / g, 1) FROM (SELECT "
     f"SUM(events) FILTER (WHERE {SEP}) AS s, SUM(events) FILTER (WHERE {AUG}) AS g "
     f"FROM {UDA} WHERE account_id = {{a}}) AS t"),
    ("avg_daily_active_sep", "What was our average number of daily active users in September?",
     "SELECT ROUND(SUM(n)::numeric / 30, 1) FROM (SELECT d::date, COUNT(DISTINCT x.user_id) AS n "
     "FROM generate_series(DATE '2026-09-01', DATE '2026-09-30', INTERVAL '1 day') AS d "
     f"LEFT JOIN {UDA} AS x ON x.activity_date = d::date AND x.account_id = {{a}} GROUP BY 1) AS t"),
    ("users_total", "How many users do we have?",
     "SELECT COUNT(*) FROM users WHERE account_id = {a}"),
    ("new_users_q3", "How many new users joined our account last quarter?",
     "SELECT COUNT(*) FROM users WHERE account_id = {a} "
     "AND created_date BETWEEN DATE '2026-07-01' AND DATE '2026-09-30'"),
    ("top_export_platform_sep", "On which platform did we export the most in September?",
     f"SELECT platform, SUM(events) FROM {UDA} WHERE account_id = {{a}} AND event_type = 'export_csv' "
     f"AND {SEP} GROUP BY 1 ORDER BY 2 DESC"),
    ("api_calls_jul", "How many API calls did we make in July?",
     f"SELECT SUM(events) FROM {UDA} WHERE account_id = {{a}} AND event_type = 'api_call' AND {JUL}"),
    ("active_jul_not_sep", "How many of our users were active in July but not in September?",
     f"SELECT COUNT(*) FROM (SELECT user_id FROM {UDA} WHERE account_id = {{a}} AND {JUL} "
     f"EXCEPT SELECT user_id FROM {UDA} WHERE account_id = {{a}} AND {SEP}) AS t"),
    ("invites_q3", "How many invites did we send last quarter?",
     f"SELECT SUM(events) FROM {UDA} WHERE account_id = {{a}} AND event_type = 'invite_user' AND {Q3}"),
    ("web_share_sep", "What share of our September events came from the web app, in percent?",
     f"SELECT ROUND(100.0 * SUM(events) FILTER (WHERE platform = 'web') / SUM(events), 1) "
     f"FROM {UDA} WHERE account_id = {{a}} AND {SEP}"),
    ("top_user_sep", "Which user was our most active in September, by number of events?",
     f"SELECT user_id, SUM(events) FROM {UDA} WHERE account_id = {{a}} AND {SEP} "
     "GROUP BY 1 ORDER BY 2 DESC"),
    ("shared_last_7_days", "How many reports did we share in the last 7 days?",
     f"SELECT SUM(events) FROM {UDA} WHERE account_id = {{a}} AND event_type = 'share_report' "
     "AND activity_date BETWEEN DATE '2026-09-24' AND DATE '2026-09-30'"),
    ("plan", "What plan are we on?",
     "SELECT plan_name FROM accounts WHERE account_id = {a}"),
    ("signup", "When did we sign up?",
     "SELECT signup_date FROM accounts WHERE account_id = {a}"),
    ("viewers_logged_in_sep", "How many viewers logged in during September?",
     f"SELECT COUNT(DISTINCT d.user_id) FROM {UDA} AS d JOIN users AS u USING (user_id) "
     f"WHERE d.account_id = {{a}} AND u.role = 'viewer' AND d.event_type = 'login' AND d.{SEP}"),
    ("busiest_week_q3", "Which week of the last quarter had the most events? Give the Monday it started on.",
     f"SELECT date_trunc('week', activity_date)::date, SUM(events) FROM {UDA} "
     f"WHERE account_id = {{a}} AND {Q3} GROUP BY 1 ORDER BY 2 DESC"),
    ("events_per_user_sep", "How many events per active user did we have in September?",
     f"SELECT ROUND(SUM(events)::numeric / COUNT(DISTINCT user_id), 1) FROM {UDA} "
     f"WHERE account_id = {{a}} AND {SEP}"),
    ("login_days_sep", "On how many days in September did at least one of our users log in?",
     f"SELECT COUNT(DISTINCT activity_date) FROM {UDA} WHERE account_id = {{a}} "
     f"AND event_type = 'login' AND {SEP}"),
]  # fmt: skip

UNANSWERABLE = [
    ("paid_last_month", "How much did we pay for our subscription last month?"),
    ("likely_to_cancel", "Which of our users is most likely to cancel?"),
    ("csv_contents", "What was in the CSV files we exported in September?"),
    ("top_user_email", "What is the email address of our most active user?"),
    ("session_length", "How long did our users spend in the product per session in September?"),
    ("support_tickets", "How many support tickets did we open last quarter?"),
    ("top_dashboards", "Which dashboards did we view the most in August?"),
    ("nps", "What is our net promoter score?"),
    ("page_load", "How fast did the product load for our users last week?"),
    ("reports_next_month", "How many reports will we create next month?"),
]


def answer(cur, sql: str) -> list | None:
    """The reference answer, or None when it is zero, missing or tied."""
    rows = cur.execute(sql).fetchall()
    if not rows or rows[0][0] is None or rows[0][0] == 0:
        return None
    if "ORDER BY 2 DESC" in sql and len(rows) > 1 and rows[0][1] == rows[1][1]:
        return None
    value = rows[0][0]
    return [value.isoformat() if hasattr(value, "isoformat") else str(value)]


def build() -> dict:
    rng = random.Random(7)
    with psycopg.connect(ADMIN, autocommit=True) as conn:
        cur = conn.cursor()
        accounts = [r[0] for r in cur.execute(
            "SELECT account_id FROM users GROUP BY account_id HAVING COUNT(*) >= 5 ORDER BY 1")]  # fmt: skip
        questions = []
        for tid, text, sql in TEMPLATES:
            pool = accounts[:]
            rng.shuffle(pool)
            picked = 0
            for a in pool:
                expected = answer(cur, sql.format(a=a))
                if expected is None:
                    continue
                questions.append({"id": f"{tid}/{a}", "template": tid, "account": a,
                                  "question": text, "answerable": True, "expected": expected,
                                  "reference_sql": sql.format(a=a)})  # fmt: skip
                picked += 1
                if picked == 3:
                    break
        for tid, text in UNANSWERABLE:
            for a in rng.sample(accounts, 2):
                questions.append({"id": f"{tid}/{a}", "template": tid, "account": a,
                                  "question": text, "answerable": False, "expected": None,
                                  "reference_sql": None})  # fmt: skip
    return {"accounts_eligible": len(accounts), "questions": questions}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    text = json.dumps(build(), indent=2) + "\n"
    if args.check:
        if not OUT.exists() or OUT.read_text() != text:
            sys.exit("lab/questions.json does not match the mart")
        print("matches lab/questions.json")
        return
    OUT.write_text(text)
    q = json.loads(text)["questions"]
    print(
        f"{len(q)} questions: {sum(x['answerable'] for x in q)} answerable, "
        f"{sum(not x['answerable'] for x in q)} not"
    )


if __name__ == "__main__":
    main()
