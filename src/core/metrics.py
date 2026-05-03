import time
from config import WALKABLE_TILES


def measure_generation_time(generator):
    """
    Mesura el temps de generació d'un mapa.

    Aquesta funció executa l'algoritme de generació i calcula
    el temps que triga a produir el mapa.

    :param generator: instància d'un algoritme de generació
    :return: (mapa generat, temps en segons)
    """
    start = time.perf_counter()
    grid = generator.generate()
    end = time.perf_counter()

    return grid, end - start


def walkable_percentage(grid):
    """
    Calcula el percentatge de cel·les transitables dins del mapa.

    Aquesta mètrica permet avaluar com d'obert o tancat és un mapa,
    cosa que pot influir en la jugabilitat.

    :param grid: mapa en forma de graella
    :return: valor entre 0 i 1 que indica el percentatge de cel·les transitables
    """
    total = len(grid) * len(grid[0])

    walkable = sum(
        1 for row in grid for cell in row if cell in WALKABLE_TILES
    )

    return walkable / total if total > 0 else 0