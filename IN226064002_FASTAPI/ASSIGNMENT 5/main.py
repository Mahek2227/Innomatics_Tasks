from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel, Field

app = FastAPI()

# ═══════════════════════════════
# MODELS
# ═══════════════════════════════

class OrderRequest(BaseModel):
    customer_name: str = Field(..., min_length=2)
    product_id: int
    quantity: int
    delivery_address: str = Field(..., min_length=10)

# ═══════════════════════════════
# DATA
# ═══════════════════════════════

products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True},
]

orders = []
order_counter = 1

# ═══════════════════════════════
# BASIC ENDPOINTS
# ═══════════════════════════════

@app.get("/")
def home():
    return {"message": "Welcome to Day 6 API"}

@app.get("/products")
def get_products():
    return {"products": products}

# ═══════════════════════════════
# Q1 — SEARCH PRODUCTS
# ═══════════════════════════════

@app.get("/products/search")
def search_products(keyword: str = Query(...)):
    result = [p for p in products if keyword.lower() in p["name"].lower()]

    if not result:
        return {"message": f"No products found for: {keyword}"}

    return {
        "keyword": keyword,
        "total_found": len(result),
        "products": result
    }

# ═══════════════════════════════
# Q2 — SORT PRODUCTS
# ═══════════════════════════════

@app.get("/products/sort")
def sort_products(
    sort_by: str = Query("price"),
    order: str = Query("asc")
):
    if sort_by not in ["price", "name"]:
        raise HTTPException(status_code=400, detail="sort_by must be 'price' or 'name'")

    reverse = True if order == "desc" else False

    sorted_products = sorted(products, key=lambda p: p[sort_by], reverse=reverse)

    return {
        "sort_by": sort_by,
        "order": order,
        "products": sorted_products
    }

# ═══════════════════════════════
# Q3 — PAGINATION
# ═══════════════════════════════

@app.get("/products/page")
def paginate_products(
    page: int = Query(1, ge=1),
    limit: int = Query(2, ge=1)
):
    start = (page - 1) * limit
    end = start + limit

    total = len(products)
    total_pages = -(-total // limit)

    return {
        "page": page,
        "limit": limit,
        "total_products": total,
        "total_pages": total_pages,
        "products": products[start:end]
    }

# ═══════════════════════════════
# Q4 — SEARCH ORDERS
# ═══════════════════════════════

@app.get("/orders/search")
def search_orders(customer_name: str = Query(...)):
    result = [
        o for o in orders
        if customer_name.lower() in o["customer_name"].lower()
    ]

    if not result:
        return {"message": f"No orders found for: {customer_name}"}

    return {
        "customer_name": customer_name,
        "total_found": len(result),
        "orders": result
    }

# ═══════════════════════════════
# Q5 — SORT BY CATEGORY + PRICE
# ═══════════════════════════════

@app.get("/products/sort-by-category")
def sort_by_category():
    result = sorted(products, key=lambda p: (p["category"], p["price"]))

    return {
        "products": result,
        "total": len(result)
    }

# ═══════════════════════════════
# Q6 — BROWSE (SEARCH + SORT + PAGINATION)
# ═══════════════════════════════

@app.get("/products/browse")
def browse_products(
    keyword: str = Query(None),
    sort_by: str = Query("price"),
    order: str = Query("asc"),
    page: int = Query(1, ge=1),
    limit: int = Query(4, ge=1)
):
    result = products

    # SEARCH
    if keyword:
        result = [p for p in result if keyword.lower() in p["name"].lower()]

    # SORT
    if sort_by in ["price", "name"]:
        result = sorted(result, key=lambda p: p[sort_by], reverse=(order == "desc"))

    # PAGINATION
    total = len(result)
    start = (page - 1) * limit
    paged = result[start:start + limit]

    return {
        "keyword": keyword,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "limit": limit,
        "total_found": total,
        "total_pages": -(-total // limit),
        "products": paged
    }

# ═══════════════════════════════
# ORDER CREATION (for testing Q4)
# ═══════════════════════════════

@app.post("/orders")
def create_order(order: OrderRequest):
    global order_counter

    product = next((p for p in products if p["id"] == order.product_id), None)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    total = product["price"] * order.quantity

    new_order = {
        "order_id": order_counter,
        "customer_name": order.customer_name,
        "product": product["name"],
        "quantity": order.quantity,
        "delivery_address": order.delivery_address,
        "total_price": total
    }

    orders.append(new_order)
    order_counter += 1

    return {"message": "Order placed", "order": new_order}

# ═══════════════════════════════
# GET ALL ORDERS
# ═══════════════════════════════

@app.get("/orders")
def get_orders():
    return {"orders": orders}