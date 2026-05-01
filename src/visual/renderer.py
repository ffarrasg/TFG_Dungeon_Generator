import pygame
import math
from config import TILE_SIZE, HUD_HEIGHT, WALL, GRASS, ROCK, DIRT, WATER, PLAYER, EXIT, KEY, ENEMY


def draw_base_tile(screen, rect, cell):
    """
    Dibuixa el terreny base d'una cel·la.
    """
    if cell == WALL:
        color = (35, 35, 35)
    elif cell == GRASS:
        color = (70, 150, 70)
    elif cell == ROCK:
        color = (170, 170, 170)
    elif cell == DIRT:
        color = (130, 90, 55)
    elif cell == WATER:
        color = (45, 105, 210)
    else:
        color = (130, 90, 55)

    pygame.draw.rect(screen, color, rect)


def draw_player(screen, rect):
    """
    Dibuixa el jugador amb una forma humana simple.
    """
    pygame.draw.circle(
        screen,
        (240, 210, 180),
        (rect.centerx, rect.y + TILE_SIZE // 4),
        TILE_SIZE // 7
    )

    pygame.draw.rect(
        screen,
        (170, 80, 220),
        pygame.Rect(
            rect.centerx - TILE_SIZE // 8,
            rect.y + TILE_SIZE // 3,
            TILE_SIZE // 4,
            TILE_SIZE // 3
        )
    )

    pygame.draw.line(
        screen,
        (170, 80, 220),
        (rect.centerx, rect.y + TILE_SIZE // 1.6),
        (rect.centerx - TILE_SIZE // 6, rect.bottom - 4),
        2
    )
    pygame.draw.line(
        screen,
        (170, 80, 220),
        (rect.centerx, rect.y + TILE_SIZE // 1.6),
        (rect.centerx + TILE_SIZE // 6, rect.bottom - 4),
        2
    )


def draw_exit(screen, rect):
    """
    Dibuixa la sortida com una porta.
    """
    door_rect = pygame.Rect(
        rect.x + TILE_SIZE // 4,
        rect.y + TILE_SIZE // 6,
        TILE_SIZE // 2,
        TILE_SIZE - TILE_SIZE // 6
    )

    pygame.draw.rect(screen, (245, 245, 245), door_rect)
    pygame.draw.rect(screen, (180, 180, 180), door_rect, 2)

    pygame.draw.circle(
        screen,
        (80, 80, 80),
        (door_rect.right - 5, door_rect.centery),
        2
    )


def draw_key(screen, rect):
    """
    Dibuixa una clau simple.
    """
    key_color = (255, 220, 0)

    pygame.draw.circle(
        screen,
        key_color,
        (rect.x + TILE_SIZE // 3, rect.centery),
        TILE_SIZE // 6,
        3
    )

    pygame.draw.line(
        screen,
        key_color,
        (rect.x + TILE_SIZE // 2, rect.centery),
        (rect.right - 4, rect.centery),
        3
    )

    pygame.draw.line(
        screen,
        key_color,
        (rect.right - 8, rect.centery),
        (rect.right - 8, rect.centery + 6),
        3
    )

    pygame.draw.line(
        screen,
        key_color,
        (rect.right - 4, rect.centery),
        (rect.right - 4, rect.centery + 4),
        3
    )


def draw_enemy(screen, rect):
    """
    Dibuixa un enemic amb forma de dimoni simple.
    """
    body_color = (190, 40, 40)

    pygame.draw.circle(
        screen,
        body_color,
        rect.center,
        TILE_SIZE // 3
    )

    pygame.draw.polygon(
        screen,
        (230, 230, 230),
        [
            (rect.centerx - 7, rect.centery - 8),
            (rect.centerx - 12, rect.centery - 15),
            (rect.centerx - 3, rect.centery - 11)
        ]
    )

    pygame.draw.polygon(
        screen,
        (230, 230, 230),
        [
            (rect.centerx + 7, rect.centery - 8),
            (rect.centerx + 12, rect.centery - 15),
            (rect.centerx + 3, rect.centery - 11)
        ]
    )

    pygame.draw.circle(screen, (255, 255, 0), (rect.centerx - 5, rect.centery - 2), 2)
    pygame.draw.circle(screen, (255, 255, 0), (rect.centerx + 5, rect.centery - 2), 2)


def draw_grid(screen, grid, entity_under_tiles=None):
    """
    Dibuixa el mapa complet amb sistema de capes.

    Primer es dibuixa el terreny original de cada cel·la.
    Després es dibuixen les entitats a sobre.
    """
    if entity_under_tiles is None:
        entity_under_tiles = {}

    for y, row in enumerate(grid):
        for x, cell in enumerate(row):
            rect = pygame.Rect(
                x * TILE_SIZE,
                y * TILE_SIZE + HUD_HEIGHT,
                TILE_SIZE,
                TILE_SIZE
            )

            # Si la cel·la conté una entitat, recuperem el terreny original.
            base_cell = entity_under_tiles.get((x, y), cell)

            draw_base_tile(screen, rect, base_cell)

            if cell == PLAYER:
                draw_player(screen, rect)
            elif cell == EXIT:
                draw_exit(screen, rect)
            elif cell == KEY:
                draw_key(screen, rect)
            elif cell == ENEMY:
                draw_enemy(screen, rect)


def draw_hud(screen, font, has_key, level, algorithm_name):
    """
    Dibuixa el HUD amb informació del joc.
    """
    hud_text = (
        f"Key: {1 if has_key else 0}   "
        f"Level: {level}   "
        f"Alg: {algorithm_name}   "
        f"A: Change   R: Reset"
    )

    hud_rect = pygame.Rect(0, 0, screen.get_width(), HUD_HEIGHT)
    pygame.draw.rect(screen, (20, 20, 20), hud_rect)

    text_surface = font.render(hud_text, True, (255, 255, 255))
    screen.blit(text_surface, (10, 10))


def draw_game_over(screen, font):
    """
    Mostra la pantalla de GAME OVER amb text de reinici amb efecte fade.
    """

    # Overlay fosc
    overlay = pygame.Surface((screen.get_width(), screen.get_height()))
    overlay.set_alpha(160)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    # Text principal
    game_over_text = font.render("GAME OVER", True, (255, 60, 60))
    game_over_rect = game_over_text.get_rect(
        center=(screen.get_width() // 2, screen.get_height() // 2 - 20)
    )
    screen.blit(game_over_text, game_over_rect)

    # --- EFECTE FADE ---
    current_time = pygame.time.get_ticks()

    # valor entre 0 i 255 amb ona sinusoidal
    alpha = int((math.sin(current_time * 0.005) + 1) * 127.5)

    small_font = pygame.font.SysFont(None, 32)
    reset_text = small_font.render("Press R to Reset", True, (220, 220, 220))

    # convertir el text en superfície amb alpha
    reset_text.set_alpha(alpha)

    reset_rect = reset_text.get_rect(
        center=(screen.get_width() // 2, screen.get_height() // 2 + 25)
    )

    screen.blit(reset_text, reset_rect)

def draw_start_screen(screen, title_font, font, background_grid=None):
    """
    Mostra la pantalla inicial amb:
    - mapa generat de fons
    - títol centrat
    - objectiu
    - llegenda i controls separats a sota
    """

    # --- FONS ---
    if background_grid is not None:
        draw_grid(screen, background_grid, {})
    else:
        screen.fill((20, 20, 20))

    # Overlay fosc per millorar contrast
    overlay = pygame.Surface((screen.get_width(), screen.get_height()))
    overlay.set_alpha(150)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    center_x = screen.get_width() // 2
    center_y = screen.get_height() // 2

    # --- CAIXA CENTRAL ---
    title_box = pygame.Rect(center_x - 330, center_y - 150, 660, 220)
    pygame.draw.rect(screen, (25, 25, 25), title_box, border_radius=14)
    pygame.draw.rect(screen, (180, 180, 180), title_box, 2, border_radius=14)

    # --- TÍTOL ---
    title_text = title_font.render("DUNGEON GENERATOR", True, (255, 255, 255))
    title_shadow = title_font.render("DUNGEON GENERATOR", True, (80, 80, 80))

    title_rect = title_text.get_rect(center=(center_x, center_y - 105))
    shadow_rect = title_shadow.get_rect(center=(center_x + 3, center_y - 102))

    screen.blit(title_shadow, shadow_rect)
    screen.blit(title_text, title_rect)

    # --- AUTOR ---
    author_text = font.render("Autor: Francesc Farràs", True, (220, 220, 220))
    screen.blit(author_text, author_text.get_rect(center=(center_x, center_y - 55)))

    # --- OBJECTIU ---
    objective_1 = font.render(
        "Troba la clau, evita els enemics i arriba a la porta de sortida.",
        True,
        (235, 235, 235)
    )
    objective_2 = font.render(
        "Cada nivell es genera amb algoritmes de generació procedural.",
        True,
        (235, 235, 235)
    )

    screen.blit(objective_1, objective_1.get_rect(center=(center_x, center_y - 10)))
    screen.blit(objective_2, objective_2.get_rect(center=(center_x, center_y + 22)))

    # --- PRESS ENTER (FADE) ---
    import math
    current_time = pygame.time.get_ticks()
    alpha = int((math.sin(current_time * 0.005) + 1) * 127.5)

    start_text = font.render("Press ENTER to Start", True, (255, 220, 0))
    start_text.set_alpha(alpha)

    screen.blit(start_text, start_text.get_rect(center=(center_x, center_y + 95)))

    # =========================================================
    # --- TAULES INFERIORS ---
    # =========================================================

    table_width = 300
    table_height = 110
    margin = 40

    left_x = margin
    right_x = screen.get_width() - table_width - margin
    table_y = screen.get_height() - table_height - 20

    # ---------- LLEGENDA ----------
    legend_rect = pygame.Rect(left_x, table_y, table_width, table_height)

    pygame.draw.rect(screen, (25, 25, 25), legend_rect, border_radius=10)
    pygame.draw.rect(screen, (120, 120, 120), legend_rect, 2, border_radius=10)

    legend_title = font.render("Llegenda", True, (255, 255, 255))
    screen.blit(legend_title, (legend_rect.x + 10, legend_rect.y + 8))

    elements = [
        ("Jugador", PLAYER),
        ("Enemic", ENEMY),
        ("Clau", KEY),
        ("Porta", EXIT),
    ]

    for i, (label, tile_type) in enumerate(elements):
        x = legend_rect.x + 10 + (i % 2) * 140
        y = legend_rect.y + 35 + (i // 2) * 30

        icon_rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)

        draw_base_tile(screen, icon_rect, DIRT)

        if tile_type == PLAYER:
            draw_player(screen, icon_rect)
        elif tile_type == ENEMY:
            draw_enemy(screen, icon_rect)
        elif tile_type == KEY:
            draw_key(screen, icon_rect)
        elif tile_type == EXIT:
            draw_exit(screen, icon_rect)

        label_text = font.render(label, True, (220, 220, 220))
        screen.blit(label_text, (x + 30, y + 4))

    # ---------- CONTROLS ----------
    controls_rect = pygame.Rect(right_x, table_y, table_width, table_height)

    pygame.draw.rect(screen, (25, 25, 25), controls_rect, border_radius=10)
    pygame.draw.rect(screen, (120, 120, 120), controls_rect, 2, border_radius=10)

    controls_title = font.render("Controls", True, (255, 255, 255))
    screen.blit(controls_title, (controls_rect.x + 10, controls_rect.y + 8))

    controls = [
        ("Fletxes", "Moure"),
        ("A", "Canvi algoritme"),
        ("R", "Reset"),
    ]

    for i, (key, action) in enumerate(controls):
        y = controls_rect.y + 35 + i * 25

        key_text = font.render(key, True, (255, 220, 0))
        action_text = font.render(action, True, (220, 220, 220))

        screen.blit(key_text, (controls_rect.x + 10, y))
        screen.blit(action_text, (controls_rect.x + 110, y))