import csv
import os
from datetime import datetime
from collections import deque

from config import (
    PLAYER, KEY, EXIT, ENEMY, WATER, WALL,
    WALKABLE_TILES,
    PASSABLE_BEFORE_KEY, PASSABLE_AFTER_KEY
)

from src.core.metrics import walkable_percentage
from src.core.map_utils import find_tile, find_path


METRICS_FILE = "data/metrics.csv"


def count_enemies(grid):
    """
    Compta el nombre d'enemics presents al mapa.
    """
    return sum(1 for row in grid for cell in row if cell == ENEMY)


def calculate_tile_percentages(grid):
    """
    Calcula el percentatge d'aigua i murs dins del mapa.
    """
    total = len(grid) * len(grid[0])

    water_count = 0
    wall_count = 0

    for row in grid:
        for cell in row:
            if cell == WATER:
                water_count += 1
            elif cell == WALL:
                wall_count += 1

    water_percentage = water_count / total if total > 0 else 0
    wall_percentage = wall_count / total if total > 0 else 0

    return water_percentage, wall_percentage


def count_connected_regions(grid):
    """
    Calcula el nombre de regions connectades transitables del mapa.

    Una regió correspon a un conjunt de cel·les transitables connectades
    entre si mitjançant moviment en quatre direccions.
    """
    visited = set()
    regions = 0

    height = len(grid)
    width = len(grid[0])

    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    for y in range(height):
        for x in range(width):

            if grid[y][x] not in WALKABLE_TILES:
                continue

            if (x, y) in visited:
                continue

            regions += 1

            queue = deque([(x, y)])
            visited.add((x, y))

            while queue:
                cx, cy = queue.popleft()

                for dx, dy in directions:
                    nx = cx + dx
                    ny = cy + dy

                    if not (0 <= nx < width and 0 <= ny < height):
                        continue

                    if (nx, ny) in visited:
                        continue

                    if grid[ny][nx] not in WALKABLE_TILES:
                        continue

                    visited.add((nx, ny))
                    queue.append((nx, ny))

    return regions


def calculate_main_path_ratio(total_path_length, grid):
    """
    Calcula la proporció del mapa transitable que forma part del camí principal.

    Aquesta mètrica permet estimar si un mapa és més lineal o més obert.
    """
    walkable_tiles = sum(
        1 for row in grid for cell in row if cell in WALKABLE_TILES
    )

    if walkable_tiles == 0:
        return 0

    return total_path_length / walkable_tiles


def calculate_map_statistics(grid, algorithm_name, level, generation_time, attempt):
    """
    Calcula les estadístiques principals d'un mapa generat.
    """
    player_pos = find_tile(grid, PLAYER)
    key_pos = find_tile(grid, KEY)
    exit_pos = find_tile(grid, EXIT)

    path_to_key = find_path(grid, player_pos, key_pos, PASSABLE_BEFORE_KEY)
    path_to_exit = find_path(grid, key_pos, exit_pos, PASSABLE_AFTER_KEY)

    path_to_key_length = len(path_to_key) if path_to_key else 0
    path_to_exit_length = len(path_to_exit) if path_to_exit else 0
    total_path_length = path_to_key_length + path_to_exit_length

    main_path_ratio = calculate_main_path_ratio(
        total_path_length,
        grid
    )

    valid_map = path_to_key is not None and path_to_exit is not None

    water_percentage, wall_percentage = calculate_tile_percentages(grid)

    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "algorithm": algorithm_name,
        "level": level,
        "generation_time_seconds": round(generation_time, 6),

        "walkable_percentage": round(walkable_percentage(grid), 4),
        "water_percentage": round(water_percentage, 4),
        "wall_percentage": round(wall_percentage, 4),
        "connected_regions": count_connected_regions(grid),

        "path_to_key_length": path_to_key_length,
        "path_to_exit_length": path_to_exit_length,
        "total_path_length": total_path_length,
        "main_path_ratio": round(main_path_ratio, 4),

        "enemy_count": count_enemies(grid),

        "valid_map": valid_map,
        "generation_attempt": attempt
    }


def save_statistics(statistics):
    """
    Guarda les estadístiques en un fitxer CSV.

    Si el fitxer no existeix, també crea la capçalera.
    """
    os.makedirs("data", exist_ok=True)

    file_exists = os.path.isfile(METRICS_FILE)

    with open(METRICS_FILE, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=statistics.keys())

        if not file_exists:
            writer.writeheader()

        writer.writerow(statistics)


def save_map_statistics(grid, algorithm_name, level, generation_time, attempt):
    """
    Calcula i desa les estadístiques d'un mapa.
    """
    statistics = calculate_map_statistics(
        grid,
        algorithm_name,
        level,
        generation_time,
        attempt
    )

    save_statistics(statistics)

    return statistics