import random
from config import DIRT, PLAYER, EXIT, KEY, ENEMY, WALKABLE_TERRAINS, WALKABLE_OBJECT_PLACEMENT


def _get_positions_by_walkable(grid):
    """
    Retorna totes les posicions del mapa que es consideren transitables.
    """
    positions = []
    for y, row in enumerate(grid):
        for x, cell in enumerate(row):
            if cell in WALKABLE_TERRAINS:
                positions.append((x, y))
    return positions


def _is_inside(grid, x, y):
    """
    Comprova si una coordenada està dins dels límits del mapa.
    """
    return 0 <= y < len(grid) and 0 <= x < len(grid[0])


def _walkable_neighbors(grid, x, y):
    """
    Compta quants veïns transitables té una cel·la.
    """
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    count = 0
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if _is_inside(grid, nx, ny) and grid[ny][nx] in WALKABLE_OBJECT_PLACEMENT:
            count += 1

    return count


def _manhattan_distance(a, b):
    """
    Calcula la distància Manhattan entre dos punts.
    """
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _valid_open_area_cell(grid, x, y, min_neighbors=3):
    """
    Comprova si una cel·la és adequada per col·locar-hi elements.
    """
    if not _is_inside(grid, x, y):
        return False

    if grid[y][x] not in WALKABLE_TERRAINS:
        return False

    return _walkable_neighbors(grid, x, y) >= min_neighbors


def _get_valid_positions(grid, player_pos=None, min_distance=0, min_neighbors=3):
    """
    Retorna posicions vàlides per col·locar elements.
    """
    positions = []

    for y, row in enumerate(grid):
        for x, cell in enumerate(row):
            if not _valid_open_area_cell(grid, x, y, min_neighbors=min_neighbors):
                continue

            if player_pos is not None and _manhattan_distance((x, y), player_pos) < min_distance:
                continue

            positions.append((x, y))

    return positions


def place_player(grid):
    """
    Col·loca el jugador en una zona adequada.
    Retorna la posició i el terreny original de sota.
    """
    valid_positions = _get_valid_positions(
        grid,
        player_pos=None,
        min_distance=0,
        min_neighbors=3
    )

    if not valid_positions:
        valid_positions = _get_valid_positions(
            grid,
            player_pos=None,
            min_distance=0,
            min_neighbors=2
        )

    if not valid_positions:
        valid_positions = _get_positions_by_walkable(grid)

    if valid_positions:
        x, y = random.choice(valid_positions)
        original_tile = grid[y][x]
        grid[y][x] = PLAYER
        return (x, y), original_tile

    return None, DIRT


def place_exit(grid, player_pos=None, min_distance=8):
    """
    Col·loca la sortida en una zona oberta i allunyada del jugador.
    Retorna la posició i el terreny original de sota.
    """
    valid_positions = _get_valid_positions(
        grid,
        player_pos=player_pos,
        min_distance=min_distance,
        min_neighbors=3
    )

    if not valid_positions:
        valid_positions = _get_valid_positions(
            grid,
            player_pos=player_pos,
            min_distance=min_distance,
            min_neighbors=2
        )

    if not valid_positions:
        valid_positions = []
        for x, y in _get_positions_by_walkable(grid):
            if player_pos is None or _manhattan_distance((x, y), player_pos) >= min_distance:
                valid_positions.append((x, y))

    if not valid_positions:
        valid_positions = _get_positions_by_walkable(grid)

    if valid_positions:
        x, y = random.choice(valid_positions)
        original_tile = grid[y][x]
        grid[y][x] = EXIT
        return (x, y), original_tile

    return None, DIRT


def place_key(grid, player_pos=None, min_distance=5):
    """
    Col·loca la clau en una zona adequada.
    Retorna la posició i el terreny original de sota.
    """
    valid_positions = _get_valid_positions(
        grid,
        player_pos=player_pos,
        min_distance=min_distance,
        min_neighbors=3
    )

    if not valid_positions:
        valid_positions = _get_valid_positions(
            grid,
            player_pos=player_pos,
            min_distance=min_distance,
            min_neighbors=2
        )

    if not valid_positions:
        valid_positions = []
        for x, y in _get_positions_by_walkable(grid):
            if player_pos is None or _manhattan_distance((x, y), player_pos) >= min_distance:
                valid_positions.append((x, y))

    if not valid_positions:
        valid_positions = _get_positions_by_walkable(grid)

    if valid_positions:
        x, y = random.choice(valid_positions)
        original_tile = grid[y][x]
        grid[y][x] = KEY
        return (x, y), original_tile

    return None, DIRT


def clear_enemies(grid, enemies=None):
    """
    Elimina els enemics i restaura el terreny original de sota.
    """
    if enemies is None:
        enemies = []

    for enemy in enemies:
        x = enemy["x"]
        y = enemy["y"]
        grid[y][x] = enemy["under_tile"]


def place_enemies(grid, count=3, forbidden_positions=None):
    """
    Col·loca enemics evitant posicions crítiques.
    Retorna una llista amb la informació de cada enemic.
    """
    if forbidden_positions is None:
        forbidden_positions = set()

    floors = _get_positions_by_walkable(grid)

    valid_positions = []
    for x, y in floors:
        if (x, y) in forbidden_positions:
            continue

        if _walkable_neighbors(grid, x, y) >= 3:
            valid_positions.append((x, y))

    if len(valid_positions) < count:
        valid_positions = [pos for pos in floors if pos not in forbidden_positions]

    random.shuffle(valid_positions)

    enemies = []
    for x, y in valid_positions[:count]:
        original_tile = grid[y][x]

        enemy = {
            "x": x,
            "y": y,
            "under_tile": original_tile
        }

        grid[y][x] = ENEMY
        enemies.append(enemy)

    return enemies