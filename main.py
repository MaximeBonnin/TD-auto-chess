# ------------------- Import -------------------

# https://www.pygame.org/docs/

import pygame
import math
import random
import os


# ------------------- Global Variables -------------------

WIDTH, HEIGHT = 32*20, 32*20
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
FPS = 60
TILE_SIZE = (32, 32)
NUM_TILES = (WIDTH//TILE_SIZE[0], HEIGHT//TILE_SIZE[1]) # numbers of tiles as tuple (columns, rows)

COLORS = {
    "black": (0, 0, 0),
    "white": (255, 255, 255),
    "red": (255, 0, 0),
    "yellow": (255, 255, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255)
}

TOWER_TYPES = {
    "basic": {
        "atk_speed": 1,
        "dmg": 1,
        "hp": 10            # können Türme angegriffen werden?
    },
    "AoE": "info",
    "SingleTarget": "info"
}

UNIT_TYPES = {
    "basic": {
        "move_speed": 1,
        "hp": 10,
        "size": 1,          # verschieden große units?
        "special": False    # vlt für sowas wie Schilde oder andere abilities?
    },
    "fast": "info",
    "tank": "info"
}


# ------------------- Initiallize -------------------

pygame.display.set_caption("Tower Defence Game")


# ------------------- CLASSES -------------------

class Tile:
    # Class that describes the map tiles
    def __init__(self, type,position):
        self.type = type
        self.position = position

        if self.type == 0:
            self.color = COLORS["black"]
        else:
            self.color = COLORS["green"]

        self.rect = pygame.Rect(self.position, TILE_SIZE)
        self.surface = pygame.Surface(TILE_SIZE)
        self.surface.fill(self.color)
        

class Tower:
    # Class that describes towers
    def __init__(self, type, lvl):
        self.type = type
        self.lvl = lvl 
        self.kills = 0      # Zählen von kills für stats oder lvl system?

class Unit:
    # Class that describes units
    def __init__(self, type, lvl):
        self.type = type
        self.lvl = lvl


# ------------------- FUNCTIONS -------------------

def make_map(tiles):
    colums, rows = tiles
    tile_list = []
    for c in range(colums):
        c_list = []
        for r in range(rows):
            t = Tile(random.randint(0, 1), (c*TILE_SIZE[0], r*TILE_SIZE[1]))
            c_list.append(t)
        tile_list.append(c_list)

    return tile_list


def draw_window(tile_list):
    # Function that draws everything on screen (every frame)

    WIN.fill(COLORS["white"])

    for c in tile_list:
        for r in c:
            WIN.blit(r.surface, r.rect)

    pygame.display.update()


# ------------------- Main Game Loop -------------------

def main():
    mapTileList = make_map(NUM_TILES) 
    clock = pygame.time.Clock()

    run = True
    while run:
        clock.tick(FPS)
        # vlt ersttmal nen Menü? aber kann später kommen
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        draw_window(mapTileList)    
    pygame.quit()


# ------------------- Save for multiple files being executed -------------------
if __name__ == "__main__":
    main()
