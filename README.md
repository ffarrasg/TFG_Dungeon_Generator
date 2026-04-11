# TFG Dungeon Generator

Aquest projecte forma part del Treball Final de Grau i consisteix en el desenvolupament d’un prototip 2D per analitzar i comparar diferents algoritmes de generació procedural de mapes de tipus *dungeon*.

## Objectiu

L’objectiu principal del projecte és comparar diferents algoritmes de generació procedural aplicats a la creació de mapes de tipus *dungeon* en videojocs. El prototip permet generar mapes amb diferents algoritmes i avaluar aspectes com la seva estructura, la jugabilitat i la distribució d’elements dins del nivell.

## Algoritmes implementats

Actualment el projecte inclou els següents algoritmes:

- Random Walk
- Binary Space Partitioning (BSP)
- Cellular Automata

## Funcionalitats actuals

El prototip inclou:

- Generació procedural de mapes
- Diferents tipus de terreny:
  - herba
  - roca
  - terra
  - aigua
- Col·locació de jugador, clau, sortida i enemics
- Sistema de nivells
- Validació bàsica dels mapes generats
- Canvi d’algoritme durant l’execució

## Requisits

- Python 3.12
- Pygame 2.6.1

## Instal·lació

1. Clonar el repositori:

<bash>
git clone https://github.com/EL_TEU_USUARI/TFG_Dungeon_Generator.git
cd TFG_Dungeon_Generator

2. Crear i activar entorn virtual:

<bash>
python -m venv .venv
.venv\Scripts\activate

3. Instal·lar dependències:

pip install -r requirements.txt

4. Executar projecte:

<bash>
python main.py

## Controls

- Fletxes: Moviment
- A: Canvi d'algoritme
- R: Reset

## Autor
Francesc Farràs Garcia (ffarrasg)
