import pytest
from framework import app, _routes
from main import dispatch
from middleware import transaction_log
from models import db

def reset_state():
    """Скидає глобальний стан для забезпечення ізоляції тестів."""
    transaction_log.clear() # [cite: 55]
    _routes.clear() # [cite: 55]
    
    db["customers"] = [] # [cite: 55]
    db["products"] = [] # [cite: 55]
    db["orders"] = [] # [cite: 55]
    
    import importlib # [cite: 55]
    import views # [cite: 55]
    importlib.reload(views) # [cite: 55]

def test_route_registration_integrity():
    """Перевіряє, що декоратори правильно реєструють шляхи у фреймворку."""
    reset_state()
    assert ('GET', '/customers') in _routes # [cite: 55]
    assert ('POST', '/orders') in _routes # [cite: 56]

def test_validation_email_format():
    """Перевіряє, що створення Клієнта не вдається з невірним email."""
    reset_state()
    request = {
        "method": "POST",
        "path": "/customers",
        "session": {"user_id": 1, "role": "admin"},
        "body": {"name": "test name", "email": "invalid-email"}, # [cite: 56]
        "query": {}
    }
    response = dispatch(request)
    assert response['status_code'] == 400 # [cite: 56]
    assert len(db["customers"]) == 0 # [cite: 56]

def test_validation_positive_price():
    """Перевіряє, що створення Продукту не вдається з від'ємною ціною."""
    reset_state()
    request = {
        "method": "POST",
        "path": "/products",
        "session": {"user_id": 1, "role": "admin"},
        "body": {"name": "Laptop", "price": -100}, # [cite: 56]
        "query": {}
    }
    response = dispatch(request)
    assert response['status_code'] == 400 # [cite: 56]
    assert len(db["products"]) == 0 # [cite: 56]

def test_relational_integrity_valid_order():
    """Перевіряє, що створення Замовлення вдається з valid ID."""
    reset_state()
    db["customers"].append({"id": 1, "name": "test name", "email": "a@test.com"}) # [cite: 56]
    db["products"].append({"id": 1, "name": "Laptop", "price": 1000}) # [cite: 56]
    
    request = {
        "method": "POST",
        "path": "/orders",
        "session": {"user_id": 1, "role": "user"}, # [cite: 57]
        "body": {"customer_id": 1, "product_id": 1, "quantity": 2}, # [cite: 57]
        "query": {}
    }
    response = dispatch(request)
    assert response['status_code'] == 201 # [cite: 57]
    assert len(db["orders"]) == 1 # [cite: 57]
    assert db["orders"][0]["total"] == 2000 # [cite: 57]

def test_relational_integrity_invalid_order():
    """Перевіряє, що створення Замовлення не вдається з невірними ID."""
    reset_state() # [cite: 59]
    request = {
        "method": "POST",
        "path": "/orders",
        "session": {"user_id": 1, "role": "user"}, # [cite: 59]
        "body": {"customer_id": 999, "product_id": 999, "quantity": 1}, # [cite: 59]
        "query": {}
    }
    response = dispatch(request)
    assert response['status_code'] == 400 # [cite: 59]
    assert len(db["orders"]) == 0 # [cite: 59]

def test_audit_log_capture_relational():
    """Перевіряє, що audit log записує операції Замовлення."""
    reset_state()
    db["customers"].append({"id": 1, "name": "test name", "email": "a@test.com"}) # [cite: 59]
    db["products"].append({"id": 1, "name": "Laptop", "price": 1000}) # [cite: 59]
    
    request = {
        "method": "POST",
        "path": "/orders",
        "session": {"user_id": 1, "role": "user"}, # [cite: 59]
        "body": {"customer_id": 1, "product_id": 1, "quantity": 1}, # [cite: 59]
        "query": {}
    }
    dispatch(request)
    assert len(transaction_log) == 1 # [cite: 59]
    entry = transaction_log[0]
    assert entry['path'] == '/orders' # [cite: 59]
    assert entry['status_code'] == 201 # [cite: 59]