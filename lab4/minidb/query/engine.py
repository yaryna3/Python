# Автор: yaryna
from typing import List, Any, Tuple, Optional, Union, Dict
from minidb.core.table import Table
from minidb.query.conditions import Condition

class JoinedTable:
    """Внутрішнє з'єднання (INNER JOIN) між двома таблицями."""
    def __init__(self, table1: Table, table2: Table, join_col1: str, join_col2: str):
        self.table1 = table1
        self.table2 = table2
        self.join_col1 = join_col1
        self.join_col2 = join_col2

    def execute(self) -> List[Dict[str, Any]]:
        results = []
        for row1 in self.table1:
            for row2 in self.table2:
                if row1[self.join_col1] == row2[self.join_col2]:
                    combined = {}
                    # Забезпечення унікальності стовпців префіксами
                    for k, v in row1._data.items():
                        combined[f"{self.table1.name}.{k}"] = v
                    for k, v in row2._data.items():
                        combined[f"{self.table2.name}.{k}"] = v
                    results.append(combined)
        return results

class SimpleQuery:
    """Клас для запитів, ланцюжка методів та агрегації."""
    def __init__(self, table: Table):
        self.table = table
        self._select_columns: List[str] = list(table.columns.keys())
        self._condition: Optional[Condition] = None
        self._order_by: Optional[Tuple[str, bool]] = None
        self._limit: Optional[int] = None

    def select(self, columns: List[str]) -> 'SimpleQuery':
        self._select_columns = columns
        return self

    def where(self, condition: Condition) -> 'SimpleQuery':
        self._condition = condition
        return self

    def order_by(self, column: str, ascending: bool = True) -> 'SimpleQuery':
        self._order_by = (column, ascending)
        return self

    def limit(self, count: int) -> 'SimpleQuery':
        self._limit = count
        return self

    def execute(self) -> List[Dict[str, Any]]:
        results = [row.to_dict() for row in self.table if not self._condition or self._condition.evaluate(row)]
        
        if self._order_by:
            col, asc = self._order_by
            results.sort(key=lambda x: x.get(col), reverse=not asc)
            
        if self._limit is not None:
            results = results[:self._limit]
            
        return [{k: r[k] for k in self._select_columns if k in r} for r in results]

    # --- Агрегація ---
    def count(self) -> int:
        return len(self.execute())

    def sum(self, column: str) -> Union[int, float]:
        return sum(row[column] for row in self.execute() if isinstance(row.get(column), (int, float)))

    def avg(self, column: str) -> float:
        valid_rows = [row[column] for row in self.execute() if isinstance(row.get(column), (int, float))]
        return sum(valid_rows) / len(valid_rows) if valid_rows else 0.0