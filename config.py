# Dimensions del mapa (en nombre de cel·les)
MAP_WIDTH = 40
MAP_HEIGHT = 25

# Mida de cada cel·la en píxels
TILE_SIZE = 24

# Dimensions de la finestra del joc (en píxels)
SCREEN_WIDTH = MAP_WIDTH * TILE_SIZE
HUD_HEIGHT = 40
SCREEN_HEIGHT = MAP_HEIGHT * TILE_SIZE + HUD_HEIGHT

# Frames per segon (velocitat d'actualització del joc)
FPS = 30


# --- Tipus de cel·les (tiles) ---
# Cada valor representa un tipus de terreny o element dins del mapa

WALL = 0      # Mur (no transitable)
GRASS = 1     # Herba (transitable)
ROCK = 2      # Roca (transitable)
DIRT = 3      # Terra (transitable)
WATER = 4     # Aigua (no transitable)

PLAYER = 5    # Posició del jugador
EXIT = 6      # Sortida del nivell
KEY = 7       # Clau necessària per completar el nivell
ENEMY = 8     # Enemic (no transitable)

FLOOR = 9     # Terra base utilitzada pels algoritmes abans d'aplicar textures


# --- Algoritmes de generació disponibles ---
# Llista dels algoritmes implementats al prototip

ALGORITHMS = ["random_walk", "bsp", "cellular"]

# Algoritme seleccionat per defecte en iniciar el joc
DEFAULT_ALGORITHM = "random_walk"


# --- Definició de cel·les transitables ---
# Aquestes estructures s'utilitzen per determinar per on pot moure's el jugador
# i per calcular camins dins del mapa

# Terrenys transitables (sense incloure elements del joc)
WALKABLE_TERRAINS = {GRASS, ROCK, DIRT}

# Totes les cel·les considerades transitables (incloent objectes i jugador)
WALKABLE_TILES = {GRASS, ROCK, DIRT, PLAYER, EXIT, KEY, ENEMY}

# Totes les cel·les considerades transitables per afegir objectes (jugador, sortida, clau)
WALKABLE_OBJECT_PLACEMENT = WALKABLE_TERRAINS | {PLAYER, EXIT, KEY}

# Tiles transitables per validació de camins
PASSABLE_BEFORE_KEY = {GRASS, ROCK, DIRT, PLAYER, KEY}
PASSABLE_AFTER_KEY = {GRASS, ROCK, DIRT, PLAYER, EXIT, KEY}
PASSABLE_FOR_PATH = {GRASS, ROCK, DIRT, PLAYER, EXIT, KEY}

BLOCKING_TILES = {WALL, WATER}
DANGER_TILES = {ENEMY}