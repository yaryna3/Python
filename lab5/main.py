import multiprocessing as mp
from sequential import run_sequential_io, run_sequential_cpu
from threaded import run_threaded
from multiprocess import run_multiprocessing

def benchmark_io(n=40, runs=5):
    print(f"\n--- БЕНЧМАРК ЗАВДАННЯ 1 (I/O, N={n}) ---")
    seq_times = []
    thread_times = []
    
    for i in range(runs):
        print(f"I/O Run {i+1}/{runs}...")
        _, t_seq = run_sequential_io(n)
        seq_times.append(t_seq)
        
        _, t_thr = run_threaded(n)
        thread_times.append(t_thr)
        
    avg_seq = sum(seq_times) / runs
    avg_thr = sum(thread_times) / runs
    speedup = avg_seq / avg_thr if avg_thr > 0 else float('inf')
    
    print(f"Середній час (посл.): {avg_seq:.2f} сек")
    print(f"Середній час (потоки): {avg_thr:.2f} сек")
    print(f"Прискорення (Speedup): {speedup:.2f}x")

def benchmark_cpu(n=20, data_size=500_000, runs=5, max_workers=4):
    print(f"\n--- БЕНЧМАРК ЗАВДАННЯ 2 (CPU, N={n}, SIZE={data_size}) ---")
    seq_times = []
    mp_times = []
    
    for i in range(runs):
        print(f"CPU Run {i+1}/{runs}...")
        _, t_seq = run_sequential_cpu(n, data_size)
        seq_times.append(t_seq)
        
        _, t_mp = run_multiprocessing(n, data_size, max_workers)
        mp_times.append(t_mp)
        
    avg_seq = sum(seq_times) / runs
    avg_mp = sum(mp_times) / runs
    speedup = avg_seq / avg_mp if avg_mp > 0 else float('inf')
    
    print(f"Середній час (посл.): {avg_seq:.2f} сек")
    print(f"Середній час (процеси): {avg_mp:.2f} сек")
    print(f"Прискорення (Speedup): {speedup:.2f}x")

if __name__ == "__main__":
    # Встановлення spawn для уніфікованої поведінки на всіх ОС
    mp.set_start_method("spawn", force=True)
    
    benchmark_io(n=40, runs=5)
    benchmark_cpu(n=20, data_size=800_000, runs=3, max_workers=4)