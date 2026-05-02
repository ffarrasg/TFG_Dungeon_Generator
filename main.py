import pygame

from config import (
    MAP_WIDTH, MAP_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT,
    FPS, WALL, WATER, PLAYER, EXIT, KEY, ENEMY,
    WALKABLE_TERRAINS, ALGORITHMS, DEFAULT_ALGORITHM
)

from src.algorithms.random_walk_generator import RandomWalkGenerator
from src.algorithms.bsp_generator import BSPGenerator
from src.algorithms.cellular_generator import CellularGenerator

from src.core.metrics import measure_generation_time, walkable_percentage
from src.core.object_placement import (
    place_player, place_exit, place_key
)
from src.core.terrain_generator import apply_base_terrain, apply_water_patches
from src.core.map_utils import (
    find_tile, path_exists, find_path,
    PASSABLE_BEFORE_KEY, PASSABLE_AFTER_KEY
)
from src.core.enemy_manager import place_level_enemies, move_enemies

from src.visual.renderer import draw_grid, draw_hud, draw_game_over, draw_start_screen

from src.core.statistics import save_map_statistics

def find_player(grid):
    """Retorna la posició del jugador."""
    for y, row in enumerate(grid):
        for x, cell in enumerate(row):
            if cell == PLAYER:
                return x, y
    return None


def build_generator(algorithm_name):
    """Construeix l'algoritme seleccionat."""
    if algorithm_name == "random_walk":
        return RandomWalkGenerator(MAP_WIDTH, MAP_HEIGHT)
    elif algorithm_name == "bsp":
        return BSPGenerator(MAP_WIDTH, MAP_HEIGHT)
    elif algorithm_name == "cellular":
        return CellularGenerator(MAP_WIDTH, MAP_HEIGHT)
    else:
        raise ValueError(f"Algoritme desconegut: {algorithm_name}")


def is_level_solvable(grid):
    """
    Comprova si el nivell és resoluble.

    Abans de tenir la clau, la porta no es considera transitable.
    Després de tenir la clau, la porta sí que es pot utilitzar.
    """
    player_pos = find_tile(grid, PLAYER)
    key_pos = find_tile(grid, KEY)
    exit_pos = find_tile(grid, EXIT)

    if player_pos is None or key_pos is None or exit_pos is None:
        return False

    # Primer s'ha de poder arribar a la clau sense travessar la porta
    if not path_exists(grid, player_pos, key_pos, PASSABLE_BEFORE_KEY):
        return False

    # Després de tenir la clau, s'ha de poder arribar a la sortida
    if not path_exists(grid, key_pos, exit_pos, PASSABLE_AFTER_KEY):
        return False

    return True


def generate_base_map(level, algorithm_name):
    """
    Genera el mapa base.

    Es repeteix fins que el mapa sigui resoluble.
    També desa estadístiques del mapa generat.
    """
    attempt = 0

    while True:
        attempt += 1

        generator = build_generator(algorithm_name)
        grid, generation_time = measure_generation_time(generator)

        apply_base_terrain(grid)
        apply_water_patches(grid)

        entity_under_tiles = {}

        player_pos, player_under_tile = place_player(grid)
        entity_under_tiles[player_pos] = player_under_tile

        exit_pos, exit_under_tile = place_exit(grid, player_pos)
        entity_under_tiles[exit_pos] = exit_under_tile

        key_pos, key_under_tile = place_key(grid, player_pos)
        entity_under_tiles[key_pos] = key_under_tile

        if is_level_solvable(grid):

            print(f"Level {level}")
            print(f"Algorithm: {algorithm_name}")
            print(f"Temps de generació: {generation_time:.6f} s")
            print(f"Percentatge transitable: {walkable_percentage(grid):.2%}")
            print(f"Mapa vàlid trobat a l'intent {attempt}")

            return grid, player_under_tile, entity_under_tiles, generation_time, attempt


def place_valid_enemies(grid, level, entity_under_tiles):
    """
    Calcula el camí crític del nivell i col·loca els enemics evitant-lo.

    El camí crític és:
    - jugador -> clau
    - clau -> sortida

    Això evita que els enemics apareguin o es moguin sobre el recorregut
    necessari per completar el nivell.
    """
    player_pos = find_tile(grid, PLAYER)
    key_pos = find_tile(grid, KEY)
    exit_pos = find_tile(grid, EXIT)

    path1 = find_path(grid, player_pos, key_pos, PASSABLE_BEFORE_KEY) or []
    path2 = find_path(grid, key_pos, exit_pos, PASSABLE_AFTER_KEY) or []

    critical_path = set(path1 + path2)

    enemies = place_level_enemies(
        grid,
        level,
        entity_under_tiles,
        forbidden_positions=critical_path
    )

    return enemies


def generate_new_map(level, algorithm):
    """
    Genera mapa complet amb enemics i desa les mètriques finals.
    """
    grid, player_under_tile, entity_under_tiles, generation_time, attempt = generate_base_map(
        level,
        algorithm
    )

    enemies = place_valid_enemies(
        grid,
        level,
        entity_under_tiles
    )

    save_map_statistics(
        grid,
        algorithm,
        level,
        generation_time,
        attempt
    )

    return grid, player_under_tile, entity_under_tiles, enemies


def move_player(grid, dx, dy, has_key, player_under_tile, entity_under_tiles):
    """Moviment del jugador."""
    x, y = find_player(grid)
    nx, ny = x + dx, y + dy

    if not (0 <= nx < len(grid[0]) and 0 <= ny < len(grid)):
        return has_key, False, False, player_under_tile

    target = grid[ny][nx]

    # Murs o aigua
    if target in (WALL, WATER):
        return has_key, False, False, player_under_tile

    # Enemic → GAME OVER immediat
    if target == ENEMY:
        return has_key, True, False, player_under_tile

    # Sortida
    if target == EXIT:
        if has_key:
            return has_key, False, True, player_under_tile
        return has_key, False, False, player_under_tile

    # Clau
    if target == KEY:
        has_key = True

    # Moure jugador
    old_pos = (x, y)
    new_pos = (nx, ny)

    grid[y][x] = player_under_tile
    entity_under_tiles.pop(old_pos, None)

    player_under_tile = entity_under_tiles.get(new_pos, target)
    entity_under_tiles.pop(new_pos, None)

    grid[ny][nx] = PLAYER
    entity_under_tiles[new_pos] = player_under_tile

    return has_key, False, False, player_under_tile


def next_algorithm(current):
    """Canvia algoritme."""
    i = ALGORITHMS.index(current)
    return ALGORITHMS[(i + 1) % len(ALGORITHMS)]


def reset_game(algorithm):
    """Reinicia partida."""
    level = 1
    has_key = False
    game_over = False

    grid, player_under_tile, entity_under_tiles, enemies = generate_new_map(level, algorithm)

    return grid, level, has_key, game_over, player_under_tile, entity_under_tiles, enemies


def main():
    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Dungeon Generator")

    clock = pygame.time.Clock()

    font = pygame.font.SysFont(None, 30)
    title_font = pygame.font.SysFont(None, 70)
    game_over_font = pygame.font.SysFont(None, 64)

    current_algorithm = DEFAULT_ALGORITHM
    game_state = "start"

    start_background = build_generator(current_algorithm).generate()

    grid, level, has_key, game_over, player_under_tile, entity_under_tiles, enemies = reset_game(
        current_algorithm
    )

    running = True
    while running:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:

                # PANTALLA INICIAL
                if game_state == "start":
                    if event.key == pygame.K_RETURN:
                        game_state = "playing"

                elif game_state == "playing":

                    if event.key == pygame.K_r:
                        grid, level, has_key, game_over, player_under_tile, entity_under_tiles, enemies = reset_game(
                            current_algorithm
                        )

                    elif event.key == pygame.K_a:
                        current_algorithm = next_algorithm(current_algorithm)
                        grid, level, has_key, game_over, player_under_tile, entity_under_tiles, enemies = reset_game(
                            current_algorithm
                        )

                    elif not game_over:

                        next_level = False
                        moved = False  

                        if event.key == pygame.K_UP:
                            has_key, game_over, next_level, player_under_tile = move_player(
                                grid, 0, -1, has_key, player_under_tile, entity_under_tiles
                            )
                            moved = True

                        elif event.key == pygame.K_DOWN:
                            has_key, game_over, next_level, player_under_tile = move_player(
                                grid, 0, 1, has_key, player_under_tile, entity_under_tiles
                            )
                            moved = True

                        elif event.key == pygame.K_LEFT:
                            has_key, game_over, next_level, player_under_tile = move_player(
                                grid, -1, 0, has_key, player_under_tile, entity_under_tiles
                            )
                            moved = True

                        elif event.key == pygame.K_RIGHT:
                            has_key, game_over, next_level, player_under_tile = move_player(
                                grid, 1, 0, has_key, player_under_tile, entity_under_tiles
                            )
                            moved = True

                        # 🔥 CANVI CLAU
                        if next_level:
                            level += 1
                            has_key = False

                            grid, player_under_tile, entity_under_tiles, enemies = generate_new_map(
                                level,
                                current_algorithm
                            )

                        elif moved and not game_over:
                            # Els enemics només es mouen si el jugador no ha mort
                            game_over = move_enemies(
                                grid,
                                enemies,
                                entity_under_tiles
                            )

        # RENDER
        if game_state == "start":
            draw_start_screen(screen, title_font, font, start_background)
        else:
            screen.fill((0, 0, 0))
            draw_grid(screen, grid, entity_under_tiles)
            draw_hud(screen, font, has_key, level, current_algorithm)

            if game_over:
                draw_game_over(screen, game_over_font)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()