# Автор: yaryna
import json
from datetime import datetime
from typing import Dict, List
from minidb.core.table import Table
from minidb.core.column import Column
from minidb.core.row import Row
from minidb.transaction import Transaction
from minidb.query.engine import SimpleQuery

class DBEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime): return obj.isoformat()
        return super().default(obj)

class Database:
    """Центральна точка управління базою даних."""
    def __init__(self, name: str):
        self.name = name
        self._tables: Dict[str, Table] = {}

    def create_table(self, name: str, columns: List[Column]) -> Table:
        table = Table(name, columns, self)
        self._tables[name] = table
        return table

    def get_table(self, name: str) -> Table:
        return self._tables[name]

    def transaction(self) -> Transaction:
        return Transaction(self)

    def query(self, table_name: str) -> SimpleQuery:
        return SimpleQuery(self.get_table(table_name))

    def save_to_json(self, filename: str) -> None:
        data = {name: {'next_id': t._next_id, 'rows': {k: v.to_dict() for k, v in t._rows.items()}} 
                for name, t in self._tables.items()}
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, cls=DBEncoder, indent=4)