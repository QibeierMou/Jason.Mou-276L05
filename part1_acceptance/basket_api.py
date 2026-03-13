"""
Shopping Basket API — provided code.  DO NOT MODIFY.
Run with: python basket_api.py
API available at http://localhost:5001
"""
from flask import Flask, jsonify, request

app = Flask(__name__)

STOCK = {
    "BK001": {"name": "Clean Code", "price": 29.99, "stock": 5},
    "BK002": {"name": "The Pragmatic Programmer", "price": 39.99, "stock": 3},
    "BK003": {"name": "Domain-Driven Design", "price": 49.99, "stock": 0},  # out of stock
}
DISCOUNT_CODES = {
    "SAVE10": 0.10,
    "SAVE20": 0.20,
}

basket = {"items": {}, "discount": None}


@app.route("/basket", methods=["GET"])
def get_basket():
    items = basket["items"]
    subtotal = sum(STOCK[k]["price"] * v for k, v in items.items() if k in STOCK)
    discount_pct = DISCOUNT_CODES.get(basket["discount"], 0)
    total = round(subtotal * (1 - discount_pct), 2)
    return jsonify({
        "items": {k: {"qty": v, "name": STOCK[k]["name"]} for k, v in items.items()},
        "subtotal": subtotal,
        "discount_applied": basket["discount"],
        "total": total,
    })


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
    return jsonify({"message": "Added", "basket": basket["items"]}), 201


@app.route("/basket/item/<book_id>", methods=["DELETE"])
def remove_item(book_id):
    if book_id not in basket["items"]:
        return jsonify({"error": "Item not in basket"}), 404
    del basket["items"][book_id]
    return jsonify({"message": "Removed"}), 200


@app.route("/basket/discount", methods=["POST"])
def apply_discount():
    code = request.json.get("code", "")
    if code not in DISCOUNT_CODES:
        return jsonify({"error": "Invalid or expired discount code"}), 400
    basket["discount"] = code
    return jsonify({"message": f"Discount {code} applied", "rate": DISCOUNT_CODES[code]}), 200


@app.route("/basket/clear", methods=["DELETE"])
def clear_basket():
    basket["items"] = {}
    basket["discount"] = None
    return jsonify({"message": "Basket cleared"}), 200


if __name__ == "__main__":
    app.run(port=5001, debug=False)
