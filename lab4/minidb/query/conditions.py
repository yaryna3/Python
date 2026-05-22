# Автор: yaryna
from typing import Any, List, Optional
from minidb.core.row import Row

class Condition:
    """Клас для побудови дерев умов (AND/OR)."""
    def __init__(self, column: Optional[str] = None, operator: Optional[str] = None, value: Any = None):
        self.column = column
        self.operator = operator
        self.value = value
        self.sub_conditions: List['Condition'] = []
        self.logic: str = ""

    def __and__(self, other: 'Condition') -> 'Condition':
        c = Condition()
        c.logic = "AND"
        c.sub_conditions = [self, other]
        return c

    def __or__(self, other: 'Condition') -> 'Condition':
        c = Condition()
        c.logic = "OR"
        c.sub_conditions = [self, other]
        return c

    def evaluate(self, row: Row) -> bool:
        if self.logic == "AND":
            return all(cond.evaluate(row) for cond in self.sub_conditions)
        if self.logic == "OR":
            return any(cond.evaluate(row) for cond in self.sub_conditions)
        
        val = row[self.column]
        if self.operator == '=': return val == self.value
        elif self.operator == '>': return val > self.value
        elif self.operator == '<': return val < self.value
        elif self.operator == '>=': return val >= self.value
        elif self.operator == '<=': return val <= self.value
        elif self.operator == '!=': return val != self.value
        elif self.operator == 'LIKE': return str(self.value) in str(val)
        return False