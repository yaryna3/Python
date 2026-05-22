import time
import multiprocessing as mp
# Імпортуємо справжні класи для коректних анотацій типів
from multiprocessing.synchronize import Semaphore, Lock
from multiprocessing.queues import Queue

from simulator import onboard_analysis

def worker(drone_id: int, data_size: int, sem: Semaphore, q: Queue, lock: Lock):
    # Обмежуємо кількість одночасних обчислень
    with sem:
        with lock:
            print(f"[Process] Дрон {drone_id}: почав обчислення...")
            
        result = onboard_analysis(drone_id, data_size)
        
        with lock:
            print(f"[Process] Дрон {drone_id}: завершив обчислення")
            
    # Безпечна передача результату в батьківський процес
    q.put(result)

def run_multiprocessing(n: int, data_size: int, max_workers: int = 4) -> tuple[list, float]:
    results = []
    
    # Створюємо об'єкти через стандартний інтерфейс mp
    q = mp.Queue()
    sem = mp.Semaphore(max_workers)
    lock = mp.Lock()
    processes = []
    
    start = time.perf_counter()
    
    for i in range(1, n + 1):
        p = mp.Process(target=worker, args=(i, data_size, sem, q, lock))
        processes.append(p)
        p.start()
        
    # ВИПРАВЛЕННЯ DEADLOCK: Вичитуємо результати з черги ДО того, як робити join().
    # Оскільки запускається n процесів, ми очікуємо рівно n результатів.
    for _ in range(n):
        results.append(q.get())
        
    # Тепер безпечно чекаємо остаточного завершення процесів (cleanup)
    for p in processes:
        p.join()
        
    duration = time.perf_counter() - start
    return results, duration