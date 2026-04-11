import random
from collections import deque
from config import FLOOR, GRASS, ROCK, DIRT, WATER, WALL, WALKABLE_TERRAINS


def _is_inside(grid, x, y):
    """
    Comprova si una coordenada està dins dels límits del mapa.
    """
    return 0 <= y < len(grid) and 0 <= x < len(grid[0])


def _neighbors4(x, y):
    """
    Retorna els 4 veïns ortogonals d'una cel·la.
    """
    return [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]


def _get_floor_positions(grid):
    """
    Retorna totes les posicions del mapa que encara són FLOOR.

    Aquestes cel·les representen el terreny base abans d'aplicar-hi
    textures com herba, roca o terra.
    """
    positions = []
    for y, row in enumerate(grid):
        for x, cell in enumerate(row):
            if cell == FLOOR:
                positions.append((x, y))
    return positions


def _get_walkable_positions(grid):
    """
    Retorna totes les posicions transitables del mapa.
    """
    positions = []
    for y, row in enumerate(grid):
        for x, cell in enumerate(row):
            if cell in WALKABLE_TERRAINS:
                positions.append((x, y))
    return positions


def apply_base_terrain(grid):
    """
    Converteix les cel·les FLOOR del mapa base en diferents tipus de terreny:
    herba, roca o terra.

    Els terrenys es generen en taques per evitar una distribució completament
    aleatòria i donar un aspecte més coherent al mapa.
    """
    floors = _get_floor_positions(grid)
    random.shuffle(floors)

    visited = set()

    for start_x, start_y in floors:
        if (start_x, start_y) in visited:
            continue

        # Es tria aleatòriament un tipus de terreny
        terrain_type = random.choice([GRASS, ROCK, DIRT])

        # Es defineix la mida aproximada de la taca
        patch_size = random.randint(5, 12)

        queue = deque()
        queue.append((start_x, start_y))
        patch_cells = []

        # Expansió local del terreny a partir d'una cel·la inicial
        while queue and len(patch_cells) < patch_size:
            x, y = queue.popleft()

            if (x, y) in visited:
                continue
            if not _is_inside(grid, x, y):
                continue
            if grid[y][x] != FLOOR:
                continue

            visited.add((x, y))
            patch_cells.append((x, y))

            neighbors = _neighbors4(x, y)
            random.shuffle(neighbors)
            for nx, ny in neighbors:
                if (nx, ny) not in visited and _is_inside(grid, nx, ny) and grid[ny][nx] == FLOOR:
                    if random.random() < 0.85:
                        queue.append((nx, ny))

        # Aplicació final del tipus de terreny sobre la taca generada
        for x, y in patch_cells:
            grid[y][x] = terrain_type

    return grid


def _flood_fill_count(grid, start):
    """
    Compta quantes cel·les transitables estan connectades a partir d'un punt inicial.

    Aquesta funció s'utilitza per comprovar la connectivitat del mapa.
    """
    if start is None:
        return 0

    sx, sy = start
    if not _is_inside(grid, sx, sy):
        return 0
    if grid[sy][sx] not in WALKABLE_TERRAINS:
        return 0

    visited = set()
    queue = deque([(sx, sy)])
    visited.add((sx, sy))

    while queue:
        x, y = queue.popleft()
        for nx, ny in _neighbors4(x, y):
            if _is_inside(grid, nx, ny) and (nx, ny) not in visited:
                if grid[ny][nx] in WALKABLE_TERRAINS:
                    visited.add((nx, ny))
                    queue.append((nx, ny))

    return len(visited)


def _all_walkable_connected(grid):
    """
    Comprova si totes les cel·les transitables del mapa continuen connectades.

    Això és important per evitar que obstacles com l'aigua separin el mapa
    en zones inaccessibles.
    """
    walkable = _get_walkable_positions(grid)
    if not walkable:
        return False

    connected_count = _flood_fill_count(grid, walkable[0])
    return connected_count == len(walkable)


def try_place_water_patch(grid, min_size=5, max_size=8, attempts=20):
    """
    Intenta col·locar una taca d'aigua al mapa sense trencar-ne la connectivitat.

    L'aigua es tracta com un obstacle no transitable, però es controla que
    la seva aparició no deixi parts del nivell aïllades.
    """
    walkable = _get_walkable_positions(grid)
    if not walkable:
        return False

    for _ in range(attempts):
        start_x, start_y = random.choice(walkable)
        patch_size = random.randint(min_size, max_size)

        queue = deque([(start_x, start_y)])
        visited = set()
        patch = []

        # Es genera una taca d'aigua a partir d'una expansió local
        while queue and len(patch) < patch_size:
            x, y = queue.popleft()

            if (x, y) in visited:
                continue
            if not _is_inside(grid, x, y):
                continue
            if grid[y][x] not in WALKABLE_TERRAINS:
                continue

            visited.add((x, y))
            patch.append((x, y))

            neighbors = _neighbors4(x, y)
            random.shuffle(neighbors)
            for nx, ny in neighbors:
                if (nx, ny) not in visited and _is_inside(grid, nx, ny):
                    if grid[ny][nx] in WALKABLE_TERRAINS and random.random() < 0.8:
                        queue.append((nx, ny))

        # Es descarten les taques massa petites
        if len(patch) < min_size:
            continue

        # Prova temporal: es guarda el terreny original
        original_values = {}
        for x, y in patch:
            original_values[(x, y)] = grid[y][x]
            grid[y][x] = WATER

        # Si la taca d'aigua trenca la connectivitat, es desfà
        if not _all_walkable_connected(grid):
            for (x, y), value in original_values.items():
                grid[y][x] = value
            continue

        return True

    return False


def apply_water_patches(grid, patch_count=2):
    """
    Intenta afegir diverses taques d'aigua al mapa.

    El nombre de llacs es controla amb el paràmetre patch_count.
    """
    for _ in range(patch_count):
        try_place_water_patch(grid, min_size=5, max_size=8, attempts=30)

    return grid