import time
import random
import threading

def drone_task_threaded(drone_id: int, results: list, sem: threading.Semaphore, lock: threading.Lock, print_lock: threading.Lock):
    # Політ та зчитування даних
    time.sleep(random.uniform(0.2, 0.8))
    time.sleep(random.uniform(0.2, 0.8))
    
    # Блок завантаження на сервер з обмеженням у 3 одночасні передачі
    with sem:
        if random.random() < 0.15:
            with print_lock:
                print(f"[Thread] Дрон {drone_id}: Помилка мережі (пропущено)")
            return
            
        time.sleep(random.uniform(0.4, 0.9))
        data = {"drone_id": drone_id, "data": random.uniform(10, 35), "status": "ok"}
    
    # Безпечне додавання до спільного ресурсу
    with lock:
        results.append(data)
        
    # Безпечний вивід у консоль
    with print_lock:
        print(f"[Thread] Дрон {drone_id}: Дані успішно завантажено")

def run_threaded(n: int) -> tuple[list, float]:
    results = []
    sem = threading.Semaphore(3)
    lock = threading.Lock()
    print_lock = threading.Lock()
    threads = []
    
    start = time.perf_counter()
    
    for i in range(1, n + 1):
        t = threading.Thread(target=drone_task_threaded, args=(i, results, sem, lock, print_lock))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    duration = time.perf_counter() - start
    return results, duration