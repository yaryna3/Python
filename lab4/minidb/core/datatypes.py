# Автор: yaryna
from abc import ABC, abstractmethod
from typing import Any
from datetime import datetime

class DataType(ABC):
    """Базовий клас для типів даних."""
    @abstractmethod
    def validate(self, value: Any) -> bool:
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass

    @classmethod
    def from_string(cls, type_str: str) -> 'DataType':
        mapping = {
            'INTEGER': IntegerType, 'STRING': StringType,
            'BOOLEAN': BooleanType, 'DATE': DateType, 'FLOAT': FloatType
        }
        if type_str.upper() not in mapping:
            raise ValueError(f"Невідомий тип даних: {type_str}")
        return mapping[type_str.upper()]()

class IntegerType(DataType):
    def validate(self, value: Any) -> bool:
        return isinstance(value, int) and not isinstance(value, bool)
    def __str__(self) -> str: return "INTEGER"

class StringType(DataType):
    def validate(self, value: Any) -> bool:
        return isinstance(value, str)
    def __str__(self) -> str: return "STRING"

class BooleanType(DataType):
    def validate(self, value: Any) -> bool:
        return isinstance(value, bool)
    def __str__(self) -> str: return "BOOLEAN"

class FloatType(DataType):
    def validate(self, value: Any) -> bool:
        return isinstance(value, (float, int)) and not isinstance(value, bool)
    def __str__(self) -> str: return "FLOAT"

class DateType(DataType):
    def validate(self, value: Any) -> bool:
        if isinstance(value, datetime): return True
        if isinstance(value, str):
            try:
                datetime.fromisoformat(value)
                return True
            except ValueError:
                return False
        return False
    def __str__(self) -> str: return "DATE"