from typing import Dict, Any
from framework import app
from middleware import audit_log, login_required, role_required
from validators import validate_customer_input, validate_product_input, validate_order_input
from models import get_all_customers, create_customer, get_all_products, create_product, get_all_orders, create_order
from templates import render_json, render_error

@app.get("/customers") # [cite: 51]
@audit_log
@login_required # [cite: 51]
def list_customers(request: Dict[str, Any]) -> Dict[str, Any]: # [cite: 37]
    data = get_all_customers()
    return {"status_code": 200, "body": render_json(data), "headers": {"Content-Type": "application/json"}}

@app.post("/customers") # [cite: 51]
@audit_log
@role_required("admin") # [cite: 51]
def add_customer(request: Dict[str, Any]) -> Dict[str, Any]:
    body = request.get("body", {})
    is_valid, error_msg = validate_customer_input(body) # [cite: 41]
    if not is_valid:
        return {"status_code": 400, "body": render_error(error_msg), "headers": {"Content-Type": "application/json"}} # [cite: 41]
    
    customer = create_customer(body["name"], body["email"]) # [cite: 41]
    return {"status_code": 201, "body": render_json(customer), "headers": {"Content-Type": "application/json"}}

@app.get("/products") # [cite: 51]
@audit_log
def list_products(request: Dict[str, Any]) -> Dict[str, Any]: # [cite: 49]
    data = get_all_products() # [cite: 50]
    return {"status_code": 200, "body": render_json(data), "headers": {"Content-Type": "application/json"}}

@app.post("/products") # [cite: 52]
@audit_log
@role_required("admin") # [cite: 52]
def add_product(request: Dict[str, Any]) -> Dict[str, Any]:
    body = request.get("body", {})
    is_valid, error_msg = validate_product_input(body)
    if not is_valid:
        return {"status_code": 400, "body": render_error(error_msg), "headers": {"Content-Type": "application/json"}}
    
    product = create_product(body["name"], body["price"])
    return {"status_code": 201, "body": render_json(product), "headers": {"Content-Type": "application/json"}}

@app.post("/orders") # [cite: 52]
@audit_log
@login_required # [cite: 52]
def add_order(request: Dict[str, Any]) -> Dict[str, Any]:
    body = request.get("body", {})
    is_valid, error_msg = validate_order_input(body) # [cite: 52]
    if not is_valid:
        return {"status_code": 400, "body": render_error(error_msg), "headers": {"Content-Type": "application/json"}}
    
    order = create_order(body["customer_id"], body["product_id"], body["quantity"]) # [cite: 53]
    if order is None:
        return {"status_code": 400, "body": render_error("Invalid customer_id or product_id"), "headers": {"Content-Type": "application/json"}} # [cite: 42]
        
    return {"status_code": 201, "body": render_json(order), "headers": {"Content-Type": "application/json"}}

@app.get("/orders") # [cite: 53]
@audit_log
@role_required("admin") # [cite: 54]
def list_orders(request: Dict[str, Any]) -> Dict[str, Any]:
    data = get_all_orders()
    return {"status_code": 200, "body": render_json(data), "headers": {"Content-Type": "application/json"}}