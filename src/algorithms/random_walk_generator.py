import random
from src.algorithms.base_generator import BaseGenerator
from config import WALL, FLOOR


class RandomWalkGenerator(BaseGenerator):
    """
    Implementació de l'algoritme Random Walk.

    Aquest algoritme genera mapes a partir del moviment aleatori d'un punt
    dins del mapa, que va "excavant" camins convertint murs en terra.
    """

    def generate(self):
        """
        Genera un mapa utilitzant un recorregut aleatori.
        """
        # Inicialment, tot el mapa és mur
        grid = [[WALL for _ in range(self.width)] for _ in range(self.height)]

        # Es comença des del centre del mapa
        x = self.width // 2
        y = self.height // 2

        # Es marca la posició inicial com a terra
        grid[y][x] = FLOOR

        # Nombre de passos que farà el recorregut aleatori
        # (aproximadament la meitat del mapa)
        steps = (self.width * self.height) // 2

        for _ in range(steps):
            # Es tria una direcció aleatòria (dreta, esquerra, amunt, avall)
            dx, dy = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])

            # Es calcula la nova posició, limitant-la per no sortir del mapa
            x = max(1, min(self.width - 2, x + dx))
            y = max(1, min(self.height - 2, y + dy))

            # Es "carva" el camí convertint la cel·la en terra
            grid[y][x] = FLOOR

        return grid