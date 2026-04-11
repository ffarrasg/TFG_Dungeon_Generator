import random
from config import GRASS, ROCK, DIRT, PLAYER, EXIT, KEY, ENEMY, WALKABLE_TERRAINS


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
    Comptador de veïns transitables en les 4 direccions principals.

    Aquesta funció s'utilitza per detectar si una cel·la forma part d'una
    zona prou oberta o si, al contrari, és un passadís estret.
    """
    walkable_tiles = set(WALKABLE_TERRAINS) | {PLAYER, EXIT, KEY}
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    count = 0
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if _is_inside(grid, nx, ny) and grid[ny][nx] in walkable_tiles:
            count += 1
    return count


def _manhattan_distance(a, b):
    """
    Calcula la distància Manhattan entre dos punts del mapa.
    Aquesta distància es fa servir per evitar que elements importants
    apareguin massa a prop entre ells.
    """
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _valid_open_area_cell(grid, x, y, min_neighbors=3):
    """
    Comprova si una cel·la és adequada per col·locar-hi elements del joc.

    Una cel·la és vàlida si:
    - està dins del mapa
    - és transitable
    - té prou veïns transitables al voltant
    """
    if not _is_inside(grid, x, y):
        return False

    if grid[y][x] not in WALKABLE_TERRAINS:
        return False

    return _walkable_neighbors(grid, x, y) >= min_neighbors


def _get_valid_positions(grid, player_pos=None, min_distance=0, min_neighbors=3):
    """
    Retorna totes les posicions vàlides per col·locar un element del joc.

    Opcionalment es pot indicar:
    - una posició de referència (normalment el jugador)
    - una distància mínima respecte aquesta posició
    - un nombre mínim de veïns transitables
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
    Col·loca el jugador en una posició inicial adequada.

    Es prioritzen zones obertes del mapa per evitar que el jugador aparegui
    en passadissos massa estrets o en posicions poc favorables.
    """
    valid_positions = _get_valid_positions(
        grid,
        player_pos=None,
        min_distance=0,
        min_neighbors=3
    )

    # Si no hi ha prou posicions bones, es relaxa la restricció
    if not valid_positions:
        valid_positions = _get_valid_positions(
            grid,
            player_pos=None,
            min_distance=0,
            min_neighbors=2
        )

    # Últim recurs: qualsevol cel·la transitable
    if not valid_positions:
        valid_positions = _get_positions_by_walkable(grid)

    if valid_positions:
        x, y = random.choice(valid_positions)

        # Es guarda quin terreny hi havia sota del jugador
        original_tile = grid[y][x]

        grid[y][x] = PLAYER
        return (x, y), original_tile

    return None, DIRT


def place_exit(grid, player_pos=None, min_distance=8):
    """
    Col·loca la sortida del nivell en una zona oberta i prou allunyada del jugador.
    """
    valid_positions = _get_valid_positions(
        grid,
        player_pos=player_pos,
        min_distance=min_distance,
        min_neighbors=3
    )

    # Si no hi ha posicions amb prou espai, es relaxa la restricció
    if not valid_positions:
        valid_positions = _get_valid_positions(
            grid,
            player_pos=player_pos,
            min_distance=min_distance,
            min_neighbors=2
        )

    # Si encara no n'hi ha, es manté només la distància mínima
    if not valid_positions:
        valid_positions = []
        for x, y in _get_positions_by_walkable(grid):
            if player_pos is None or _manhattan_distance((x, y), player_pos) >= min_distance:
                valid_positions.append((x, y))

    # Últim recurs: qualsevol cel·la transitable
    if not valid_positions:
        valid_positions = _get_positions_by_walkable(grid)

    if valid_positions:
        x, y = random.choice(valid_positions)
        grid[y][x] = EXIT
        return (x, y)

    return None


def place_key(grid, player_pos=None, min_distance=5):
    """
    Col·loca la clau en una zona adequada del mapa.

    Igual que amb la sortida, es prioritzen zones obertes i
    es manté una certa distància respecte al jugador.
    """
    valid_positions = _get_valid_positions(
        grid,
        player_pos=player_pos,
        min_distance=min_distance,
        min_neighbors=3
    )

    # Si no hi ha prou posicions, es relaxa el nombre mínim de veïns
    if not valid_positions:
        valid_positions = _get_valid_positions(
            grid,
            player_pos=player_pos,
            min_distance=min_distance,
            min_neighbors=2
        )

    # Si encara no n'hi ha, es manté només la distància mínima
    if not valid_positions:
        valid_positions = []
        for x, y in _get_positions_by_walkable(grid):
            if player_pos is None or _manhattan_distance((x, y), player_pos) >= min_distance:
                valid_positions.append((x, y))

    # Últim recurs: qualsevol cel·la transitable
    if not valid_positions:
        valid_positions = _get_positions_by_walkable(grid)

    if valid_positions:
        x, y = random.choice(valid_positions)
        grid[y][x] = KEY
        return (x, y)

    return None


def clear_enemies(grid):
    """
    Elimina tots els enemics del mapa.

    Quan es recalcula la col·locació dels enemics, les seves caselles
    es restauren com a terra base.
    """
    for y, row in enumerate(grid):
        for x, cell in enumerate(row):
            if cell == ENEMY:
                grid[y][x] = DIRT


def place_enemies(grid, count=3, forbidden_positions=None):
    """
    Col·loca enemics al mapa evitant posicions crítiques.

    Les posicions prohibides solen correspondre al camí principal entre
    jugador, clau i sortida, per evitar que els enemics bloquegin el nivell.
    """
    if forbidden_positions is None:
        forbidden_positions = set()

    floors = _get_positions_by_walkable(grid)

    valid_positions = []
    for x, y in floors:
        # No es poden posar enemics en posicions prohibides
        if (x, y) in forbidden_positions:
            continue

        # Es prioritzen zones obertes per evitar bloquejar passadissos
        if _walkable_neighbors(grid, x, y) >= 3:
            valid_positions.append((x, y))

    # Si no hi ha prou posicions bones, es relaxa la restricció
    if len(valid_positions) < count:
        valid_positions = [pos for pos in floors if pos not in forbidden_positions]

    random.shuffle(valid_positions)

    enemies = []
    for x, y in valid_positions[:count]:
        grid[y][x] = ENEMY
        enemies.append((x, y))

    return enemies