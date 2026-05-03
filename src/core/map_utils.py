from collections import deque
from config import PASSABLE_FOR_PATH


def is_inside(grid, x, y):
    return 0 <= y < len(grid) and 0 <= x < len(grid[0])


def find_tile(grid, tile_type):
    for y, row in enumerate(grid):
        for x, cell in enumerate(row):
            if cell == tile_type:
                return (x, y)
    return None


def path_exists(grid, start, goal, passable_tiles=None):
    return find_path(grid, start, goal, passable_tiles) is not None


def find_path(grid, start, goal, passable_tiles=None):
    """
    Retorna el camí més curt entre dos punts.
    Permet definir quines cel·les són transitables segons el context.
    """
    if passable_tiles is None:
        passable_tiles = PASSABLE_FOR_PATH

    if start is None or goal is None:
        return None

    sx, sy = start
    gx, gy = goal

    if not is_inside(grid, sx, sy) or not is_inside(grid, gx, gy):
        return None

    visited = set()
    queue = deque([start])
    visited.add(start)
    parent = {}

    while queue:
        x, y = queue.popleft()

        if (x, y) == goal:
            path = []
            current = goal
            while current != start:
                path.append(current)
                current = parent[current]
            path.append(start)
            path.reverse()
            return path

        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx, ny = x + dx, y + dy

            if is_inside(grid, nx, ny) and (nx, ny) not in visited:
                if grid[ny][nx] in passable_tiles:
                    visited.add((nx, ny))
                    parent[(nx, ny)] = (x, y)
                    queue.append((nx, ny))

    return None