# ------------------- Import -------------------

# https://www.pygame.org/docs/

import pygame
import math
import random
import os

from pygame import mouse


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
    def __init__(self, type, position):
        self.type = type
        self.position = position

        if self.type == 0:
            self.color = COLORS["black"]
        elif self.type == 1:
            self.color = COLORS["green"]
        else:
            print("Tile Type Error")

        self.rect = pygame.Rect(self.position, TILE_SIZE)
        self.surface = pygame.Surface(TILE_SIZE)
        self.surface.fill(self.color)

        self.has_unit = False
    
    def spawn_tower(self, type):
        self.has_unit = True
        self.color = COLORS["blue"]
        self.surface.fill(self.color)
        # TODO spawn units
        

class Tower:
    # Class that describes towers
    def __init__(self, type, lvl, tile):
        self.type = type
        self.lvl = lvl 
        self.tile = tile
        self.kills = 0      # Zählen von kills für stats oder lvl system?

class Unit:
    # Class that describes units
    def __init__(self, type, lvl, tile):
        self.type = type
        self.lvl = lvl
        self.tile = tile


# ------------------- FUNCTIONS -------------------

def make_map(tiles):
    colums, rows = tiles
    tile_list = []
    i = 0
    for c in range(colums):
        c_list = []
        for r in range(rows):
            if i == NUM_TILES[0]//2:
                t = Tile(1, (c*TILE_SIZE[0], r*TILE_SIZE[1]))
            else:
                t = Tile(0, (c*TILE_SIZE[0], r*TILE_SIZE[1]))
            c_list.append(t)
        tile_list.append(c_list)
        i += 1

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
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for c in mapTileList:
                    for i in c:
                        if i.rect.collidepoint(mouse.get_pos()[0], mouse.get_pos()[1]):
                            i.spawn_tower(1)

        draw_window(mapTileList)    
    pygame.quit()


# ------------------- Save for multiple files being executed -------------------
if __name__ == "__main__":
    main()
