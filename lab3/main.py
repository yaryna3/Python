from typing import Dict, Any
from framework import _routes
import views # Запускає фазу реєстрації декораторів

def dispatch(request: Dict[str, Any]) -> Dict[str, Any]:
    """Витягує method та path з запиту, шукає функцію у _routes та виконує її."""
    method = request.get("method")
    path = request.get("path")
    
    handler = _routes.get((method, path))
    
    if handler:
        return handler(request) # Запускає стек middleware та view [cite: 8, 9]
    else:
        return {
            "status_code": 404,
            "body": '{"error": "Not Found"}',
            "headers": {"Content-Type": "application/json"}
        }