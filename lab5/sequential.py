import time
from simulator import drone_task, onboard_analysis

def run_sequential_io(n: int) -> tuple[list, float]:
    """Послідовна версія Завдання 1 (I/O)"""
    results = []
    start = time.perf_counter()
    
    for i in range(1, n + 1):
        res = drone_task(i)
        if res is not None:
            results.append(res)
            
    duration = time.perf_counter() - start
    return results, duration

def run_sequential_cpu(n: int, data_size: int) -> tuple[list, float]:
    """Послідовна версія Завдання 2 (CPU)"""
    results = []
    start = time.perf_counter()
    
    for i in range(1, n + 1):
        res = onboard_analysis(i, data_size)
        results.append(res)
        
    duration = time.perf_counter() - start
    return results, duration