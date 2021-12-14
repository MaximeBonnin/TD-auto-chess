# ------------------- Import -------------------

# https://www.pygame.org/docs/
# https://www.youtube.com/watch?v=jO6qQDNa2UY

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
UNIT_LIST =[]
TOWER_LIST = []


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
        "atk_speed": 3,     # alle 3 sekunden angreifen?
        "dmg": 3,
        "hp": 10,           # können Türme angegriffen werden?
        "range": 500
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
        

class Tower:
    # Class that describes towers
    def __init__(self, towerType, tile):
        print(f"Tower of type {towerType} spawned!")
        self.towerType = towerType
        self.tile = tile
        self.kills = 0      # Zählen von kills für stats oder lvl system?

        global TOWER_LIST   # eig schlechte Lösung aber erstmal so: Globale variable mit allen Türmen
        TOWER_LIST.append(self)


    def aim(self, unitList):
        # kürzeste distanz von unit
        m = self.tile.rect.center
        closest = 1000      # initialize var? vlt anderer wert
        distance = 1000
        target = False
        for u in unitList:
            m_u = u.tile.rect.center
            distance = ((m[0]-m_u[0])**2 + (m[1]-m_u[1]))**(1/2) # a^2+b^2 = c^2
            if distance <= closest:
                closest = distance
                target = u
        return target, distance


    def shoot(self, unitList):
        target, distance = self.aim(unitList)
        last = 0
        cooldown = TOWER_TYPES[self.towerType]["atk_speed"]*1000
        now = pygame.time.get_ticks()
        #print(now-last)

        if distance <= TOWER_TYPES[self.towerType]["range"] and (now - last) >= cooldown:
            # TODO shoot them
            print(f"shooting at {target.unitType}")
            last = pygame.time.get_ticks()
        


class Unit:
    # Class that describes units
    def __init__(self, unitType, tile):
        print(f"Unit of type {unitType} spawned!")
        self.unitType = unitType
        self.lvl = 1
        self.tile = tile

        global TOWER_LIST   # eig schlechte Lösung aber erstmal so: Globale variable mit allen Units
        UNIT_LIST.append(self)


class Tile:
    # Class that describes the map tiles
    def __init__(self, tileType, position):
        self.tileType = tileType
        self.position = position

        if self.tileType == 0:
            self.color = COLORS["black"]
        elif self.tileType == 1:
            self.color = COLORS["green"]
        else:
            print("Tile Type Error")

        self.rect = pygame.Rect(self.position, TILE_SIZE)
        self.surface = pygame.Surface(TILE_SIZE)
        self.surface.fill(self.color)

        self.has_unit = False
        self.has_tower = False
    

    def spawn_tower(self, towerType):
        if self.tileType == 1:
            print("This is a path, you cannot place towers here.")
        elif self.has_tower:
            print("This tile already has a tower on it.")
        else:
            self.has_tower = Tower(towerType, self)
            self.color = COLORS["blue"]
            self.surface.fill(self.color)
            

    def spawn_unit(self, unitType):
        if self.tileType == 0:
            print("This is a wall, you cannot place units here.")
        elif self.has_unit:
            print("This tile already has a unit on it.")
        else:
            self.has_unit = Unit(unitType, self)
            self.color = COLORS["red"]
            self.surface.fill(self.color)
            


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

    # Draw all map tiles
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
                if event.button == 1:       # linksclick spawnt turm
                    for c in mapTileList:
                        for i in c:
                            if i.rect.collidepoint(mouse.get_pos()[0], mouse.get_pos()[1]):
                                i.spawn_tower("basic")
                elif event.button == 3:     # rechtcklick spawn unit
                    for c in mapTileList:
                        for i in c:
                            if i.rect.collidepoint(mouse.get_pos()[0], mouse.get_pos()[1]):
                                i.spawn_unit("basic")


        # Testing
        for t in TOWER_LIST:
            t.shoot(UNIT_LIST)
        # Testing end

        draw_window(mapTileList)    
    pygame.quit()


# ------------------- Save for multiple files being executed -------------------
if __name__ == "__main__":
    main()
