# Автор: yaryna
from typing import Any, Optional, Tuple, Dict
from minidb.core.datatypes import DataType
from minidb.core.row import Row

class Column:
    """Зберігає назву, тип даних та обмеження."""
    def __init__(self, name: str, data_type: DataType, nullable: bool = True, 
                 unique: bool = False, references: Optional[Tuple[str, str]] = None):
        self.name = name
        self.data_type = data_type
        self.nullable = nullable
        self.unique = unique
        self.references = references

    def validate(self, value: Any) -> None:
        if value is None:
            if not self.nullable: raise ValueError(f"Стовпець '{self.name}' не може бути NULL.")
            return
        if not self.data_type.validate(value):
            raise TypeError(f"Значення {value} не відповідає типу {self.data_type}.")

    def _check_unique(self, value: Any, table_rows: Dict[int, Row]) -> None:
        if not self.unique or value is None: return
        for row in table_rows.values():
            if row[self.name] == value:
                raise ValueError(f"Порушення унікальності: '{value}' вже існує.")

    def _check_foreign_key(self, value: Any, database: Any) -> None:
        if not self.references or value is None: return
        ref_table_name, ref_column_name = self.references
        ref_table = database.get_table(ref_table_name)
        if not any(row[ref_column_name] == value for row in ref_table):
            raise ValueError(f"Зовнішній ключ: '{value}' не знайдено в {ref_table_name}.")

    def __repr__(self) -> str:
        ref = f", ref={self.references}" if self.references else ""
        return f"Column({self.name}, {self.data_type}, null={self.nullable}, uniq={self.unique}{ref})"