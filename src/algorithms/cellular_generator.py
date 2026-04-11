import random
from src.algorithms.base_generator import BaseGenerator
from config import WALL, FLOOR


class CellularGenerator(BaseGenerator):
    """
    Implementació d'un generador basat en Cellular Automata.

    Aquest algoritme parteix d'un mapa inicial aleatori i aplica diverses
    iteracions de regles locals per obtenir estructures més orgàniques,
    semblants a coves o espais naturals.
    """
    def __init__(
        self,
        width: int,
        height: int,
        fill_probability: float = 0.45,
        iterations: int = 5
    ):
        super().__init__(width, height)

        # Probabilitat inicial que una cel·la sigui mur
        self.fill_probability = fill_probability

        # Nombre d'iteracions de simulació
        self.iterations = iterations

    def generate(self):
        """
        Genera un mapa utilitzant Cellular Automata.
        """
        # Es crea una graella inicial aleatòria
        grid = self._initialize_grid()

        # Es realitzen diverses iteracions de simulació
        for _ in range(self.iterations):
            grid = self._simulate_step(grid)

        # S'obre una petita zona central per evitar mapes completament bloquejats
        self._carve_center_area(grid)

        return grid

    def _initialize_grid(self):
        """
        Inicialitza la graella amb una distribució aleatòria de murs i terra.
        """
        # Inicialment, tot el mapa és mur
        grid = [[WALL for _ in range(self.width)] for _ in range(self.height)]

        # Es generen aleatòriament les cel·les interiors
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                if random.random() > self.fill_probability:
                    grid[y][x] = FLOOR
                else:
                    grid[y][x] = WALL

        return grid

    def _simulate_step(self, grid):
        """
        Aplica una iteració de les regles de Cellular Automata.
        Cada cel·la es recalcula segons el nombre de murs veïns.
        """
        new_grid = [[WALL for _ in range(self.width)] for _ in range(self.height)]

        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                wall_count = self._count_wall_neighbors(grid, x, y)

                # Regla típica per generar coves:
                # si hi ha molts murs al voltant, la cel·la es converteix en mur;
                # si no, passa a ser terra.
                if wall_count >= 5:
                    new_grid[y][x] = WALL
                else:
                    new_grid[y][x] = FLOOR

        return new_grid

    def _count_wall_neighbors(self, grid, x, y):
        """
        Compta quants murs hi ha al voltant d'una cel·la
        considerant el seu veïnat de 8 posicions.
        """
        count = 0

        for ny in range(y - 1, y + 2):
            for nx in range(x - 1, x + 2):

                # No es compta la mateixa cel·la
                if nx == x and ny == y:
                    continue

                # Les posicions fora del mapa es consideren mur
                if nx < 0 or nx >= self.width or ny < 0 or ny >= self.height:
                    count += 1

                # També es compten les cel·les veïnes que siguin mur
                elif grid[ny][nx] == WALL:
                    count += 1

        return count

    def _carve_center_area(self, grid):
        """
        Obre una petita àrea central al mapa.

        Això ajuda a reduir la probabilitat que el mapa quedi massa tancat
        o directament impossible de jugar.
        """
        center_x = self.width // 2
        center_y = self.height // 2

        for y in range(center_y - 1, center_y + 2):
            for x in range(center_x - 1, center_x + 2):
                if 0 <= x < self.width and 0 <= y < self.height:
                    grid[y][x] = FLOOR