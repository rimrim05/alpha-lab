"""One scorecard for every track. A signal cannot pick a friendlier rubric."""
import pandas as pd
from core.eval.metrics import sharpe, deflated_sharpe, max_drawdown, hit_rate


def scorecard(net: pd.Series, benchmarks: dict, n_trials: int, periods_per_year: int) -> dict:
    net = net.dropna()
    halves = [net.iloc[: len(net) // 2], net.iloc[len(net) // 2:]]
    return {
        "sharpe": sharpe(net, periods_per_year),
        "deflated_sharpe_prob": deflated_sharpe(net, n_trials, periods_per_year),
        "max_drawdown": max_drawdown(net),
        "hit_rate": hit_rate(net),
        "ann_return": float(net.mean() * periods_per_year),
        "n_obs": len(net),
        "n_trials_declared": n_trials,
        "subperiods": [{"start": str(h.index[0].date()), "end": str(h.index[-1].date()),
                        "sharpe": sharpe(h, periods_per_year)} for h in halves if len(h) > 1],
        "benchmarks": {k: sharpe(v.dropna(), periods_per_year) for k, v in benchmarks.items()},
    }


def to_markdown(result: dict, title: str) -> str:
    lines = [f"# Scorecard — {title}", "",
             f"- Net Sharpe (ann.): **{result['sharpe']:.2f}**",
             f"- Deflated Sharpe prob (n_trials={result['n_trials_declared']}): **{result['deflated_sharpe_prob']:.2%}**",
             f"- Ann. return: {result['ann_return']:.2%} | Max DD: {result['max_drawdown']:.2%} "
             f"| Hit rate: {result['hit_rate']:.2%} | Obs: {result['n_obs']}",
             "", "## Subperiods"]
    lines += [f"- {s['start']} → {s['end']}: Sharpe {s['sharpe']:.2f}" for s in result["subperiods"]]
    lines += ["", "## Benchmarks (Sharpe)"]
    lines += [f"- {k}: {v:.2f}" for k, v in result["benchmarks"].items()]
    return "\n".join(lines) + "\n"
