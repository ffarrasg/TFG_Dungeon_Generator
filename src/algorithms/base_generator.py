from abc import ABC, abstractmethod

class BaseGenerator(ABC):
    """
    Aquesta classe defineix la interfície comuna que han de seguir tots
    els generadors de mapes (Random Walk, BSP, Cellular Automata, etc.).
    """

    def __init__(self, width: int, height: int):
        """
        Inicialitza el generador amb les dimensions del mapa.

        :param width: amplada del mapa (nombre de cel·les)
        :param height: alçada del mapa (nombre de cel·les)
        """
        self.width = width
        self.height = height

    @abstractmethod
    def generate(self):
        pass