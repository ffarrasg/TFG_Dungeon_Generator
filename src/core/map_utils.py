from collections import deque
from config import GRASS, ROCK, DIRT, PLAYER, EXIT, KEY


# Conjunt de cel·les considerades transitables per al càlcul de camins
PASSABLE_FOR_PATH = {GRASS, ROCK, DIRT, PLAYER, EXIT, KEY}


def is_inside(grid, x, y):
    """
    Comprova si una coordenada està dins dels límits del mapa.
    """
    return 0 <= y < len(grid) and 0 <= x < len(grid[0])


def find_tile(grid, tile_type):
    """
    Cerca la primera aparició d'un tipus de cel·la dins del mapa.

    :param grid: mapa en forma de graella
    :param tile_type: tipus de cel·la a cercar
    :return: coordenades (x, y) o None si no es troba
    """
    for y, row in enumerate(grid):
        for x, cell in enumerate(row):
            if cell == tile_type:
                return (x, y)
    return None


def path_exists(grid, start, goal):
    """
    Comprova si existeix un camí entre dos punts del mapa.

    Utilitza la funció find_path i retorna True o False.
    """
    return find_path(grid, start, goal) is not None


def find_path(grid, start, goal):
    """
    Calcula el camí més curt entre dos punts del mapa utilitzant BFS.

    BFS (Breadth-First Search) garanteix trobar el camí més curt en un
    entorn de graella sense pesos.

    :param grid: mapa
    :param start: punt inicial (x, y)
    :param goal: punt final (x, y)
    :return: llista de coordenades que formen el camí o None si no existeix
    """
    # Comprovació inicial de validesa
    if start is None or goal is None:
        return None

    sx, sy = start
    gx, gy = goal

    if not is_inside(grid, sx, sy) or not is_inside(grid, gx, gy):
        return None

    # Conjunt de cel·les visitades per evitar bucles
    visited = set()

    # Cua per implementar BFS
    queue = deque([start])
    visited.add(start)

    # Diccionari per reconstruir el camí
    parent = {}

    while queue:
        x, y = queue.popleft()

        # Si arribem al destí, reconstruïm el camí
        if (x, y) == goal:
            path = []
            current = goal

            # Es reconstrueix el camí des del final fins a l'inici
            while current != start:
                path.append(current)
                current = parent[current]

            path.append(start)
            path.reverse()
            return path

        # Exploració dels veïns (moviment en 4 direccions)
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx, ny = x + dx, y + dy

            # Es comprova que la nova posició és vàlida i no visitada
            if is_inside(grid, nx, ny) and (nx, ny) not in visited:

                # Només es poden recórrer cel·les transitables
                if grid[ny][nx] in PASSABLE_FOR_PATH:
                    visited.add((nx, ny))
                    parent[(nx, ny)] = (x, y)
                    queue.append((nx, ny))

    # Si no s'ha trobat cap camí
    return None