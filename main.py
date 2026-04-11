import pygame

# Importació de constants de configuració del projecte
from config import (
    MAP_WIDTH, MAP_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT,
    FPS, WALL, WATER, DIRT, PLAYER, EXIT, KEY, ENEMY,
    WALKABLE_TERRAINS, ALGORITHMS, DEFAULT_ALGORITHM
)

# Importació dels diferents algoritmes de generació de mapes
from src.algorithms.random_walk_generator import RandomWalkGenerator
from src.algorithms.bsp_generator import BSPGenerator
from src.algorithms.cellular_generator import CellularGenerator

# Importació de funcions auxiliars
from src.core.metrics import measure_generation_time, walkable_percentage
from src.core.object_placement import (
    place_player, place_exit, place_key, place_enemies, clear_enemies
)
from src.core.terrain_generator import apply_base_terrain, apply_water_patches
from src.core.map_utils import find_tile, path_exists, find_path

# Funcions de renderitzat
from src.visual.renderer import draw_grid, draw_hud, draw_game_over


def find_player(grid):
    """
    Cerca la posició actual del jugador dins del mapa.
    Retorna una tupla (x, y) o None si no es troba.
    """
    for y, row in enumerate(grid):
        for x, cell in enumerate(row):
            if cell == PLAYER:
                return x, y
    return None


def build_generator(algorithm_name):
    """
    Crea una instància de l'algoritme de generació seleccionat.
    Permet canviar d'algoritme dinàmicament durant l'execució.
    """
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
    Es considera resoluble si:
    - existeix camí del jugador a la clau
    - existeix camí de la clau a la sortida
    """
    player_pos = find_tile(grid, PLAYER)
    key_pos = find_tile(grid, KEY)
    exit_pos = find_tile(grid, EXIT)

    if player_pos is None or key_pos is None or exit_pos is None:
        return False

    if not path_exists(grid, player_pos, key_pos):
        return False

    if not path_exists(grid, key_pos, exit_pos):
        return False

    return True


def generate_base_map(level, algorithm_name, max_attempts=50):
    """
    Genera un mapa base sense enemics.
    Es repeteix el procés fins que el mapa és jugable.
    """
    for attempt in range(max_attempts):
        generator = build_generator(algorithm_name)

        # Generació del mapa amb l'algoritme escollit
        grid, generation_time = measure_generation_time(generator)

        # Aplicació de textures (herba, roca, terra)
        apply_base_terrain(grid)

        # Afegir zones d'aigua com a obstacles
        apply_water_patches(grid, patch_count=2)

        # Col·locació d'elements principals
        player_pos, player_under_tile = place_player(grid)
        place_exit(grid, player_pos=player_pos, min_distance=8)
        place_key(grid, player_pos=player_pos, min_distance=5)

        # Validació del mapa
        if is_level_solvable(grid):
            print(f"Level {level}")
            print(f"Algorithm: {algorithm_name}")
            print(f"Temps de generació: {generation_time:.6f} s")
            print(f"Percentatge transitable: {walkable_percentage(grid):.2%}")
            print(f"Mapa base vàlid trobat a l'intent {attempt + 1}")
            return grid, player_under_tile

    # Si no es troba cap mapa vàlid
    raise RuntimeError("No s'ha pogut generar un mapa base resoluble.")


def place_valid_enemies(grid, level, max_attempts=40):
    """
    Col·loca enemics evitant bloquejar el camí principal.
    Si bloquegen el mapa, es recol·loquen sense regenerar tot el nivell.
    """
    player_pos = find_tile(grid, PLAYER)
    key_pos = find_tile(grid, KEY)
    exit_pos = find_tile(grid, EXIT)

    # Camins crítics del nivell
    path1 = find_path(grid, player_pos, key_pos) or []
    path2 = find_path(grid, key_pos, exit_pos) or []

    critical_path = set(path1 + path2)

    # Nombre d'enemics augmenta amb el nivell
    enemy_count = min(3 + level, 8)

    for _ in range(max_attempts):
        clear_enemies(grid)
        place_enemies(grid, count=enemy_count, forbidden_positions=critical_path)

        if is_level_solvable(grid):
            return True

    # Si no es pot garantir la jugabilitat, es treuen els enemics
    clear_enemies(grid)
    return False


def generate_new_map(level, algorithm_name):
    """
    Genera un mapa complet:
    - mapa base vàlid
    - col·locació d'enemics
    """
    grid, player_under_tile = generate_base_map(level, algorithm_name)
    place_valid_enemies(grid, level)
    return grid, player_under_tile


def move_player(grid, dx, dy, has_key, player_under_tile):
    """
    Gestiona el moviment del jugador i les interaccions amb el mapa.
    """
    pos = find_player(grid)
    if not pos:
        return has_key, False, False, player_under_tile

    x, y = pos
    new_x = x + dx
    new_y = y + dy

    # Evitar sortir del mapa
    if new_x < 0 or new_x >= len(grid[0]) or new_y < 0 or new_y >= len(grid):
        return has_key, False, False, player_under_tile

    target_tile = grid[new_y][new_x]

    # Obstacles no transitables
    if target_tile == WALL or target_tile == WATER:
        return has_key, False, False, player_under_tile

    # Enemic → final de la partida
    if target_tile == ENEMY:
        return has_key, True, False, player_under_tile

    # Sortida
    if target_tile == EXIT:
        if has_key:
            return has_key, False, True, player_under_tile
        return has_key, False, False, player_under_tile

    # Clau
    if target_tile == KEY:
        has_key = True
        grid[y][x] = player_under_tile
        player_under_tile = DIRT
        grid[new_y][new_x] = PLAYER
        return has_key, False, False, player_under_tile

    # Moviment normal
    if target_tile in WALKABLE_TERRAINS:
        grid[y][x] = player_under_tile
        player_under_tile = target_tile
        grid[new_y][new_x] = PLAYER

    return has_key, False, False, player_under_tile


def next_algorithm(current_algorithm):
    """
    Retorna el següent algoritme disponible (cicle).
    """
    current_index = ALGORITHMS.index(current_algorithm)
    next_index = (current_index + 1) % len(ALGORITHMS)
    return ALGORITHMS[next_index]


def reset_game(current_algorithm):
    """
    Reinicia el joc:
    - nivell 1
    - sense clau
    - nou mapa
    """
    level = 1
    has_key = False
    game_over = False
    grid, player_under_tile = generate_new_map(level, current_algorithm)
    return grid, level, has_key, game_over, player_under_tile


def main():
    """
    Funció principal del programa.
    Gestiona el bucle del joc i la interacció amb l'usuari.
    """
    pygame.init()

    # Creació de la finestra
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Dungeon Generator Prototype")

    clock = pygame.time.Clock()

    # Fonts per al HUD i missatges
    font = pygame.font.SysFont(None, 30)
    game_over_font = pygame.font.SysFont(None, 64)

    current_algorithm = DEFAULT_ALGORITHM

    # Inicialització del joc
    grid, level, has_key, game_over, player_under_tile = reset_game(current_algorithm)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:

                # Reiniciar partida
                if event.key == pygame.K_r:
                    grid, level, has_key, game_over, player_under_tile = reset_game(current_algorithm)

                # Canviar algoritme
                elif event.key == pygame.K_a:
                    current_algorithm = next_algorithm(current_algorithm)
                    grid, level, has_key, game_over, player_under_tile = reset_game(current_algorithm)

                # Moviment del jugador
                elif not game_over:
                    next_level = False

                    if event.key == pygame.K_UP:
                        has_key, game_over, next_level, player_under_tile = move_player(
                            grid, 0, -1, has_key, player_under_tile
                        )
                    elif event.key == pygame.K_DOWN:
                        has_key, game_over, next_level, player_under_tile = move_player(
                            grid, 0, 1, has_key, player_under_tile
                        )
                    elif event.key == pygame.K_LEFT:
                        has_key, game_over, next_level, player_under_tile = move_player(
                            grid, -1, 0, has_key, player_under_tile
                        )
                    elif event.key == pygame.K_RIGHT:
                        has_key, game_over, next_level, player_under_tile = move_player(
                            grid, 1, 0, has_key, player_under_tile
                        )

                    # Avançar de nivell
                    if next_level:
                        level += 1
                        has_key = False
                        grid, player_under_tile = generate_new_map(level, current_algorithm)

        # Renderitzat
        screen.fill((0, 0, 0))
        draw_grid(screen, grid)
        draw_hud(screen, font, has_key, level, current_algorithm)

        # Mostrar pantalla de Game Over
        if game_over:
            draw_game_over(screen, game_over_font)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()