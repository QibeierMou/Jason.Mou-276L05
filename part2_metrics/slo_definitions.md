# SLO Definitions — Shopping Basket API
# Complete this file as part of the lab (Part 2, Task 2)

## SLI-001: Request Success Rate

**SLI (what we measure):**
```
SLI = (successful_requests / total_requests) × 100
```
Metric: `basket_requests_total{status=~"2.."} / basket_requests_total`

**SLO (our internal target):**
```
SLO: 99.5% of requests must return a 2xx status code, measured over a 30-day rolling window
```

**SLA (our external commitment):**
```
SLA: 99.0% availability per calendar month (below = service credits)
```

**Error budget:** `100% - 99.5% = 0.5%` = ~3.6 hours/month of allowed downtime

---

## SLI-002: Request Latency

**SLI (what we measure):**
```
SLI = p95 of basket_request_duration_seconds
```
Prometheus query: `histogram_quantile(0.95, rate(basket_request_duration_seconds_bucket[5m]))`

**SLO:** `p95 latency ≤ 0.5 seconds for all /basket endpoints, 30-day window`

**SLA:** `p95 latency ≤ 1.0 second`

**Error budget:** SLO leaves 0.5s headroom before the SLA is breached.

---

## TODO: Define SLI-003 yourself
Choose a metric from the instrumented API and write:
- SLI (formula and Prometheus metric)
SlI = (invalid discount attempts / total discount attempts) x 100
- SLO (target, window)
Less than 5% of discount attempts should be invalid, measured over 30 days.
- SLA (external commitment)
Less than 10% of discount attempts should be invalid per month.
- Error budget calculation
We allow up to 5% invalid attempts before we have a problem.