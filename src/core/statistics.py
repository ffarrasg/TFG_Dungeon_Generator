import csv
import os
from datetime import datetime

from config import PLAYER, KEY, EXIT, ENEMY, WATER, WALL
from src.core.metrics import walkable_percentage
from src.core.map_utils import (
    find_tile,
    find_path,
    PASSABLE_BEFORE_KEY,
    PASSABLE_AFTER_KEY
)


METRICS_FILE = "data/metrics.csv"


def count_enemies(grid):
    """
    Compta el nombre d'enemics presents al mapa.
    """
    return sum(1 for row in grid for cell in row if cell == ENEMY)

def calculate_tile_percentages(grid):
    """
    Calcula percentatges d'aigua i murs al mapa.
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

        "path_to_key_length": path_to_key_length,
        "path_to_exit_length": path_to_exit_length,
        "total_path_length": total_path_length,

        "enemy_count": count_enemies(grid),

        "valid_map": valid_map,
        "generation_attempt": attempt
    }


def save_statistics(statistics):
    """
    Guarda les estadístiques en un fitxer CSV.
    Si el fitxer no existeix, crea també la capçalera.
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
    Calcula i guarda les estadístiques d'un mapa.
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