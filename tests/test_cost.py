"""The AI cost model's arithmetic, checked against numbers worked out by hand."""

from __future__ import annotations

import pytest

from cost.model import answer_cost, call_cost, load, run


@pytest.fixture(scope="module")
def inputs():
    return load()


def test_a_call_is_input_plus_output_tokens_at_their_prices(inputs) -> None:
    prices, _ = inputs
    haiku = prices["models"]["claude-haiku-4-5"]
    assert call_cost(haiku, 1_000_000, 0) == pytest.approx(1.00)
    assert call_cost(haiku, 0, 1_000_000) == pytest.approx(5.00)


def test_a_usage_answer_is_one_call_at_the_measured_tokens(inputs) -> None:
    prices, workloads = inputs
    oss = prices["models"]["databricks-gpt-oss-120b"]
    expected = (1094 * 0.167154 + 198 * 0.668538) / 1e6
    assert answer_cost(oss, workloads["features"]["usage_assistant"]) == pytest.approx(expected)


def test_break_even_is_instance_price_over_price_per_request(inputs) -> None:
    prices, workloads = inputs
    r = run()
    per_request = answer_cost(prices["models"]["gpt-6-luna"], workloads["features"]["usage_assistant"])
    expected = prices["gpus"]["g6e-xlarge"]["usd_per_hour"] / per_request
    assert r["break_even"]["g6e-xlarge"]["requests_per_hour"]["gpt-6-luna"] == round(expected)


def test_every_price_cites_its_source(inputs) -> None:
    prices, _ = inputs
    for group in ("models", "gpus"):
        for name, item in prices[group].items():
            assert item["source"].startswith("https://"), name
            assert "quote" in item, name


def test_a_warehouse_is_billed_for_the_hours_it_is_awake(inputs) -> None:
    r = run()["query_engine"]
    assert r["usd_per_hour"] == pytest.approx(4 * 0.91)
    assert r["monthly_usd"]["always"] == round(4 * 0.91 * 730)
