import pandas as pd
from tracks.llm_sentiment.prompt import build_prompt
from tracks.llm_sentiment.scorer import parse_response, mask_entity, score_headlines
from tracks.llm_sentiment.signal import daily_signal


def test_prompt_contains_paper_structure():
    p = build_prompt("Apple beats earnings", "Apple Inc")
    assert "YES" in p and "NO" in p and "UNKNOWN" in p and "Apple beats earnings" in p


def test_parse_response():
    assert parse_response("YES\nGood earnings beat.") == 1
    assert parse_response("NO\nLawsuit risk.") == -1
    assert parse_response("UNKNOWN\nUnclear.") == 0
    assert parse_response("garbled") == 0


def test_mask_entity():
    m = mask_entity("Apple (AAPL) beats estimates", "Apple", "AAPL")
    assert "Apple" not in m and "AAPL" not in m and "the company" in m


class FakeMessages:
    def create(self, **kw):
        class R:
            content = [type("B", (), {"text": "YES\nok"})()]
        return R()


class FakeClient:
    messages = FakeMessages()


def test_score_headlines_and_daily_signal():
    items = [{"date": "2026-07-01", "ticker": "AAA", "company": "Alpha Co",
              "headline": "Alpha wins contract"}]
    df = score_headlines(FakeClient(), items)
    assert df.iloc[0]["score"] == 1
    sig = daily_signal(df)
    assert sig.loc[pd.Timestamp("2026-07-01"), "AAA"] == 1.0
