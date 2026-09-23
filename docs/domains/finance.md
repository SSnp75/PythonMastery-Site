---
title: "Python for Finance"
description: Time series, returns, risk and backtesting with Python
---

# Python for Finance <span class="pm-badge pm-badge-proficient">Domain</span>

<div class="pm-topic-header">
  <strong>🌍 Domain Applications</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~1 week</span>
    <span>📚 Prereqs: <a href="../data/intermediate/pandas.md">Pandas</a>, <a href="../data/intermediate/statistics.md">Statistics</a></span>
  </div>
</div>

---

## What you'll learn

- [x] Core financial math (compound interest, returns)
- [x] Working with price time series
- [x] Risk basics (volatility, drawdown)
- [x] The idea of backtesting a strategy
- [x] The library ecosystem

Python dominates quantitative finance — from research notebooks to trading systems. The core math is simple; the libraries (Pandas, NumPy) handle scale. The stdlib examples here are **run-verified**; the Pandas ones follow its documented API.

---

## Financial math (stdlib, tested)

The foundations need no libraries. Compound interest and simple returns:

```python
def compound(principal, rate, years, n=1):
    """Future value with interest compounded n times per year."""
    return principal * (1 + rate / n) ** (n * years)

print(round(compound(1000, 0.05, 10), 2))   # 10y at 5%, annual
```

Output:

```text
1628.89
```

Period-over-period returns from a price series:

```python
def simple_return(prices):
    return [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]

print([round(r, 4) for r in simple_return([100, 110, 99])])
```

Output:

```text
[0.1, -0.1]
```

The price went up 10% then down 10% — note that leaves you *below* where you started (0.9 × 1.1 = 0.99), a classic reminder that percentage gains and losses aren't symmetric.

---

## Time series with Pandas

Real finance work uses **Pandas** for time-indexed price data:

```python
import pandas as pd     # pip install pandas

# Load prices with a datetime index
prices = pd.read_csv("prices.csv", parse_dates=["date"], index_col="date")

returns = prices["close"].pct_change()          # daily returns
cumulative = (1 + returns).cumprod()            # growth of $1
rolling_vol = returns.rolling(window=20).std()  # 20-day volatility
sma_50 = prices["close"].rolling(50).mean()     # 50-day moving average
```

!!! note "Pandas snippet follows documented API"
    Pandas isn't installed here, so this isn't run-verified (the stdlib math above is). Pandas' `pct_change`, `rolling`, and `cumprod` are the everyday tools of financial analysis — see the [Pandas](../data/intermediate/pandas.md) topic.

---

## Risk basics

A few standard risk measures:

- **Volatility** — standard deviation of returns; how much they swing. Higher = riskier.
- **Maximum drawdown** — the largest peak-to-trough drop; the worst loss you'd have endured.
- **Sharpe ratio** — return per unit of risk (excess return ÷ volatility); the classic risk-adjusted measure.

```python
# Max drawdown from a cumulative-growth series (stdlib logic)
def max_drawdown(cumulative):
    peak = cumulative[0]
    worst = 0.0
    for v in cumulative:
        peak = max(peak, v)
        worst = min(worst, (v - peak) / peak)
    return worst

print(round(max_drawdown([1.0, 1.2, 0.9, 1.1]), 4))   # -0.25 (from 1.2 to 0.9)
```

The drawdown of -0.25 means the portfolio fell 25% from its peak before recovering — the kind of loss an investor actually feels.

---

## Backtesting

**Backtesting** simulates a trading strategy on historical data to estimate how it *would* have performed. The skeleton: for each day, decide a signal from past data only, apply it, and track the resulting returns.

!!! warning "Backtests lie easily"
    Backtesting is riddled with traps: **look-ahead bias** (using data you wouldn't have had yet), **survivorship bias** (testing only on companies that still exist), overfitting to the past, and ignoring transaction costs/slippage. A great backtest is not a great strategy. Treat results with heavy skepticism, and this page as *technical* guidance — not financial advice.

Libraries like `backtrader`, `vectorbt`, and `zipline` provide realistic backtesting engines that help avoid these traps.

---

## The ecosystem

| Need | Library |
|---|---|
| Data / time series | Pandas, NumPy |
| Market data | yfinance, pandas-datareader |
| Backtesting | backtrader, vectorbt, zipline |
| Stats / econometrics | statsmodels, scipy |
| Optimization / ML | scikit-learn, cvxpy |

---

## Practice exercises

1. Extend `simple_return` to compute **log returns** (`ln(p_t / p_{t-1})`) and compare to simple returns.
2. Write a function for the Sharpe ratio given a list of returns and a risk-free rate.
3. Implement a simple moving-average crossover *signal* in pure Python (buy when short MA > long MA).
4. Compute max drawdown for a real price series you load with Pandas.
5. List three ways a backtest can look great but mislead you, and how to guard against each.
