import pytest
from core.data.registry import register, read_manifest


def test_register_appends_and_reads(tmp_path):
    m = tmp_path / "manifest.jsonl"
    e = register(m, name="prices_test", source="yfinance", filters={"tickers": 2},
                 path="data/raw/p.parquet", rows=10)
    assert e["name"] == "prices_test" and "pulled_at" in e
    entries = read_manifest(m)
    assert len(entries) == 1 and entries[0]["source"] == "yfinance"


def test_register_rejects_empty_name(tmp_path):
    with pytest.raises(ValueError):
        register(tmp_path / "m.jsonl", name="", source="x", filters={}, path="p", rows=0)
