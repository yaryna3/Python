from functools import wraps
from typing import Callable, Dict, Any, List

transaction_log: List[Dict[str, Any]] = [] # [cite: 25]

def audit_log(func: Callable) -> Callable:
    @wraps(func) # [cite: 25]
    def wrapper(request: Dict[str, Any]) -> Dict[str, Any]:
        log_entry = {
            "method": request.get("method"),
            "path": request.get("path"),
            "user_id": request.get("session", {}).get("user_id"), # [cite: 25]
            "status_code": None
        }
        transaction_log.append(log_entry) # [cite: 25]
        
        response = func(request) # [cite: 25]
        
        log_entry["status_code"] = response.get("status_code") # [cite: 26]
        return response
    return wrapper

def login_required(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(request: Dict[str, Any]) -> Dict[str, Any]:
        if not request.get("session", {}).get("user_id"): # [cite: 26]
            return {"status_code": 401, "body": "Unauthorized", "headers": {}}
        return func(request)
    return wrapper

def role_required(required_role: str) -> Callable: # [cite: 26]
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(request: Dict[str, Any]) -> Dict[str, Any]:
            session = request.get("session", {}) # [cite: 26]
            if session.get("role") != required_role:
                return {"status_code": 403, "body": "Forbidden", "headers": {}}
            return func(request)
        return wrapper
    return decorator