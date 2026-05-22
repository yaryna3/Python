# Автор: yaryna
from typing import Dict, List, Any, Optional
from minidb.core.column import Column
from minidb.core.row import Row

class Table:
    """Координатор структури даних."""
    def __init__(self, name: str, columns: List[Column], database: Any):
        self.name = name
        self.columns = {col.name: col for col in columns}
        self.database = database
        self._rows: Dict[int, Row] = {}
        self._next_id = 1
        self._indexes: Dict[str, Dict[Any, int]] = {col.name: {} for col in columns if col.unique}

    def insert(self, data: Dict[str, Any]) -> Row:
        for col_name, col in self.columns.items():
            if col_name == 'id': continue
            val = data.get(col_name)
            col.validate(val)
            col._check_unique(val, self._rows)
            col._check_foreign_key(val, self.database)

        row_id = data.get('id', self._next_id)
        if row_id >= self._next_id: self._next_id = row_id + 1

        new_row = Row(row_id, data)
        self._rows[row_id] = new_row
        
        for col_name in self._indexes:
            if data.get(col_name) is not None:
                self._indexes[col_name][data[col_name]] = row_id
        return new_row

    def get_by_id(self, row_id: int) -> Optional[Row]:
        return self._rows.get(row_id)

    def delete(self, row_id: int) -> None:
        """Реалізація політики RESTRICT для зовнішніх ключів."""
        if row_id not in self._rows: return
        row = self._rows[row_id]
        
        for t_name, table in self.database._tables.items():
            if t_name == self.name: continue
            for col in table.columns.values():
                if col.references and col.references[0] == self.name:
                    if any(r[col.name] == row[col.references[1]] for r in table):
                        raise ValueError(f"RESTRICT: є залежні записи в '{t_name}'.")

        for col_name in self._indexes:
            if row[col_name] is not None:
                del self._indexes[col_name][row[col_name]]
        del self._rows[row_id]

    def update(self, row_id: int, new_data: Dict[str, Any]) -> Row:
        row = self._rows[row_id]
        for key, val in new_data.items():
            if key in self.columns:
                col = self.columns[key]
                col.validate(val)
                if row[key] != val:
                    col._check_unique(val, self._rows)
                    col._check_foreign_key(val, self.database)
                    if col.unique:
                        if row[key] is not None: del self._indexes[key][row[key]]
                        if val is not None: self._indexes[key][val] = row_id
                row[key] = val
        return row

    def __iter__(self):
        return iter(self._rows.values())

    def __len__(self):
        return len(self._rows)