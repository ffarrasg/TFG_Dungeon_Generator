import time
from config import GRASS, ROCK, DIRT, PLAYER, EXIT, KEY, ENEMY


def measure_generation_time(generator):
    """
    Mesura el temps de generació d'un mapa.

    Aquesta funció executa l'algoritme de generació i calcula
    el temps que triga a produir el mapa.

    :param generator: instància d'un algoritme de generació
    :return: (mapa generat, temps en segons)
    """
    start = time.perf_counter()      # inici de la mesura
    grid = generator.generate()      # generació del mapa
    end = time.perf_counter()        # final de la mesura

    return grid, end - start         # es retorna el mapa i el temps


def walkable_percentage(grid):
    """
    Calcula el percentatge de cel·les transitables dins del mapa.

    Aquesta mètrica permet avaluar com d'obert o tancat és un mapa,
    cosa que pot influir en la jugabilitat.

    :param grid: mapa en forma de graella
    :return: valor entre 0 i 1 que indica el percentatge de cel·les transitables
    """
    # Conjunt de cel·les considerades transitables
    walkable_tiles = {GRASS, ROCK, DIRT, PLAYER, EXIT, KEY, ENEMY}

    # Nombre total de cel·les del mapa
    total = len(grid) * len(grid[0])

    # Comptador de cel·les transitables
    walkable = sum(
        1 for row in grid for cell in row if cell in walkable_tiles
    )

    # Es retorna el percentatge (evitant divisió per zero)
    return walkable / total if total > 0 else 0