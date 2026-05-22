import json
from typing import Any

def render_json(data: Any) -> str:
    """Використовує json.dumps для перетворення даних у рядок."""
    return json.dumps(data) # [cite: 34]

def render_error(message: str) -> str:
    """Повертає форматований рядок, що вказує на помилку."""
    return json.dumps({"error": message}) # [cite: 35]