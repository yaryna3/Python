# Автор: yaryna
from typing import Dict, Any

class Row:
    """Зберігає дані одного запису у вигляді словника."""
    def __init__(self, id: int, data: Dict[str, Any]):
        self.id = id
        self._data = data
        self._data['id'] = id 

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self._data[key] = value

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Row): return False
        return self.id == other.id and self._data == other._data

    def __iter__(self):
        return iter(self._data.items())

    def __repr__(self) -> str:
        return f"Row({self._data})"

    def to_dict(self) -> Dict[str, Any]:
        return self._data.copy()