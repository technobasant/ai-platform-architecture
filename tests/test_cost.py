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


def test_an_analyst_answer_is_three_calls(inputs) -> None:
    prices, workloads = inputs
    sonnet = prices["models"]["claude-sonnet-5"]
    expected = 3 * (4000 * 2.00 + 300 * 10.00) / 1e6
    assert answer_cost(sonnet, workloads["features"]["analyst_answer"]) == pytest.approx(expected)


def test_break_even_is_instance_price_over_price_per_request(inputs) -> None:
    prices, workloads = inputs
    r = run()
    per_request = answer_cost(prices["models"]["gpt-6-luna"], workloads["features"]["support_answer"])
    expected = prices["gpus"]["g6e-xlarge"]["usd_per_hour"] / per_request
    assert r["break_even"]["g6e-xlarge"]["requests_per_hour"]["gpt-6-luna"] == round(expected)


def test_triage_per_cluster_is_cheaper_on_every_model() -> None:
    for model, t in run()["triage_day1"].items():
        assert t["per_cluster"] < t["per_row"], model


def test_every_price_cites_its_source(inputs) -> None:
    prices, _ = inputs
    for group in ("models", "gpus"):
        for name, item in prices[group].items():
            assert item["source"].startswith("https://"), name
            assert "quote" in item, name
