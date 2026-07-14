import pandas as pd
from tracks.llm_sentiment.prompt import build_prompt
from tracks.llm_sentiment.scorer import (
    ScoreCache, cache_misses, mask_entity, parse_response, score_headlines, scoring_input,
)
from tracks.llm_sentiment.signal import daily_signal
from tracks.llm_sentiment.sample import select_smoke
from tracks.llm_sentiment.signal import decision_session


def test_prompt_contains_paper_structure():
    p = build_prompt("Apple beats earnings", "Apple Inc")
    assert "YES" in p and "NO" in p and "UNKNOWN" in p and "Apple beats earnings" in p


def test_parse_response():
    assert parse_response('{"label":"YES","reason":"Good earnings beat."}') == 1
    assert parse_response('{"label":"NO","reason":"Lawsuit risk."}') == -1
    assert parse_response('{"label":"UNKNOWN","reason":"Unclear."}') == 0
    assert parse_response("garbled") is None
    assert parse_response('{"label":"YES","reason":"ok","extra":1}') is None


def test_mask_entity():
    m = mask_entity("Apple (AAPL) beats estimates", "Apple", "AAPL")
    assert "Apple" not in m and "AAPL" not in m and "the company" in m


class FakeMessages:
    calls = 0

    def create(self, **kw):
        self.calls += 1
        class R:
            id = "req-test"
            model = "claude-haiku-4-5-20251001"
            usage = type("U", (), {"input_tokens": 10, "output_tokens": 8})()
            content = [type("B", (), {"text": '{"label":"YES","reason":"ok"}'})()]
        return R()


class FakeClient:
    def __init__(self):
        self.messages = FakeMessages()


def test_score_headlines_and_daily_signal(tmp_path):
    items = [{"published_at": "2026-07-01T15:00:00Z", "date": "2026-07-01",
              "ticker": "AAA", "company": "Alpha Co",
              "headline": "Alpha wins contract"}]
    cache = ScoreCache(tmp_path / "scores.sqlite")
    client = FakeClient()
    df = score_headlines(client, items, cache=cache, execute=True, max_new_calls=1)
    assert df.iloc[0]["score"] == 1
    sig = daily_signal(df)
    assert sig.loc[pd.Timestamp("2026-07-01"), "AAA"] == 1.0
    # cached rerun performs no new request and needs no client/key
    again = score_headlines(None, items, cache=cache, max_new_calls=0)
    assert again.iloc[0]["score"] == 1 and client.messages.calls == 1


def test_budget_blocks_before_first_request(tmp_path):
    cache = ScoreCache(tmp_path / "scores.sqlite")
    client = FakeClient()
    items = [{"date": "2026-07-01", "ticker": "AAA", "company": "Alpha",
              "headline": "Alpha wins"}]
    import pytest
    with pytest.raises(RuntimeError, match="exceed"):
        score_headlines(client, items, cache=cache, execute=True, max_new_calls=0)
    assert client.messages.calls == 0


def test_cache_key_tracks_scoring_inputs():
    item = {"ticker": "AAA", "company": "Alpha", "headline": "Alpha wins"}
    key, _, _ = scoring_input(item)
    masked_key, _, _ = scoring_input(item, masked=True)
    assert key != masked_key


def test_duplicate_prompt_one_call(tmp_path):
    cache = ScoreCache(tmp_path / "scores.sqlite")
    client = FakeClient()
    item = {"date": "2026-07-01", "ticker": "AAA", "company": "Alpha",
            "headline": "Alpha wins"}
    assert cache_misses([item, item], cache) == 1
    df = score_headlines(client, [item, item], cache=cache, execute=True, max_new_calls=1)
    assert len(df) == 2 and client.messages.calls == 1


def test_decision_session_is_conservative():
    assert decision_session("2026-07-02T19:00:00Z") == "2026-07-02"  # 3pm ET
    assert decision_session("2026-07-02T21:00:00Z") == "2026-07-06"  # after close; Fri holiday
    assert decision_session("2026-07-04T15:00:00Z") == "2026-07-06"  # weekend


def test_smoke_selection_is_row_order_invariant():
    rows = []
    for day in range(1, 4):
        for i in range(10):
            rows.append({"published_at": f"2026-02-0{day}T15:00:00Z",
                         "date": f"2026-02-0{day}", "ticker": f"T{i:02d}",
                         "company": f"Co {i}", "headline": f"Headline {day}-{i}"})
    news = pd.DataFrame(rows)
    a = select_smoke(news, limit=20)
    b = select_smoke(news.sample(frac=1, random_state=7), limit=20)
    pd.testing.assert_frame_equal(a, b)
