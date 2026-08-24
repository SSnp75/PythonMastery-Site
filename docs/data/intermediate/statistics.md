---
title: Statistics for Python
description: scipy.stats, distributions, hypothesis testing, correlation and regression
---

# Statistics for Python <span class="pm-badge pm-badge-intermediate">Intermediate</span>

<div class="pm-topic-header">
  <strong>📊 Data & AI Track · Level 3</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~4 days</span>
    <span>📚 Prerequisite: <a href="numpy/">NumPy</a></span>
  </div>
</div>

---

## Descriptive statistics

```python
import numpy as np
from scipy import stats

data = np.array([23, 45, 12, 67, 34, 89, 56, 78, 43, 21, 55, 67, 34, 90, 12])

# Central tendency
print(f"Mean:   {np.mean(data):.2f}")      # 48.40
print(f"Median: {np.median(data):.2f}")    # 45.00
print(f"Mode:   {stats.mode(data, keepdims=True).mode[0]}")  # 12 or 34 or 67

# Spread
print(f"Std:    {np.std(data, ddof=1):.2f}")    # 25.88 (sample std)
print(f"Var:    {np.var(data, ddof=1):.2f}")    # 669.83
print(f"Range:  {np.ptp(data)}")                 # 78 (max - min)
print(f"IQR:    {stats.iqr(data):.2f}")         # 35.50

# Percentiles
print(f"25th:   {np.percentile(data, 25):.2f}")  # 23.00
print(f"75th:   {np.percentile(data, 75):.2f}")  # 67.00
print(f"90th:   {np.percentile(data, 90):.2f}")  # 84.80

# Shape
print(f"Skewness: {stats.skew(data):.4f}")       # ~0 for symmetric
print(f"Kurtosis: {stats.kurtosis(data):.4f}")   # ~0 for normal-like
```

---

## Probability distributions

```python
from scipy.stats import norm, t, chi2, binom, poisson, expon

# ─── Normal distribution ──────────────────────────
# PDF — probability density at a point
print(norm.pdf(0, loc=0, scale=1))      # 0.3989 (peak of standard normal)

# CDF — probability of X ≤ x
print(norm.cdf(1.96))                    # 0.975 (97.5% below 1.96σ)
print(norm.cdf(0))                       # 0.5   (50% below mean)

# Inverse CDF (quantile function)
print(norm.ppf(0.975))                   # 1.96
print(norm.ppf(0.95))                    # 1.645

# Random samples
samples = norm.rvs(loc=100, scale=15, size=1000, random_state=42)
print(f"Sample mean: {samples.mean():.2f}, std: {samples.std():.2f}")

# ─── t-distribution ──────────────────────────────
# Used when sample size is small and population std is unknown
t_critical = t.ppf(0.975, df=29)   # 95% CI, 30 samples
print(f"t-critical (df=29): {t_critical:.4f}")   # 2.045

# ─── Binomial ────────────────────────────────────
# P(X = k) for n trials with probability p
print(binom.pmf(k=7, n=10, p=0.5))    # P(7 heads in 10 flips)
print(binom.cdf(k=7, n=10, p=0.5))    # P(≤ 7 heads)

# ─── Poisson ─────────────────────────────────────
# Events per unit time (λ = average rate)
print(poisson.pmf(k=5, mu=3))          # P(5 events when average is 3)
```

---

## Hypothesis testing

### One-sample t-test

```python
# Question: Is the average height different from 170cm?
heights = np.array([172, 168, 175, 171, 169, 174, 167, 173, 170, 176,
                    171, 168, 172, 174, 169, 173, 175, 170, 168, 172])

t_stat, p_value = stats.ttest_1samp(heights, popmean=170)
print(f"t-statistic: {t_stat:.4f}")   # 2.456
print(f"p-value: {p_value:.4f}")       # 0.0237

alpha = 0.05
if p_value < alpha:
    print("Reject H0: Average height IS different from 170cm")
else:
    print("Fail to reject H0: No significant difference")
```

### Two-sample t-test

```python
# Question: Do two groups have different means?
group_a = np.array([85, 90, 78, 92, 88, 76, 95, 89, 91, 84])
group_b = np.array([75, 80, 72, 85, 78, 70, 82, 77, 79, 74])

t_stat, p_value = stats.ttest_ind(group_a, group_b)
print(f"t-statistic: {t_stat:.4f}")   # 3.826
print(f"p-value: {p_value:.6f}")       # 0.001229

# For paired samples (before/after):
t_stat, p_value = stats.ttest_rel(group_a, group_b)
```

### Chi-squared test (independence)

```python
# Question: Is there a relationship between gender and product preference?
observed = np.array([
    [45, 30, 25],    # Male:   Product A, B, C
    [35, 40, 25],    # Female: Product A, B, C
])

chi2_stat, p_value, dof, expected = stats.chi2_contingency(observed)
print(f"χ² statistic: {chi2_stat:.4f}")
print(f"p-value: {p_value:.4f}")
print(f"Degrees of freedom: {dof}")
print(f"Expected frequencies:\n{expected}")
```

### ANOVA (multiple groups)

```python
# Question: Do 3+ groups have different means?
group1 = [85, 90, 78, 92, 88]
group2 = [75, 80, 72, 85, 78]
group3 = [92, 95, 88, 97, 91]

f_stat, p_value = stats.f_oneway(group1, group2, group3)
print(f"F-statistic: {f_stat:.4f}")
print(f"p-value: {p_value:.6f}")
```

---

## Correlation

```python
import numpy as np
from scipy import stats

x = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
y = np.array([2.1, 3.8, 6.2, 7.9, 10.1, 12.3, 13.8, 16.1, 18.0, 19.9])

# Pearson (linear correlation)
r, p_value = stats.pearsonr(x, y)
print(f"Pearson r: {r:.4f}, p-value: {p_value:.6f}")
# r ≈ 0.9997 (nearly perfect linear relationship)

# Spearman (rank correlation — handles non-linear monotonic)
rho, p_value = stats.spearmanr(x, y)
print(f"Spearman ρ: {rho:.4f}")

# Correlation matrix (with pandas)
import pandas as pd
df = pd.DataFrame({"x": x, "y": y, "z": x**2})
print(df.corr())
#          x         y         z
# x  1.000000  0.999720  0.974679
# y  0.999720  1.000000  0.970818
# z  0.974679  0.970818  1.000000
```

---

## Linear regression

```python
from scipy.stats import linregress

x = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
y = np.array([2.5, 4.1, 5.8, 8.2, 9.5, 12.1, 13.7, 15.9, 18.2, 19.8])

result = linregress(x, y)
print(f"Slope:     {result.slope:.4f}")        # ~1.95
print(f"Intercept: {result.intercept:.4f}")    # ~0.57
print(f"R-squared: {result.rvalue**2:.4f}")    # ~0.998
print(f"p-value:   {result.pvalue:.2e}")       # very small
print(f"Std error: {result.stderr:.4f}")

# Predict
x_new = 12
y_pred = result.slope * x_new + result.intercept
print(f"Prediction for x={x_new}: {y_pred:.2f}")

# Plot
import matplotlib.pyplot as plt
plt.scatter(x, y, label="Data")
plt.plot(x, result.slope * x + result.intercept, "r-", label=f"Fit (R²={result.rvalue**2:.3f})")
plt.legend()
plt.xlabel("x")
plt.ylabel("y")
plt.title("Linear Regression")
plt.show()
```

---

## Confidence intervals

```python
# CI for the mean
data = np.array([23, 25, 28, 30, 26, 24, 27, 29, 31, 22])
n = len(data)
mean = np.mean(data)
se = stats.sem(data)   # standard error of the mean

# 95% confidence interval
ci = stats.t.interval(confidence=0.95, df=n-1, loc=mean, scale=se)
print(f"Mean: {mean:.2f}")
print(f"95% CI: ({ci[0]:.2f}, {ci[1]:.2f})")
# Interpretation: We're 95% confident the true mean is in this interval

# Bootstrap confidence interval (non-parametric)
def bootstrap_ci(data, n_bootstrap=10000, confidence=0.95):
    rng = np.random.default_rng(42)
    means = [rng.choice(data, size=len(data), replace=True).mean()
             for _ in range(n_bootstrap)]
    lower = np.percentile(means, (1 - confidence) / 2 * 100)
    upper = np.percentile(means, (1 + confidence) / 2 * 100)
    return lower, upper

ci_boot = bootstrap_ci(data)
print(f"Bootstrap 95% CI: ({ci_boot[0]:.2f}, {ci_boot[1]:.2f})")
```

---

## A/B Testing

```python
# Conversion rates: variant A vs variant B
visitors_a, conversions_a = 10000, 350    # 3.5%
visitors_b, conversions_b = 10000, 400    # 4.0%

# Two-proportion z-test
from statsmodels.stats.proportion import proportions_ztest

count = np.array([conversions_a, conversions_b])
nobs = np.array([visitors_a, visitors_b])

z_stat, p_value = proportions_ztest(count, nobs, alternative="two-sided")
print(f"z-statistic: {z_stat:.4f}")
print(f"p-value: {p_value:.4f}")

if p_value < 0.05:
    print("Statistically significant difference!")
    print(f"Variant B converts {(400/10000 - 350/10000)*100:.1f}% more")
```

---

## Practice Exercises

1. **Generate 1000 samples** from a normal distribution and verify the 68-95-99.7 rule.
2. **Perform a t-test** on two groups of exam scores and interpret the result.
3. **Compute correlation** between all pairs of features in a dataset and create a heatmap.
4. **Implement bootstrap** for estimating the confidence interval of the median.
5. **Design and analyze an A/B test** — compute sample size needed for 80% power.
6. **Fit a linear regression** and plot residuals to check assumptions.
