import pygame
from config import TILE_SIZE, WALL, GRASS, ROCK, DIRT, WATER, PLAYER, EXIT, KEY, ENEMY


def draw_grid(screen, grid):
    """
    Dibuixa el mapa complet a la pantalla.

    Cada cel·la de la graella es representa com un rectangle amb un color
    diferent segons el tipus de terreny o element que contingui.
    """
    for y, row in enumerate(grid):
        for x, cell in enumerate(row):

            # Definició del rectangle que representa la cel·la
            rect = pygame.Rect(
                x * TILE_SIZE,
                y * TILE_SIZE,
                TILE_SIZE,
                TILE_SIZE
            )

            # Assignació de colors segons el tipus de cel·la
            if cell == WALL:
                color = (40, 40, 40)          # mur (no transitable)

            elif cell == GRASS:
                color = (70, 160, 70)         # herba

            elif cell == ROCK:
                color = (180, 180, 180)       # roca

            elif cell == DIRT:
                color = (130, 90, 50)         # terra

            elif cell == WATER:
                color = (50, 110, 220)        # aigua (obstacle)

            elif cell == PLAYER:
                color = (170, 80, 220)        # jugador (violeta)

            elif cell == EXIT:
                color = (255, 255, 255)       # sortida (blanc)

            elif cell == KEY:
                color = (255, 220, 0)         # clau

            elif cell == ENEMY:
                color = (200, 50, 50)         # enemic

            else:
                # Color de debug per detectar errors
                color = (255, 0, 255)

            # Dibuix de la cel·la
            pygame.draw.rect(screen, color, rect)

            # Dibuix del contorn de la cel·la (grid visual)
            pygame.draw.rect(screen, (25, 25, 25), rect, 1)


def draw_hud(screen, font, has_key, level, algorithm_name):
    """
    Dibuixa la interfície d'usuari (HUD) a la part superior de la pantalla.

    Mostra informació rellevant del joc:
    - Si el jugador té la clau
    - Nivell actual
    - Algoritme utilitzat
    - Controls bàsics
    """
    hud_text = (
        f"Key: {1 if has_key else 0}   "
        f"Level: {level}   "
        f"Alg: {algorithm_name}   "
        f"A: Change   R: Reset"
    )

    text_surface = font.render(hud_text, True, (255, 255, 255))

    # Es dibuixa a la part superior esquerra
    screen.blit(text_surface, (10, 10))


def draw_game_over(screen, font):
    """
    Mostra el missatge de GAME OVER al centre de la pantalla.

    Aquesta funció s'utilitza quan el jugador entra en contacte amb un enemic.
    """
    text_surface = font.render("GAME OVER", True, (255, 60, 60))

    # Centrat del text a la pantalla
    rect = text_surface.get_rect(
        center=(screen.get_width() // 2, screen.get_height() // 2)
    )

    screen.blit(text_surface, rect)