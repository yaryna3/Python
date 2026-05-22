import numpy as np
import matplotlib.pyplot as plt
import collections
from typing import List, Tuple, Dict, Any, Set, Optional
import time

# =====================================================================

def box_blur(arr: np.ndarray, r: int) -> np.ndarray:
    if r <= 0:
        return arr.astype(np.float32, copy=False)
    a = arr.astype(np.float32, copy=False)
    h, w = a.shape
    k = 2 * r + 1
    p = np.pad(a, ((r, r), (r, r)), mode="edge")
    s = np.zeros((p.shape[0] + 1, p.shape[1] + 1), dtype=np.float32)
    s[1:, 1:] = p.cumsum(axis=0).cumsum(axis=1)
    total = s[k : k + h, k : k + w] - s[0 : h, k : k + w] - s[k : k + h, 0 : w] + s[0 : h, 0 : w]
    return total / (k * k)

def normalize01(x: np.ndarray, eps: float = 1e-8) -> np.ndarray:
    x_float = x.astype(np.float32, copy=False)
    mn, mx = float(x_float.min()), float(x_float.max())
    return (x_float - mn) / (mx - mn + eps)

def _pick_radii(n: int, island_count: int, land_frac: float, rng: np.random.Generator) -> Tuple[int, int]:
    land_frac_clamped = float(np.clip(land_frac, 0.02, 0.85))
    area_per = (land_frac_clamped * (n * n)) / max(1, island_count)
    r_eq = float(np.sqrt(area_per / np.pi))
    r_min = max(3, int(round(r_eq * 0.55)))
    r_max = max(r_min + 1, int(round(r_eq * 1.35)))
    r_max = min(r_max, max(8, n // 6))
    r_min = min(r_min, max(6, r_max - 2))
    return r_min, r_max

def generate_islands(n: int, seed: int, island_count: int, land_frac: float = 0.18, 
                     margin_frac: float = 0.08, coast_noise: float = 0.06, 
                     smooth_frac: float = 0.004, profile_power: float = 2.2, 
                     aspect_min: float = 0.70, aspect_max: float = 1.55, 
                     max_outer_retries: int = 8) -> np.ndarray:
    rng = np.random.default_rng(seed)
    r_min0, r_max0 = _pick_radii(n, island_count, land_frac, rng)
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
    smooth_px0 = max(1, int(round(smooth_frac * n)))

    for outer in range(max_outer_retries):
        shrink = 0.90 ** outer
        r_min = max(2, int(round(r_min0 * shrink)))
        r_max = max(r_min + 1, int(round(r_max0 * shrink)))
        margin = max(1, int(round(margin_frac * r_max)))
        smooth_px = max(1, int(round(smooth_px0 * (0.9 ** outer))))
        cell = max(4, r_max + margin)
        grid = {} 
        centers = []

        def ok_place(cy: int, cx: int, eff: float) -> bool:
            gy, gx = cy // cell, cx // cell
            for yy_ in range(gy - 2, gy + 3):
                for xx_ in range(gx - 2, gx + 3):
                    lst = grid.get((yy_, xx_))
                    if not lst: continue
                    for (py, px, peff, _, _) in lst:
                        if (cy - py) ** 2 + (cx - px) ** 2 < (eff + peff) ** 2:
                            return False
            return True
            
        edge_pad = r_max + margin + 2
        for _ in range(40000 + island_count * 1500):
            if len(centers) >= island_count: break
            rad = int(rng.integers(r_min, r_max + 1))
            aspect = float(rng.uniform(aspect_min, aspect_max))
            a, b = float(rad), float(max(2, int(round(rad * aspect))))
            eff = float(max(a, b) + margin)
            if edge_pad >= n // 2: break
            cy, cx = int(rng.integers(edge_pad, n - edge_pad)), int(rng.integers(edge_pad, n - edge_pad))

            if ok_place(cy, cx, eff):
                centers.append((cy, cx, rad, a, b))
                grid.setdefault((cy // cell, cx // cell), []).append((cy, cx, eff, a, b))

        if len(centers) < island_count: continue

        height = np.zeros((n, n), dtype=np.float32)
        for (cy, cx, rad, a, b) in centers:
            ang = float(rng.uniform(0.0, 2.0 * np.pi))
            ca, sa = float(np.cos(ang)), float(np.sin(ang))
            dy, dx = yy - cy, xx - cx
            xr, yr = ca * dx + sa * dy, -sa * dx + ca * dy
            d = np.sqrt((xr / a) ** 2 + (yr / b) ** 2)
            island = np.clip(1.0 - d, 0.0, 1.0) ** profile_power
            island *= float(rng.uniform(0.8, 1.15))
            height = np.maximum(height, island.astype(np.float32, copy=False))

        if coast_noise > 0:
            noise = box_blur(rng.random((n, n), dtype=np.float32), max(1, smooth_px // 2))
            height = height + coast_noise * noise * (height > 0).astype(np.float32)

        height = box_blur(height, smooth_px)
        land = height > 1e-4
        out = np.zeros((n, n), dtype=np.uint8)
        if np.any(land):
            lh = normalize01(height[land])
            out[land] = (np.floor((lh ** 1.15) * 9.0).astype(np.int32) + 1).clip(1, 9).astype(np.uint8)
        return out
    return np.zeros((n, n), dtype=np.uint8)

# =====================================================================

SEA_LEVEL = 2

def get_binary_map(height_map: np.ndarray, sea_level: int) -> np.ndarray:
    return (height_map > sea_level).astype(int)

def analyze_islands(binary_map: np.ndarray) -> List[Dict[str, Any]]:
    n = binary_map.shape[0]
    visited = np.zeros_like(binary_map, dtype=bool)
    islands_data = []
    island_id = 1
    dirs_4 = [(-1,0), (1,0), (0,-1), (0,1)]
    
    for y in range(n):
        for x in range(n):
            if binary_map[y, x] == 1 and not visited[y, x]:
                island_cells, coastal_cells = [], []
                perimeter = 0
                queue = collections.deque([(y, x)])
                visited[y, x] = True
                
                while queue:
                    cy, cx = queue.popleft()
                    island_cells.append((cy, cx))
                    is_coast = False
                    for dy, dx in dirs_4:
                        ny, nx = cy + dy, cx + dx
                        if 0 <= ny < n and 0 <= nx < n:
                            if binary_map[ny, nx] == 0:
                                perimeter += 1; is_coast = True
                            elif not visited[ny, nx]:
                                visited[ny, nx] = True; queue.append((ny, nx))
                        else: perimeter += 1; is_coast = True
                    if is_coast: coastal_cells.append((cy, cx))
                
                ys, xs = [c[0] for c in island_cells], [c[1] for c in island_cells]
                islands_data.append({
                    "id": island_id, "area": len(island_cells),
                    "bbox": (min(xs), min(ys), max(xs), max(ys)),
                    "perimeter": perimeter, "cells": island_cells, "coast": coastal_cells
                })
                island_id += 1
    return islands_data

def find_base_and_distances(binary_map: np.ndarray, islands: List[Dict[str, Any]]) -> Tuple[Tuple[int, int], Dict[int, int], Dict[int, List[Tuple[int, int]]]]:
    n = binary_map.shape[0]
    
    # ОПТИМІЗАЦІЯ ДЛЯ ШВИДКОСТІ (щоб не зависало на 1000x1000)
    if n >= 1000: step = n // 10
    elif n >= 500: step = n // 15
    else: step = max(1, n // 25)
    
    best_base, best_avg_dist = (0, 0), float('inf')
    best_distances, best_paths = {}, {}
    dirs_4 = [(-1,0), (1,0), (0,-1), (0,1)]
    
    coast_map = {c: isl["id"] for isl in islands for c in isl["coast"]}

    for by in range(0, n, step):
        for bx in range(0, n, step):
            if binary_map[by, bx] == 0:
                distances, paths, parents = {}, {}, {(by, bx): (-1, -1)}
                queue = collections.deque([(by, bx, 0)])
                found_islands = 0
                total_islands = len(islands)
                
                while queue and found_islands < total_islands:
                    cy, cx, dist = queue.popleft()
                    for dy, dx in dirs_4:
                        ny, nx = cy + dy, cx + dx
                        if 0 <= ny < n and 0 <= nx < n and (ny, nx) not in parents:
                            parents[(ny, nx)] = (cy, cx)
                            if binary_map[ny, nx] == 0: queue.append((ny, nx, dist + 1))
                            elif (ny, nx) in coast_map:
                                isl_id = coast_map[(ny, nx)]
                                if isl_id not in distances:
                                    distances[isl_id] = dist + 1
                                    found_islands += 1
                                    path, curr = [], (ny, nx)
                                    while curr != (-1, -1):
                                        path.append(curr); curr = parents[curr]
                                    paths[isl_id] = path[::-1]
                
                if len(distances) == total_islands and total_islands > 0:
                    avg_dist = sum(distances.values()) / len(distances)
                    if avg_dist < best_avg_dist:
                        best_avg_dist, best_base, best_distances, best_paths = avg_dist, (by, bx), distances, paths
                        
    return best_base, best_distances, best_paths

def find_shortest_bridge(binary_map: np.ndarray, islands: List[Dict[str, Any]]) -> Tuple[int, int, List[Tuple[int, int]]]:
    n = binary_map.shape[0]
    dirs_4 = [(-1,0), (1,0), (0,-1), (0,1)]
    best_bridge, min_bridge_len = [], float('inf')
    id1, id2 = -1, -1
    coast_map = {c: isl["id"] for isl in islands for c in isl["coast"]}

    # Оптимізація: беремо топ-10 найбільших островів для пошуку мостів
    islands_to_check = sorted(islands, key=lambda x: x["area"], reverse=True)[:10]

    for start_isl in islands_to_check:
        start_id = start_isl["id"]
        queue = collections.deque([(c[0], c[1], 0) for c in start_isl["coast"]])
        parents = {c: (-1, -1) for c in start_isl["coast"]}
        
        while queue:
            cy, cx, dist = queue.popleft()
            if dist >= min_bridge_len: break
            for dy, dx in dirs_4:
                ny, nx = cy + dy, cx + dx
                if 0 <= ny < n and 0 <= nx < n and (ny, nx) not in parents:
                    parents[(ny, nx)] = (cy, cx)
                    if binary_map[ny, nx] == 0: queue.append((ny, nx, dist + 1))
                    elif binary_map[ny, nx] == 1:
                        target_id = coast_map.get((ny, nx), -1)
                        if target_id != -1 and target_id != start_id:
                            path, curr = [], (ny, nx)
                            while curr != (-1, -1):
                                path.append(curr); curr = parents[curr]
                            path = path[::-1]
                            if len(path) < min_bridge_len:
                                min_bridge_len, best_bridge, id1, id2 = len(path), path, start_id, target_id
                            queue.clear(); break

    return id1, id2, best_bridge

# =====================================================================

if __name__ == "__main__":
    params = ((100, 7), (500, 20), (1000, 35))
    grids, all_results = [], []

    for p in params:
        n, island_count = p
        t_start = time.time()
        
        print(f"\n{'='*50}\nАНАЛІЗ КАРТИ {n}x{n}\n{'='*50}")
        grid = generate_islands(n=n, seed=11, island_count=island_count)
        grids.append(grid)
        
        bin_map = get_binary_map(grid, SEA_LEVEL)
        islands_info = analyze_islands(bin_map)
        print(f"Знайдено островів: {len(islands_info)}")
        
        print("Розрахунок бази та маршрутів...")
        base_pos, distances, paths = find_base_and_distances(bin_map, islands_info)
        print(f"Оптимальна позиція бази: Y={base_pos[0]}, X={base_pos[1]}")
        
        for isl in islands_info:
            i_id = isl["id"]
            dist = distances.get(i_id, 0)
            isl["dist"] = dist
            isl["score"] = isl["area"] / (dist + 1)
            isl["path"] = paths.get(i_id, [])
            
        sorted_by_score = sorted(islands_info, key=lambda k: k['score'], reverse=True)
        sorted_by_dist = sorted(islands_info, key=lambda k: k['dist'])
        
        print("\nТОП-5 Островів за рейтингом (score = area / (dist + 1)):")
        for rank in sorted_by_score[:5]:
            print(f"Острів {rank['id']}: Площа={rank['area']}, Відстань={rank['dist']}, Рейтинг={rank['score']:.2f}")

        print("\nТОП-5 Найближчих островів:")
        for rank in sorted_by_dist[:5]:
            print(f"Острів {rank['id']}: Відстань={rank['dist']}, Рейтинг={rank['score']:.2f}")
            
        print("Пошук моста...")
        b_id1, b_id2, bridge_path = find_shortest_bridge(bin_map, islands_info)
        if b_id1 != -1:
            water_cells_to_fill = max(0, len(bridge_path) - 2)
            print(f"\nНайкоротший міст між островами {b_id1} та {b_id2}. Треба забудувати {water_cells_to_fill} клітинок води.")
        
        all_results.append({
            "bin_map": bin_map, "islands": islands_info, 
            "base": base_pos, "paths": paths, "bridge": bridge_path
        })
        print(f"Карту {n}x{n} оброблено за {time.time() - t_start:.1f} сек.")

    # ================== МАЛЮВАННЯ (ЯК НА СКРІНШОТІ) ==================
    print(f"\n{'='*50}\nМалюємо зображення...\n{'='*50}")
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    for i, ax in enumerate(axes):
        res = all_results[i]
        grid_img = grids[i]
        
        # 1. Малюємо рельєф
        img = ax.imshow(grid_img, cmap="terrain")
        ax.set_title(f"Map {params[i][0]}x{params[i][0]}")
        
        # 2. Острови та шляхи
        for isl in res["islands"]:
            min_x, min_y, max_x, max_y = isl["bbox"]
            
            # Номери островів (червоний текст)
            ax.text(min_x, min_y, str(isl["id"]), color='red', fontsize=8, weight='bold')
            
            # Білі пунктирні шляхи (малюємо відразу масивом, це швидко!)
            path = isl["path"]
            if path:
                py = [p[0] for p in path]
                px = [p[1] for p in path]
                ax.plot(px, py, linestyle=':', color='white', linewidth=1, alpha=0.7)

        # 3. База (рожевий квадрат)
        by, bx = res["base"]
        # Адаптивний розмір квадрата залежно від масштабу
        sq_size = max(4, params[i][0] // 25) 
        base_rect = plt.Rectangle((bx - sq_size/2, by - sq_size/2), sq_size, sq_size, fill=True, color='magenta', zorder=5)
        ax.add_patch(base_rect)
        ax.text(bx + sq_size, by + sq_size, "BASE", color='magenta', fontsize=10, fontweight='bold')
        
        # 4. Міст (жовта лінія)
        bridge = res["bridge"]
        if bridge:
            by_coords = [p[0] for p in bridge]
            bx_coords = [p[1] for p in bridge]
            ax.plot(bx_coords, by_coords, color='yellow', linewidth=2, zorder=4)

    # 5. Спільна кольорова шкала
    cbar = fig.colorbar(img, ax=axes.ravel().tolist(), label="Висота", fraction=0.02, pad=0.04)
    
    plt.savefig("collage_islands.png")
    print("Готово! Зображення збережено в 'collage_islands.png'")
    plt.show()