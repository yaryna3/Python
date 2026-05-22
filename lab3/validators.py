from typing import Tuple, Dict, Any

def validate_email(email: str) -> Tuple[bool, str]:
    if isinstance(email, str) and '@' in email and '.' in email: # [cite: 26]
        return True, ""
    return False, "Invalid email format"

def validate_positive_number(value: Any) -> Tuple[bool, str]:
    if isinstance(value, (int, float)) and value > 0: # [cite: 27]
        return True, ""
    return False, "Must be a positive number"

def validate_customer_input(data: Dict[str, Any]) -> Tuple[bool, str]:
    if "name" not in data or not isinstance(data["name"], str): # [cite: 27]
        return False, "Name is required"
    if "email" not in data: # [cite: 27]
        return False, "Email is required"
    return validate_email(data["email"])

def validate_product_input(data: Dict[str, Any]) -> Tuple[bool, str]:
    if "name" not in data or not isinstance(data["name"], str): # [cite: 28]
        return False, "Name is required"
    if "price" not in data: # [cite: 28]
        return False, "Price is required"
    return validate_positive_number(data["price"])

def validate_order_input(data: Dict[str, Any]) -> Tuple[bool, str]:
    if "customer_id" not in data or not isinstance(data["customer_id"], int): # [cite: 28]
        return False, "Invalid customer_id"
    if "product_id" not in data or not isinstance(data["product_id"], int): # [cite: 28]
        return False, "Invalid product_id"
    if "quantity" not in data or not isinstance(data["quantity"], int) or data["quantity"] <= 0: # [cite: 28]
        return False, "Quantity must be a positive integer"
    return True, ""