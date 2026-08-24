---
title: Advanced SQL
description: CTEs, window functions, subqueries, indexing and query optimization
---

# Advanced SQL <span class="pm-badge pm-badge-proficient">Proficient</span>

<div class="pm-topic-header">
  <strong>🗄️ Databases · Level 4</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~1 week</span>
  </div>
</div>

---

## Common Table Expressions (CTEs)

```sql
-- Named subquery — readable, reusable
WITH monthly_revenue AS (
    SELECT
        DATE_TRUNC('month', order_date) AS month,
        SUM(amount) AS revenue
    FROM orders
    GROUP BY 1
),
monthly_growth AS (
    SELECT
        month,
        revenue,
        LAG(revenue) OVER (ORDER BY month) AS prev_month,
        (revenue - LAG(revenue) OVER (ORDER BY month)) / LAG(revenue) OVER (ORDER BY month) * 100 AS growth_pct
    FROM monthly_revenue
)
SELECT * FROM monthly_growth WHERE growth_pct > 10;
```

---

## Window functions

```sql
-- Ranking
SELECT
    name,
    department,
    salary,
    RANK() OVER (PARTITION BY department ORDER BY salary DESC) AS dept_rank,
    ROW_NUMBER() OVER (ORDER BY salary DESC) AS overall_rank,
    DENSE_RANK() OVER (ORDER BY salary DESC) AS dense_rank
FROM employees;

-- Running totals and moving averages
SELECT
    date,
    revenue,
    SUM(revenue) OVER (ORDER BY date) AS running_total,
    AVG(revenue) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS ma_7day
FROM daily_sales;

-- Lead/Lag (previous/next row)
SELECT
    date,
    price,
    LAG(price, 1) OVER (ORDER BY date) AS yesterday_price,
    price - LAG(price, 1) OVER (ORDER BY date) AS daily_change
FROM stock_prices;

-- Percentile
SELECT
    name,
    salary,
    PERCENT_RANK() OVER (ORDER BY salary) AS percentile
FROM employees;
```

---

## Subqueries vs JOINs

```sql
-- Correlated subquery (runs per row — can be slow)
SELECT name, salary
FROM employees e
WHERE salary > (SELECT AVG(salary) FROM employees WHERE department = e.department);

-- Same as JOIN (usually faster)
SELECT e.name, e.salary
FROM employees e
JOIN (SELECT department, AVG(salary) as avg_sal FROM employees GROUP BY department) d
    ON e.department = d.department
WHERE e.salary > d.avg_sal;

-- EXISTS (efficient for "has any match?" checks)
SELECT * FROM customers c
WHERE EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id AND o.amount > 1000);
```

---

## Indexing strategy

```sql
-- B-tree index (default, most common)
CREATE INDEX idx_users_email ON users(email);

-- Composite index (multi-column — order matters!)
CREATE INDEX idx_orders_user_date ON orders(user_id, order_date DESC);
-- Supports: WHERE user_id = ? AND order_date > ?
-- Does NOT efficiently support: WHERE order_date > ? (without user_id)

-- Partial index (only index rows matching condition)
CREATE INDEX idx_active_users ON users(email) WHERE active = true;

-- EXPLAIN to check if index is used
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'alice@example.com';
```

---

## Query optimization tips

| Problem | Solution |
|---|---|
| Full table scan | Add appropriate index |
| N+1 queries (ORM) | Use JOIN or eager loading |
| Slow COUNT(*) | Use approximate counts or materialized views |
| Large IN clauses | Use temp table + JOIN |
| LIKE '%text%' | Full-text search index |
| Sorting large results | Index on ORDER BY column |

---

## Practice Exercises

1. **Write a CTE** that finds the top 3 customers by revenue per month.
2. **Use window functions** to compute a 30-day moving average of daily sales.
3. **Optimize a slow query** — use EXPLAIN, identify the bottleneck, add an index.
4. **Write a recursive CTE** to traverse a hierarchical category tree.
5. **Compare** correlated subquery vs JOIN performance on 1M rows.
