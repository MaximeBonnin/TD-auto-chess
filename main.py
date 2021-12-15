#
#  ------------------- Import -------------------

# https://www.pygame.org/docs/
# https://www.youtube.com/watch?v=jO6qQDNa2UY

import pygame
import math
import random
import os

from pygame import mouse

# ------------------- Initiallize -------------------

pygame.display.set_caption("Tower Defence Game")

pygame.mixer.init()
pew = pygame.mixer.Sound(os.path.join("Assets","Sound","pew.wav"))
pew.set_volume(0.1)
hit = pygame.mixer.Sound(os.path.join("Assets","Sound","hit.mp3"))
hit.set_volume(0.2)
explosion = pygame.mixer.Sound(os.path.join("Assets","Sound","explosion.wav"))
explosion.set_volume(0.4)


# ------------------- Global Variables -------------------

WIDTH, HEIGHT = 32*20, 32*20
MENU_W, MENU_H = 128, HEIGHT
WIN = pygame.display.set_mode((WIDTH+MENU_W, HEIGHT))
FPS = 60
TILE_SIZE = (32, 32)
PROJ_SIZE = (4, 4)
NUM_TILES = (WIDTH//TILE_SIZE[0], HEIGHT//TILE_SIZE[1]) # numbers of tiles as tuple (columns, rows)
UNIT_LIST =[]
TOWER_LIST = []
PROJ_LIST = []

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
        "atk_speed": 1.5,     # alle 3 sekunden angreifen?
        "dmg": 3,
        "hp": 10,           # können Türme angegriffen werden?
        "range": 300,
        "proj_type": "basic"
    },
    "AoE": "info",
    "SingleTarget": "info"
}

UNIT_TYPES = {
    "basic": {
        "move_speed": 1,
        "hp": 10,
        "size": (16, 16),          # verschieden große units?
        "special": False    # vlt für sowas wie Schilde oder andere abilities?
    },
    "fast": "info",
    "tank": "info"
}

PROJ_TYPES = {
    "basic": {
        "dmg": 3,
        "speed": 20,
        "spread": 1, # ???
        "AoE": False,
        "AoE_area": 0
    }
}


# ------------------- CLASSES -------------------

class Projectile:
    def __init__(self, projType, origin, target):
        self.projType = projType
        self.origin = origin
        self.target = target
        self.x, self.y = origin.tile.rect.center
        self.color = COLORS["white"] # verschiedene Farben?
        self.last_move = pygame.time.get_ticks()

        self.rect = pygame.Rect(origin.tile.rect.center, PROJ_SIZE) #TODO spawn ist nicht mittig
        self.surface = pygame.Surface(PROJ_SIZE)
        self.surface.fill(self.color)

        self.angle = math.atan2(self.target.rect.centery - self.origin.tile.rect.centery, self.target.rect.centerx - self.origin.tile.rect.centerx)
        self.dx = math.cos(self.angle)*PROJ_TYPES[self.projType]["speed"]
        self.dy = math.sin(self.angle)*PROJ_TYPES[self.projType]["speed"]

        global PROJ_LIST
        PROJ_LIST.append(self)    

    def check_hit(self):
        for unit in UNIT_LIST:
            if unit.rect.colliderect(self.rect):
                unit.take_dmg(PROJ_TYPES[self.projType]["dmg"])
                PROJ_LIST.remove(self)
                return
            elif self.x < 0 or self.x > WIDTH:
                PROJ_LIST.remove(self)
                return
            elif self.y < 0 or self.y > HEIGHT:
                PROJ_LIST.remove(self)
                return

    def move(self):
        now = pygame.time.get_ticks()
        if now - self.last_move >= 15: #15ms warten bis nächste bewegeung
            self.x = self.x + self.dx
            self.y = self.y + self.dy

            self.rect.x = int(self.x)
            self.rect.y = int(self.y)

            self.last_move = pygame.time.get_ticks()

            self.check_hit()
            
                
class Tower:
    # Class that describes towers
    def __init__(self, towerType, tile):
        print(f"Tower of type {towerType} spawned!")
        self.towerType = towerType
        self.tile = tile
        self.last_shot = pygame.time.get_ticks()
        self.kills = 0      # Zählen von kills für stats oder lvl system?

        global TOWER_LIST   # eig schlechte Lösung aber erstmal so: Globale variable mit allen Türmen
        TOWER_LIST.append(self)

    def aim(self, unitList):
        # kürzeste distanz von unit
        m = self.tile.rect.center
        target = False
        distance_list = []
    
        for u in unitList:
            m_u = u.rect.center
            distance = ((m[0]-m_u[0])**2 + (m[1]-m_u[1])**2)**(1/2) # a^2+b^2 = c^2
            distance_list.append(distance)

        distance = min(distance_list)
        target = UNIT_LIST[distance_list.index(min(distance_list))]

        return target, distance

    def shoot(self, unitList):
        if unitList:
            target, distance = self.aim(unitList)
            cooldown = TOWER_TYPES[self.towerType]["atk_speed"]*1000
            now = pygame.time.get_ticks()

            if distance <= TOWER_TYPES[self.towerType]["range"] and (now - self.last_shot) >= cooldown:
                pew.play()
                Projectile(TOWER_TYPES[self.towerType]["proj_type"], self, target)
                self.last_shot = pygame.time.get_ticks()
        

class Unit:
    # Class that describes units
    def __init__(self, unitType, tile):
        print(f"Unit of type {unitType} spawned!")
        self.unitType = unitType
        self.lvl = 1
        self.tile = tile
        self.hp = UNIT_TYPES[self.unitType]["hp"]

        self.x = self.tile.rect.x + UNIT_TYPES[self.unitType]["size"][0]/2
        self.y = self.tile.rect.y + UNIT_TYPES[self.unitType]["size"][1]/2
        self.rect = pygame.Rect((self.x, self.y), UNIT_TYPES[self.unitType]["size"])
        self.color = COLORS["yellow"]
        self.surface = pygame.Surface(UNIT_TYPES[self.unitType]["size"])
        self.surface.fill(self.color)

        global TOWER_LIST   # eig schlechte Lösung aber erstmal so: Globale variable mit allen Units
        UNIT_LIST.append(self)
    
    def die(self):
        print(f"{self.unitType} unit died.")
        explosion.play()
        UNIT_LIST.remove(self)

        self.tile.has_unit = False

        #TODO animation
    
    def take_dmg(self, amount):
        self.hp -= amount
        hit.play()
        if self.hp <= 0:
            self.die()
    
    def move(self):
        self.y += UNIT_TYPES[self.unitType]["move_speed"]
        self.rect.y = self.y

        if self.x < 0 or self.x > WIDTH: #TODO make this lose life of player
            UNIT_LIST.remove(self)
            return
        elif self.y < 0 or self.y > HEIGHT:
            UNIT_LIST.remove(self)
            return


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
        else:
            Unit(unitType, self)


class Player:
    def __init__(self, money, life):
        self.money = money
        self.hp = life

    def lose_life(self, amount):
        print(f"Player lost {amount} life.")



# ------------------- FUNCTIONS -------------------

def make_map(tiles):
    colums, rows = tiles
    print(tiles)

    #TODO make a path here? maybe import some kind of map? nodes?
    node_list = [(1, 0)]
    for y in range(rows):
        if y % 2 == 0:
            pass # skip every second row
        else:
            node_list.append((1, y))
            node_list.append((colums-2, y))
    # node_list.append() # exit?
    print(node_list)

    path_list = []
    for n in range(1, len(node_list)-1):
        prev_node = node_list[n]
        node = node_list[n]
        dx = prev_node[0] - node[0]
        dy = prev_node[1] - node[1]
        if dx > 1:
            for i in range(dx):
                pass #TODO fix this shit
        elif dy > 1:
            for i in range(dy):
                pass
        else:
            print("Difference of nodes is 1 or less")
                

    tile_list = []
    i = 0
    for c in range(colums):
        c_list = []
        for r in range(rows):
            if (c, r) in node_list:
                t = Tile(1, (c*TILE_SIZE[0], r*TILE_SIZE[1]))
            else:
                t = Tile(0, (c*TILE_SIZE[0], r*TILE_SIZE[1])) # alles wände
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
    
    for p in PROJ_LIST:
        WIN.blit(p.surface, p.rect)

    for u in UNIT_LIST:
        WIN.blit(u.surface, u.rect)

    pygame.display.update()


def update_objects():
    for t in TOWER_LIST:
        t.shoot(UNIT_LIST)
    for p in PROJ_LIST:
        p.move()
    for u in UNIT_LIST:
        u.move()
        


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
                        for tile in c:
                            if tile.rect.collidepoint(mouse.get_pos()[0], mouse.get_pos()[1]) and tile.tileType == 1:
                                Unit("basic", tile)

        update_objects()

        draw_window(mapTileList)    
    pygame.quit()


# ------------------- Save for multiple files being executed -------------------

if __name__ == "__main__":
    main()
