"""
Instrumented Shopping Basket API
Run: python basket_api_instrumented.py
Metrics: http://localhost:5001/metrics
"""
from flask import Flask, jsonify, request, Response
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import time

app = Flask(__name__)

# ── Prometheus metrics (your SLIs) ────────────────────────────────────────────
REQUEST_COUNT = Counter(
    "basket_requests_total",
    "Total HTTP requests to the basket API",
    ["method", "endpoint", "status"]
)
REQUEST_LATENCY = Histogram(
    "basket_request_duration_seconds",
    "HTTP request latency in seconds",
    ["endpoint"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0]
)
BASKET_ITEMS_GAUGE = Gauge(
    "basket_active_items",
    "Number of items currently in baskets"
)
DISCOUNT_APPLICATIONS = Counter(
    "basket_discount_applications_total",
    "Number of discount code applications",
    ["code", "result"]
)

# ── Middleware ─────────────────────────────────────────────────────────────────
@app.before_request
def start_timer():
    request._start_time = time.time()

@app.after_request
def record_metrics(response):
    duration = time.time() - request._start_time
    endpoint = request.path
    REQUEST_COUNT.labels(method=request.method, endpoint=endpoint, status=response.status_code).inc()
    REQUEST_LATENCY.labels(endpoint=endpoint).observe(duration)
    return response


# Same API code as Part 1, with metric recording added ...
STOCK = {
    "BK001": {"name": "Clean Code", "price": 29.99, "stock": 5},
    "BK002": {"name": "The Pragmatic Programmer", "price": 39.99, "stock": 3},
    "BK003": {"name": "Domain-Driven Design", "price": 49.99, "stock": 0},
}
DISCOUNT_CODES = {"SAVE10": 0.10, "SAVE20": 0.20}
basket = {"items": {}, "discount": None}


@app.route("/metrics")
def metrics():
    """Prometheus scrape endpoint"""
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


@app.route("/basket", methods=["GET"])
def get_basket():
    items = basket["items"]
    subtotal = sum(STOCK[k]["price"] * v for k, v in items.items() if k in STOCK)
    discount_pct = DISCOUNT_CODES.get(basket["discount"], 0)
    total = round(subtotal * (1 - discount_pct), 2)
    BASKET_ITEMS_GAUGE.set(len(items))
    return jsonify({"items": items, "subtotal": subtotal, "discount_applied": basket["discount"], "total": total})


@app.route("/basket/item", methods=["POST"])
def add_item():
    data = request.json
    book_id = data.get("book_id")
    qty = data.get("qty", 1)
    if book_id not in STOCK:
        return jsonify({"error": "Book not found"}), 404
    if STOCK[book_id]["stock"] < qty:
        return jsonify({"error": "Insufficient stock"}), 409
    basket["items"][book_id] = basket["items"].get(book_id, 0) + qty
    BASKET_ITEMS_GAUGE.set(len(basket["items"]))
    return jsonify({"message": "Added"}), 201


@app.route("/basket/item/<book_id>", methods=["DELETE"])
def remove_item(book_id):
    if book_id not in basket["items"]:
        return jsonify({"error": "Item not in basket"}), 404
    del basket["items"][book_id]
    BASKET_ITEMS_GAUGE.set(len(basket["items"]))
    return jsonify({"message": "Removed"}), 200


@app.route("/basket/discount", methods=["POST"])
def apply_discount():
    code = request.json.get("code", "")
    if code not in DISCOUNT_CODES:
        DISCOUNT_APPLICATIONS.labels(code=code, result="invalid").inc()
        return jsonify({"error": "Invalid or expired discount code"}), 400
    basket["discount"] = code
    DISCOUNT_APPLICATIONS.labels(code=code, result="success").inc()
    return jsonify({"message": f"Discount {code} applied"}), 200


@app.route("/basket/clear", methods=["DELETE"])
def clear_basket():
    basket["items"] = {}
    basket["discount"] = None
    BASKET_ITEMS_GAUGE.set(0)
    return jsonify({"message": "Basket cleared"}), 200


if __name__ == "__main__":
    app.run(port=5001, debug=False)
