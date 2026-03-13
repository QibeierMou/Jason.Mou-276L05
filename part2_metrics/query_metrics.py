"""
query_metrics.py  –  Lab 05 Part B starter
===========================================
Query the Prometheus-format /metrics endpoint exposed by basket_api_instrumented.py
and check whether the service is meeting its SLO targets.

Run with:
    python query_metrics.py

Prerequisites:
    python basket_api_instrumented.py   (in a separate terminal)
"""

import requests

METRICS_URL = "http://localhost:5001/metrics"

# SLI-001 SLO target (from slo_definitions.md)
SUCCESS_RATE_SLO = 99.5   # percent


# ── Helper ────────────────────────────────────────────────────────────────────

def parse_counter(metrics_text: str, metric_name: str, labels: dict) -> float:
    """
    Extract a single counter value from Prometheus text-format output.

    Parameters
    ----------
    metrics_text : str
        The raw text returned by GET /metrics
    metric_name : str
        Base name of the metric, e.g. "basket_requests_total"
    labels : dict
        Label key/value pairs to match, e.g. {"status": "error"}
        Pass an empty dict {} to match a metric with no labels.

    Returns
    -------
    float
        The numeric value, or 0.0 if the metric/label combination is not found.

    Example
    -------
    >>> text = 'basket_requests_total{endpoint="/basket",status="success"} 42.0'
    >>> parse_counter(text, "basket_requests_total", {"status": "success"})
    42.0
    """
    for line in metrics_text.splitlines():
        if line.startswith("#") or not line.strip():
            continue
        if not line.startswith(metric_name):
            continue

        # Check all required labels are present with the right values
        all_match = all(f'{k}="{v}"' in line for k, v in labels.items())
        if all_match:
            # Value is the last whitespace-separated token
            return float(line.split()[-1])

    return 0.0


# ── TODO: implement this function ─────────────────────────────────────────────

def calculate_success_rate(metrics_text: str) -> float:
    """
    Calculate the overall request success rate as a percentage.

    Steps:
      1. Use parse_counter() to get the total number of requests
         (hint: basket_requests_total has a "status" label)
      2. Use parse_counter() to get the number of error requests
      3. If total is 0, return 100.0 (no requests = no failures)
      4. Calculate: success_rate = (total - errors) / total * 100
      5. Return the result rounded to 2 decimal places

    Available label values for basket_requests_total:
        status="success"
        status="error"

    Parameters
    ----------
    metrics_text : str
        Raw Prometheus text from GET /metrics

    Returns
    -------
    float
        Success rate as a percentage, e.g. 98.76
    """
    # TODO: replace this with your implementation
    raise NotImplementedError("Implement calculate_success_rate()")


# ── TODO: implement this function ─────────────────────────────────────────────

def check_slo(success_rate: float, slo_target: float) -> None:
    """
    Print a PASS or FAIL message comparing the measured rate to the SLO target.

    Output format:
        PASS  Success rate 99.80% meets SLO target of 99.5%
        FAIL  Success rate 97.30% is BELOW SLO target of 99.5%

    Parameters
    ----------
    success_rate : float
        The measured success rate (percentage)
    slo_target : float
        The SLO threshold (percentage)
    """
    # TODO: replace this with your implementation
    raise NotImplementedError("Implement check_slo()")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print(f"Querying metrics from {METRICS_URL} ...")
    try:
        response = requests.get(METRICS_URL, timeout=5)
        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect. Is basket_api_instrumented.py running?")
        return
    except requests.exceptions.RequestException as e:
        print(f"ERROR: {e}")
        return

    metrics_text = response.text

    print("\n── SLI-001: Request Success Rate ──────────────────────────────")
    rate = calculate_success_rate(metrics_text)
    check_slo(rate, SUCCESS_RATE_SLO)

    # ── Extension: add checks for SLI-002 and your own SLI-003 here ──────────


if __name__ == "__main__":
    main()
