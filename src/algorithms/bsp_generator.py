import random
from src.algorithms.base_generator import BaseGenerator
from config import WALL, FLOOR


class BSPNode:
    """
    Representa un node de l'arbre BSP.

    Cada node defineix una regió rectangular del mapa.
    Aquesta regió es pot dividir en dues subregions i, en les fulles finals,
    s'hi pot generar una habitació.
    """
    def __init__(self, x, y, width, height):
        self.x = x                  # coordenada X inicial de la regió
        self.y = y                  # coordenada Y inicial de la regió
        self.width = width          # amplada de la regió
        self.height = height        # alçada de la regió
        self.left = None            # subregió esquerra o superior
        self.right = None           # subregió dreta o inferior
        self.room = None            # habitació associada al node, si n'hi ha


class BSPGenerator(BaseGenerator):
    """
    Implementació de l'algoritme Binary Space Partitioning (BSP).

    Aquest algoritme divideix recursivament l'espai disponible en diverses
    regions més petites. A cada regió final s'hi crea una habitació, i
    posteriorment aquestes habitacions es connecten mitjançant passadissos.
    """
    def __init__(self, width: int, height: int, min_leaf_size=8, min_room_size=4):
        super().__init__(width, height)

        # Mida mínima d'una regió per poder-se dividir
        self.min_leaf_size = min_leaf_size

        # Mida mínima de les habitacions que es generaran
        self.min_room_size = min_room_size

        # Llista de totes les habitacions creades
        self.rooms = []

    def generate(self):
        """
        Genera el mapa complet utilitzant BSP.
        """
        # Inicialment, tot el mapa és mur
        grid = [[WALL for _ in range(self.width)] for _ in range(self.height)]
        self.rooms = []

        # Node arrel que ocupa gairebé tot el mapa,
        # deixant un petit marge exterior
        root = BSPNode(1, 1, self.width - 2, self.height - 2)
        leaves = [root]

        # Es van dividint les regions mentre sigui possible
        did_split = True
        while did_split:
            did_split = False
            new_leaves = []

            for leaf in leaves:
                # Només es divideixen les regions que encara no tenen fills
                if leaf.left is None and leaf.right is None:
                    # Es decideix si val la pena intentar dividir la regió
                    if (
                        leaf.width > self.min_leaf_size * 2
                        or leaf.height > self.min_leaf_size * 2
                        or random.random() > 0.3
                    ):
                        if self._split_leaf(leaf):
                            # Si la divisió té èxit, s'afegeixen les noves subregions
                            new_leaves.append(leaf.left)
                            new_leaves.append(leaf.right)
                            did_split = True
                        else:
                            new_leaves.append(leaf)
                    else:
                        new_leaves.append(leaf)
                else:
                    new_leaves.append(leaf)

            leaves = new_leaves

        # Un cop construït l'arbre, es creen les habitacions
        self._create_rooms(root, grid)

        # Finalment, es connecten les habitacions
        self._connect_rooms(root, grid)

        return grid

    def _split_leaf(self, leaf):
        """
        Intenta dividir una regió en dues subregions.
        La divisió pot ser horitzontal o vertical.
        """
        # Inicialment es tria aleatòriament el tipus de divisió
        split_h = random.choice([True, False])

        # Si la regió és molt més ampla que alta, es força divisió vertical
        if leaf.width / leaf.height >= 1.25:
            split_h = False

        # Si la regió és molt més alta que ampla, es força divisió horitzontal
        elif leaf.height / leaf.width >= 1.25:
            split_h = True

        # Es calcula la mida màxima possible de la divisió
        max_size = (leaf.height if split_h else leaf.width) - self.min_leaf_size

        # Si no hi ha prou espai, no es pot dividir
        if max_size <= self.min_leaf_size:
            return False

        # Es tria el punt concret de divisió
        split = random.randint(self.min_leaf_size, max_size)

        # Divisió horitzontal
        if split_h:
            leaf.left = BSPNode(leaf.x, leaf.y, leaf.width, split)
            leaf.right = BSPNode(leaf.x, leaf.y + split, leaf.width, leaf.height - split)

        # Divisió vertical
        else:
            leaf.left = BSPNode(leaf.x, leaf.y, split, leaf.height)
            leaf.right = BSPNode(leaf.x + split, leaf.y, leaf.width - split, leaf.height)

        return True

    def _create_rooms(self, node, grid):
        """
        Recorre l'arbre BSP i crea una habitació a cada node fulla.
        """
        # Si el node té fills, es continua recorrent recursivament
        if node.left or node.right:
            if node.left:
                self._create_rooms(node.left, grid)
            if node.right:
                self._create_rooms(node.right, grid)

        # Si és una fulla final, s'hi crea una habitació
        else:
            # Es calcula una mida aleatòria per a l'habitació
            room_width = random.randint(self.min_room_size, max(self.min_room_size, node.width - 2))
            room_height = random.randint(self.min_room_size, max(self.min_room_size, node.height - 2))

            # Es calcula una posició aleatòria dins de la regió
            room_x = random.randint(node.x, node.x + max(0, node.width - room_width))
            room_y = random.randint(node.y, node.y + max(0, node.height - room_height))

            # Es desa la informació de l'habitació
            node.room = (room_x, room_y, room_width, room_height)
            self.rooms.append(node.room)

            # Es dibuixa l'habitació al mapa
            for y in range(room_y, room_y + room_height):
                for x in range(room_x, room_x + room_width):
                    grid[y][x] = FLOOR

    def _connect_rooms(self, node, grid):
        """
        Connecta les habitacions dels subarbres mitjançant passadissos.
        """
        if node.left and node.right:
            self._connect_rooms(node.left, grid)
            self._connect_rooms(node.right, grid)

            # Es recupera una habitació representativa de cada costat
            left_room = self._get_room(node.left)
            right_room = self._get_room(node.right)

            # Si existeixen les dues, es connecten pels seus centres
            if left_room and right_room:
                x1, y1 = self._room_center(left_room)
                x2, y2 = self._room_center(right_room)
                self._create_corridor(grid, x1, y1, x2, y2)

    def _get_room(self, node):
        """
        Retorna una habitació associada a un node.
        Si el node no té habitació directa, la cerca als seus fills.
        """
        if node.room:
            return node.room

        left_room = self._get_room(node.left) if node.left else None
        right_room = self._get_room(node.right) if node.right else None

        # Si només hi ha una habitació en un dels costats, es retorna aquesta
        if left_room and not right_room:
            return left_room
        if right_room and not left_room:
            return right_room

        # Si n'hi ha dues, se'n tria una aleatòriament
        if left_room and right_room:
            return random.choice([left_room, right_room])

        return None

    def _room_center(self, room):
        """
        Calcula el centre d'una habitació.
        """
        x, y, w, h = room
        return x + w // 2, y + h // 2

    def _create_corridor(self, grid, x1, y1, x2, y2):
        """
        Crea un passadís en forma de L entre dos punts.
        Es decideix aleatòriament si es fa primer el tram horitzontal
        o el tram vertical.
        """
        if random.choice([True, False]):
            self._carve_h_corridor(grid, x1, x2, y1)
            self._carve_v_corridor(grid, y1, y2, x2)
        else:
            self._carve_v_corridor(grid, y1, y2, x1)
            self._carve_h_corridor(grid, x1, x2, y2)

    def _carve_h_corridor(self, grid, x1, x2, y):
        """
        Excava un passadís horitzontal entre dues coordenades X.
        """
        for x in range(min(x1, x2), max(x1, x2) + 1):
            grid[y][x] = FLOOR

    def _carve_v_corridor(self, grid, y1, y2, x):
        """
        Excava un passadís vertical entre dues coordenades Y.
        """
        for y in range(min(y1, y2), max(y1, y2) + 1):
            grid[y][x] = FLOOR