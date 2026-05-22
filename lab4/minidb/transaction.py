# Автор: yaryna
import copy
from typing import Any

class TransactionError(Exception):
    pass

class Transaction:
    """Контекстний менеджер транзакцій (Атомарність та Відкат)."""
    def __init__(self, db: Any):
        self.db = db
        self._backup = None

    def __enter__(self):
        self._backup = copy.deepcopy(self.db._tables)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.db._tables = self._backup  # Rollback
        self._backup = None  # Commit (або очищення після Rollback)