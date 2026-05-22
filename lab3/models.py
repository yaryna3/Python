from typing import Dict, List, Any, Optional

db: Dict[str, List[Dict[str, Any]]] = {
    "customers": [], # [cite: 30]
    "products": [],
    "orders": []
}

def get_all_customers() -> List[Dict[str, Any]]:
    return db["customers"]

def create_customer(name: str, email: str) -> Dict[str, Any]:
    new_id = len(db["customers"]) + 1
    customer = {"id": new_id, "name": name, "email": email}
    db["customers"].append(customer)
    return customer

def get_all_products() -> List[Dict[str, Any]]:
    return db["products"]

def create_product(name: str, price: float) -> Dict[str, Any]:
    new_id = len(db["products"]) + 1
    product = {"id": new_id, "name": name, "price": price}
    db["products"].append(product)
    return product

def get_all_orders() -> List[Dict[str, Any]]:
    return db["orders"]

def create_order(customer_id: int, product_id: int, quantity: int) -> Optional[Dict[str, Any]]:
    customer_exists = any(c["id"] == customer_id for c in db["customers"]) # [cite: 31]
    product = next((p for p in db["products"] if p["id"] == product_id), None) # [cite: 31]
    
    if not customer_exists or not product: # [cite: 32]
        return None
        
    total = product["price"] * quantity
    new_id = len(db["orders"]) + 1
    order = {
        "id": new_id,
        "customer_id": customer_id,
        "product_id": product_id,
        "quantity": quantity,
        "total": total
    }
    db["orders"].append(order)
    return order # [cite: 33]