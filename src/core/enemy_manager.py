import random
from config import ENEMY, PLAYER, WALKABLE_TERRAINS


DIRECTIONS = [(1, 0), (-1, 0), (0, 1), (0, -1)]


def get_enemy_config(level):
    if level == 1:
        return 3, "static", 0
    elif level == 2:
        return 3, "patrol", 1
    elif level == 3:
        return 4, "patrol", 2
    elif level == 4:
        return 5, "patrol", 3
    elif level == 5:
        return 6, "random", 1
    else:
        return 7, "random", 1


def is_inside(grid, x, y):
    return 0 <= y < len(grid) and 0 <= x < len(grid[0])


def is_enemy_at(enemies, x, y, ignored_enemy=None):
    for enemy in enemies:
        if ignored_enemy is not None and enemy is ignored_enemy:
            continue
        if enemy["x"] == x and enemy["y"] == y:
            return True
    return False


def is_valid_enemy_position(grid, x, y, enemies, ignored_enemy=None):
    """
    Comprova si un enemic pot ocupar una posició.

    Els enemics no poden:
    - sortir del mapa
    - ocupar la mateixa casella que un altre enemic
    - entrar en murs, aigua, clau o porta
    - entrar al camí crític del nivell
    """
    if not is_inside(grid, x, y):
        return False

    if is_enemy_at(enemies, x, y, ignored_enemy=ignored_enemy):
        return False

    forbidden_positions = ignored_enemy.get("forbidden_positions", set()) if ignored_enemy else set()

    if (x, y) in forbidden_positions:
        return False

    return grid[y][x] in WALKABLE_TERRAINS or grid[y][x] == PLAYER


def can_move_steps(grid, enemy, dx, dy, steps, enemies):
    """
    Valida que un enemic pugui moure's diverses caselles en una direcció.
    """
    x = enemy["x"]
    y = enemy["y"]

    for step in range(1, steps + 1):
        nx = x + dx * step
        ny = y + dy * step

        if not is_valid_enemy_position(grid, nx, ny, enemies, ignored_enemy=enemy):
            return False

    return True


def get_valid_patrol_directions(grid, x, y, patrol_range, enemies, forbidden_positions):
    """
    Busca direccions vàlides per a un enemic de patrulla.
    """
    valid_directions = []

    temp_enemy = {
        "x": x,
        "y": y,
        "forbidden_positions": forbidden_positions
    }

    for dx, dy in DIRECTIONS:
        if can_move_steps(grid, temp_enemy, dx, dy, patrol_range, enemies):
            valid_directions.append((dx, dy))

    return valid_directions


def get_enemy_candidates(grid, forbidden_positions=None):
    """
    Retorna possibles posicions inicials per als enemics.
    """
    if forbidden_positions is None:
        forbidden_positions = set()

    candidates = []

    for y, row in enumerate(grid):
        for x, cell in enumerate(row):
            if cell in WALKABLE_TERRAINS and (x, y) not in forbidden_positions:
                candidates.append((x, y))

    random.shuffle(candidates)
    return candidates


def place_level_enemies(grid, level, entity_under_tiles, forbidden_positions=None):
    """
    Col·loca enemics segons el nivell evitant el camí crític.
    """
    if forbidden_positions is None:
        forbidden_positions = set()

    enemy_count, mode, patrol_range = get_enemy_config(level)
    candidates = get_enemy_candidates(grid, forbidden_positions)

    enemies = []

    for x, y in candidates:
        if len(enemies) >= enemy_count:
            break

        if is_enemy_at(enemies, x, y):
            continue

        enemy = {
            "x": x,
            "y": y,
            "under_tile": grid[y][x],
            "mode": mode,
            "range": patrol_range,
            "forbidden_positions": forbidden_positions
        }

        if mode == "patrol":
            valid_dirs = get_valid_patrol_directions(
                grid,
                x,
                y,
                patrol_range,
                enemies,
                forbidden_positions
            )

            if not valid_dirs:
                continue

            dx, dy = random.choice(valid_dirs)

            enemy["dx"] = dx
            enemy["dy"] = dy
            enemy["offset"] = 0
            enemy["forward"] = True

        grid[y][x] = ENEMY
        entity_under_tiles[(x, y)] = enemy["under_tile"]
        enemies.append(enemy)

    return enemies


def move_enemy_to(grid, enemy, new_x, new_y, entity_under_tiles):
    """
    Mou un enemic i restaura el terreny anterior.
    """
    old_x = enemy["x"]
    old_y = enemy["y"]

    old_pos = (old_x, old_y)
    new_pos = (new_x, new_y)

    grid[old_y][old_x] = enemy["under_tile"]
    entity_under_tiles.pop(old_pos, None)

    enemy["under_tile"] = grid[new_y][new_x]
    enemy["x"] = new_x
    enemy["y"] = new_y

    grid[new_y][new_x] = ENEMY
    entity_under_tiles[new_pos] = enemy["under_tile"]


def move_patrol_enemy(grid, enemy, enemies, entity_under_tiles):
    """
    Mou un enemic de patrulla endavant i endarrere.
    """
    dx = enemy["dx"]
    dy = enemy["dy"]

    direction = 1 if enemy["forward"] else -1
    new_offset = enemy["offset"] + direction

    if new_offset > enemy["range"]:
        enemy["forward"] = False
        direction = -1
        new_offset = enemy["offset"] + direction

    elif new_offset < 0:
        enemy["forward"] = True
        direction = 1
        new_offset = enemy["offset"] + direction

    new_x = enemy["x"] + dx * direction
    new_y = enemy["y"] + dy * direction

    if is_inside(grid, new_x, new_y) and grid[new_y][new_x] == PLAYER:
        return True

    if not is_valid_enemy_position(grid, new_x, new_y, enemies, ignored_enemy=enemy):
        enemy["forward"] = not enemy["forward"]
        return False

    move_enemy_to(grid, enemy, new_x, new_y, entity_under_tiles)
    enemy["offset"] = new_offset

    return False


def move_random_enemy(grid, enemy, enemies, entity_under_tiles):
    """
    Mou un enemic aleatòriament a una casella permesa.
    """
    directions = DIRECTIONS[:]
    random.shuffle(directions)

    for dx, dy in directions:
        new_x = enemy["x"] + dx
        new_y = enemy["y"] + dy

        if is_inside(grid, new_x, new_y) and grid[new_y][new_x] == PLAYER:
            return True

        if is_valid_enemy_position(grid, new_x, new_y, enemies, ignored_enemy=enemy):
            move_enemy_to(grid, enemy, new_x, new_y, entity_under_tiles)
            return False

    return False


def move_enemies(grid, enemies, entity_under_tiles):
    """
    Mou tots els enemics després del moviment del jugador.
    """
    for enemy in enemies:
        if enemy["mode"] == "static":
            continue

        if enemy["mode"] == "patrol":
            game_over = move_patrol_enemy(
                grid,
                enemy,
                enemies,
                entity_under_tiles
            )

        elif enemy["mode"] == "random":
            game_over = move_random_enemy(
                grid,
                enemy,
                enemies,
                entity_under_tiles
            )

        else:
            game_over = False

        if game_over:
            return True

    return False