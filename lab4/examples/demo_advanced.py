# Автор: yaryna
from minidb.database import Database
from minidb.core.column import Column
from minidb.core.datatypes import IntegerType, StringType
from minidb.query.conditions import Condition
from minidb.query.engine import JoinedTable

# 1. Ініціалізація
db = Database("school_db")

db.create_table("departments", [
    Column("id", IntegerType(), unique=True),
    Column("name", StringType(), nullable=False)
])

db.create_table("employees", [
    Column("id", IntegerType(), unique=True),
    Column("name", StringType()),
    Column("dept_id", IntegerType(), references=("departments", "id"))
])

# 2. Транзакції
try:
    with db.transaction():
        db.get_table("departments").insert({"id": 1, "name": "IT"})
        db.get_table("departments").insert({"id": 2, "name": "HR"})
        db.get_table("employees").insert({"id": 101, "name": "Alice", "dept_id": 1})
        db.get_table("employees").insert({"id": 102, "name": "Bob", "dept_id": 2})
        # Викличе помилку -> відкат всієї транзакції
        # db.get_table("employees").insert({"id": 103, "name": "Eve", "dept_id": 99}) 
except Exception as e:
    print(f"Rollback: {e}")

# 3. Складні умови (Condition AND)
cond1 = Condition("dept_id", "=", 1)
cond2 = Condition("name", "LIKE", "Ali")
complex_cond = cond1 & cond2

res = db.query("employees").where(complex_cond).execute()
print(f"Складний запит: {res}")

# 4. JOIN таблиць
join_engine = JoinedTable(db.get_table("employees"), db.get_table("departments"), "dept_id", "id")
print(f"JOIN результат: {join_engine.execute()}")

# 5. Агрегація
print(f"Всього співробітників: {db.query('employees').count()}")

# 6. Збереження бази даних у файл
db.save_to_json("school_db.json")