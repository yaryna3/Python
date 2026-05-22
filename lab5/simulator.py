import time
import random
import math

def drone_task(drone_id: int) -> dict | None:
    """Імітація операції дрона (послідовна версія)."""
    # 1. Політ до зони
    time.sleep(random.uniform(0.2, 0.8))
    # 2. Зчитування даних
    time.sleep(random.uniform(0.2, 0.8))
    
    # 3. Завантаження на сервер (15% ймовірність помилки)
    if random.random() < 0.15:
        return None
        
    time.sleep(random.uniform(0.4, 0.9))
    return {"drone_id": drone_id, "data": random.uniform(10, 35), "status": "ok"}

def onboard_analysis(drone_id: int, data_size: int) -> dict:
    """Імітація CPU-важкої задачі на борту дрона."""
    score = 0.0
    # Python-обчислення для навантаження на процесор
    for i in range(data_size):
        score += math.sin(i) ** 2 + math.cos(i) ** 2
        
    return {"drone_id": drone_id, "score": float(score), "iterations": data_size, "status": "ok"}