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

pygame.font.init()

tower_base_img = pygame.image.load(os.path.join("Assets","Images","tower_base.png"))
tower_turret_img = pygame.image.load(os.path.join("Assets","Images","tower_turret.png"))

# ------------------- Global Variables -------------------

WIDTH, HEIGHT = 32*20, 32*20
MENU_W, MENU_H = int(WIDTH*0.25), HEIGHT
WIN = pygame.display.set_mode((WIDTH+MENU_W, HEIGHT))
FPS = 60

MAIN_FONT = pygame.font.SysFont("Arial", 20)
ROUND_COOLDOWN = 15*1000 # in milliseconds

TILE_SIZE = (32, 32)
PROJ_SIZE = (4, 4)
TOWER_SIZE = (32, 32)
NUM_TILES = (WIDTH//TILE_SIZE[0], HEIGHT//TILE_SIZE[1]) # numbers of tiles as tuple (columns, rows)

UNIT_LIST =[]
TOWER_LIST = []
PROJ_LIST = []
BUTTON_LIST = []

COLORS = {
    "black": (0, 0, 0),
    "white": (255, 255, 255),
    "gray": (128, 128, 128),
    "red": (255, 0, 0),
    "yellow": (255, 255, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "dark_blue": (0, 0, 139),
    "light_blue": (173, 216, 230)
}

TOWER_TYPES = {
    "basic": {
        "atk_speed": 1,     # alle 3 sekunden angreifen?
        "cost": 15,
        "color": "blue",
        "range": 150,
        "proj_type": "basic"
    },
    "AoE": {
        "atk_speed": 1.5,     # alle 3 sekunden angreifen?
        "cost": 15,
        "color": "blue",
        "range": 150,
        "proj_type": "basic"
    },
    "singleTarget": {
        "atk_speed": 5,     # alle 3 sekunden angreifen?
        "cost": 25,
        "color": "dark_blue",
        "range": 300,
        "proj_type": "seeking"
    },
    "superFast": {
        "atk_speed": 0.2,     # alle 3 sekunden angreifen?
        "cost": 25,
        "color": "light_blue",
        "range": 100,
        "proj_type": "weak"
    }
}

UNIT_TYPES = {
    "basic": {
        "move_speed": 2,
        "hp": 10,
        "size": (16, 16),          # verschieden große units?
        "gold_value": 5,
        "special": False    # vlt für sowas wie Schilde oder andere abilities?
    },
    "fast": {
        "move_speed": 5,
        "hp": 5,
        "size": (8, 8),          # verschieden große units?
        "gold_value": 4,
        "special": False    # vlt für sowas wie Schilde oder andere abilities?
    },
    "tank": {
        "move_speed": 1,
        "hp": 25,
        "size": (28, 28),          # verschieden große units?
        "gold_value": 10,
        "special": False    # vlt für sowas wie Schilde oder andere abilities?
    }
}

PROJ_TYPES = {
    "basic": {
        "dmg": 3,
        "speed": 20,
        "spread": 1, # ???
        "AoE": False,
        "AoE_area": 0,
        "seeking": False
    },
    "seeking": {
        "dmg": 10,
        "speed": 6,
        "spread": 1, # ???
        "AoE": False,
        "AoE_area": 0,
        "seeking": True
    },
    "weak": {
        "dmg": 1,
        "speed": 50,
        "spread": 1, # ???
        "AoE": False,
        "AoE_area": 0,
        "seeking": True
    }
}

# ------------------- CLASSES -------------------

class Projectile:
    def __init__(self, projType, origin, target, player):
        self.projType = PROJ_TYPES[projType]
        self.origin = origin
        self.target = target
        self.x, self.y = origin.tile.rect.center
        self.color = COLORS["white"] # verschiedene Farben?
        self.last_move = pygame.time.get_ticks()
        self.player = player

        self.rect = pygame.Rect(origin.tile.rect.center, PROJ_SIZE) #TODO spawn ist nicht mittig
        self.surface = pygame.Surface(PROJ_SIZE)
        self.surface.fill(self.color)

        self.angle = math.atan2(self.target.rect.centery - self.origin.tile.rect.centery, self.target.rect.centerx - self.origin.tile.rect.centerx)
        self.dx = math.cos(self.angle)*self.projType["speed"]
        self.dy = math.sin(self.angle)*self.projType["speed"]

        global PROJ_LIST
        PROJ_LIST.append(self)    

    def check_hit(self):
        for unit in UNIT_LIST:
            if unit.rect.colliderect(self.rect):
                unit.take_dmg(self.projType["dmg"], self.origin)
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
        if now - self.last_move >= 5: # ms warten bis nächste bewegeung

            if self.projType["seeking"] and self.target in UNIT_LIST: 
                self.angle = math.atan2(self.target.rect.centery - self.y, self.target.rect.centerx - self.x)
                self.dx = math.cos(self.angle)*self.projType["speed"]
                self.dy = math.sin(self.angle)*self.projType["speed"]

            self.x = self.x + self.dx
            self.y = self.y + self.dy

            self.rect.x = int(self.x)
            self.rect.y = int(self.y)

            self.last_move = pygame.time.get_ticks()

            self.check_hit()
            
                
class Tower:
    # Class that describes towers
    def __init__(self, towerType, tile, player):
        self.towerType = TOWER_TYPES[towerType]
        self.tile = tile
        self.last_shot = pygame.time.get_ticks()
        self.player = player
        self.kills = 0      # Zählen von kills für stats oder lvl system?
        self.rect = self.tile.rect
        self.surface = pygame.Surface(TOWER_SIZE)
        self.inner_surface = pygame.Surface((TOWER_SIZE[0]-8, TOWER_SIZE[1]-8))
        self.inner_surface.fill(COLORS[self.towerType["color"]])
        self.surface.blit(self.inner_surface, (4, 4))
        self.surface.blit(tower_base_img, (0,0))
        self.surface.blit(tower_turret_img, (0,0))


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

        #TODO turret spin
        angle = math.atan2(target.rect.centery - self.rect.centery, target.rect.centerx - self.rect.centerx) * -180/math.pi
        print(angle)
        rotated_image = pygame.transform.rotate(tower_turret_img, angle)
        self.surface.blit(self.inner_surface, (4, 4))
        self.surface.blit(tower_base_img, (0,0))
        self.surface.blit(rotated_image, (0,0))

        return target, distance

    def shoot(self, unitList):
        if unitList:
            target, distance = self.aim(unitList)
            cooldown = self.towerType["atk_speed"]*1000
            now = pygame.time.get_ticks()

            if distance <= self.towerType["range"] and (now - self.last_shot) >= cooldown:
                pew.play()
                Projectile(self.towerType["proj_type"], self, target, self.player)
                self.last_shot = pygame.time.get_ticks()
        

class Unit:
    # Class that describes units
    def __init__(self, unitType, mapNodeHead, player):
        self.unitType = UNIT_TYPES[unitType]
        self.current_node = mapNodeHead
        self.next_node = self.current_node.next_val
        self.player = player
        self.lvl = 1
        self.max_hp = self.unitType["hp"]
        self.hp = self.unitType["hp"]

        self.random_move_modifier = random.randint(1, 10)/100

        self.x = mapNodeHead.position[0]*TILE_SIZE[0]*1.5 - self.unitType["size"][0]/2
        self.y = mapNodeHead.position[1]*TILE_SIZE[1]*1.5 + self.unitType["size"][1]/2
        self.rect = pygame.Rect((self.x, self.y), self.unitType["size"])
        self.color = COLORS["green"]
        self.surface = pygame.Surface(self.unitType["size"])
        self.surface.fill(self.color)

        global TOWER_LIST   # eig schlechte Lösung aber erstmal so: Globale variable mit allen Units
        UNIT_LIST.append(self)
    
    def die(self, origin):
        origin.kills += 1
        origin.player.money += self.unitType["gold_value"]
        explosion.play()
        UNIT_LIST.remove(self)

        #TODO animation
    
    def take_dmg(self, amount, origin):
        self.hp -= amount

        # color from green -> red based on health
        health_percent = self.hp/self.max_hp
        if health_percent < 0:
            health_percent = 0
        self.color = (int(255 * (1-health_percent)), int(255 * health_percent), 0)
        self.surface = pygame.Surface(self.unitType["size"])
        self.surface.fill(self.color)

        hit.play()
        if self.hp <= 0:
            self.die(origin)
    
    def move(self): # move to next node in path
        if self.current_node.position[0] > self.next_node.position[0]:      # move left
            self.x -= self.unitType["move_speed"]*(1 + self.random_move_modifier)
        elif self.current_node.position[0] < self.next_node.position[0]:    # move right
            self.x += self.unitType["move_speed"]*(1 + self.random_move_modifier)
        elif self.current_node.position[1] < self.next_node.position[1]:    # move down
            self.y += self.unitType["move_speed"]*(1 + self.random_move_modifier)
        else:                                                               # move up
            self.y -= self.unitType["move_speed"]*(1 + self.random_move_modifier)
        self.rect.x = self.x
        self.rect.y = self.y
        
        next_node_coords = (self.next_node.position[0]*TILE_SIZE[0] + TILE_SIZE[0]/2, self.next_node.position[1]*TILE_SIZE[1] + TILE_SIZE[1]/2)

        if self.rect.collidepoint(next_node_coords): # next node if arrived at node
            self.current_node = self.current_node.next_val
            self.next_node = self.current_node.next_val

        # check if off screen and remove 
        if self.x < 0 or self.x > WIDTH: #TODO make this lose life of player; maybe new type of tile "end"
            UNIT_LIST.remove(self)
            self.player.lose_life(1) #TODO different dmg based on unit type?
            return
        elif self.y < 0 or self.y > HEIGHT:
            UNIT_LIST.remove(self)
            self.player.lose_life(1) #TODO different dmg based on unit type?
            return


class Tile:
    # Class that describes the map tiles
    def __init__(self, tileType, position):
        self.tileType = tileType
        self.position = position

        if self.tileType == 0:
            self.color = COLORS["gray"]
        elif self.tileType == 1:
            self.color = COLORS["yellow"]
        else:
            print("Tile Type Error")

        self.rect = pygame.Rect(self.position, TILE_SIZE)
        self.surface = pygame.Surface(TILE_SIZE)
        self.surface.fill(self.color)

        self.has_tower = False

    def spawn_tower(self, towerType, player):
        if self.tileType == 1:
            print("This is a path, you cannot place towers here.")
        elif self.has_tower:
            print("This tile already has a tower on it.")
        elif player.money >= TOWER_TYPES[towerType]["cost"]:
            player.money -= TOWER_TYPES[towerType]["cost"]
            self.has_tower = Tower(towerType, self, player)
            self.color = COLORS[TOWER_TYPES[towerType]["color"]]
            self.surface.fill(self.color)
        else:
            #print(f"Not enough money: {player.money}")
            pass
            

class Player:
    def __init__(self, money=100, life=100):
        self.money = money
        self.max_hp = life
        self.hp = life

    def lose_life(self, amount):
        self.hp -= amount

        if self.hp <= 0:
            print("Player lost the game.")


class MapNode:
    def __init__(self, position, prev_val, next_val=None):
        self.position = position
        self.prev_val = prev_val
        self.next_val = next_val


class Button:
    def __init__(self, text, coords):
        self.text = text
        self.rendered_text = MAIN_FONT.render(self.text, 1, COLORS["black"])
        self.coords = coords
        self.pressed_down = False
        self.size = (MENU_W - 20, self.rendered_text.get_height()) # ?
        self.rect = pygame.Rect(self.coords, self.size)
        self.color = COLORS["light_blue"]
        self.surface = pygame.Surface(self.size)
        self.surface.fill(self.color)
        self.surface.blit(self.rendered_text, self.coords)

        BUTTON_LIST.append(self)

    def pressed(self): #TODO click sound?
        if self.text == "start round": # Button to start the next round early
            print("button start round")

        for t in TOWER_TYPES.keys():
            if self.text == t:
                print(f"Spawning {t} tower")

        self.surface.fill(self.color)
        self.surface.blit(self.rendered_text, self.coords)

    def check_hover(self):
        if self.rect.collidepoint(mouse.get_pos()):
            if pygame.mouse.get_pressed()[0]:
                self.pressed_down = True
                self.color = COLORS["dark_blue"]
                self.surface.fill(self.color)
                self.surface.blit(self.rendered_text, self.coords)
            else:
                self.pressed_down = False
                self.color = COLORS["blue"]
                self.surface.fill(self.color)
                self.surface.blit(self.rendered_text, self.coords)
        else:
            self.pressed_down = False
            self.color = COLORS["light_blue"]
            self.surface.fill(self.color)
            self.surface.blit(self.rendered_text, self.coords)


# ------------------- FUNCTIONS -------------------

def make_nodes():
    # function that creates a linked list of nodes with coordinates to represent a map path
    colums, rows = NUM_TILES


    node_list_head = MapNode((1, 0), None)
    last_node = node_list_head
    
    current_y = 1
    current_x = 1

    while current_y < colums:
        
        if last_node == node_list_head: # first node
            current_y += 2
        elif last_node.position[1] == last_node.prev_val.position[1]: # two times same y -> y + 2
            current_y += 2

        elif last_node.position[0] == 1: # last was left node -> jump to right
            current_x += colums-2
        else: # last was right node -> jump to left (only happens if the last two x values arent the same)
            current_x -= colums-2

        next_node = MapNode((current_x, current_y), last_node)
        last_node.next_val = next_node
        last_node = next_node
    
    return node_list_head


def make_map():
    colums, rows = NUM_TILES

    #TODO make node maps that can be loaded here
    node_list_head = make_nodes()

    # loop that connects each node with the next one
    path_list = [(1, 0)]
    i = node_list_head
    while i.next_val:

        dx = i.position[0] - i.next_val.position[0]
        dy = i.position[1] - i.next_val.position[1]
        for tile in range(abs(dx)):
            if dx < 0:
                path_tile_x = i.position[0] + tile
            else:
                path_tile_x = i.position[0] - tile
            path_tile_y = i.position[1]
            path_list.append((path_tile_x, path_tile_y))
        for tile in range(abs(dy)):
            path_tile_x = i.position[0]
            if dy < 0:
                path_tile_y = i.position[1] + tile
            else:
                path_tile_y = i.position[1] - tile
            path_list.append((path_tile_x, path_tile_y))

        i = i.next_val

    tile_list = []
    i = 0
    for c in range(colums):
        c_list = []
        for r in range(rows):
            if (c, r) in path_list:
                t = Tile(1, (c*TILE_SIZE[0], r*TILE_SIZE[1]))
            else:
                t = Tile(0, (c*TILE_SIZE[0], r*TILE_SIZE[1])) # alles wände
            c_list.append(t)
        tile_list.append(c_list)
        i += 1
    #TODO hier noch tile_list[-1] = "end" tile

    return tile_list, node_list_head


def make_buttons():
    Button("start round", (WIDTH + 10, 100))

    for t in TOWER_TYPES.keys():
        y_pos = BUTTON_LIST[-1].rect.bottomleft[1] + 10
        Button(t, (WIDTH + 10, y_pos))


def draw_window(tile_list, player, last_round):
    # Function that draws everything on screen (every frame)

    WIN.fill(COLORS["white"])

    # Draw all map tiles
    for c in tile_list:
        for r in c:
            WIN.blit(r.surface, r.rect)
    
    for t in TOWER_LIST:
        WIN.blit(t.surface, t.rect)

    for u in UNIT_LIST:
        WIN.blit(u.surface, u.rect)

    for p in PROJ_LIST:
        WIN.blit(p.surface, p.rect)


    for b in BUTTON_LIST:
        b.check_hover()
        WIN.blits(((b.surface, b.rect),(b.rendered_text, b.rect)))

    round_start_text = MAIN_FONT.render(f"Next round: {(ROUND_COOLDOWN - last_round - pygame.time.get_ticks())//1000}", 1, COLORS["black"]) 
    WIN.blit(round_start_text, (WIDTH+10, 10))

    player_health_text = MAIN_FONT.render(f"HP:{player.hp}/{player.max_hp}", 1, COLORS["black"]) #TODO put this in player class?
    WIN.blit(player_health_text, (WIDTH+10, 10 + round_start_text.get_height() + 10))

    player_money_text = MAIN_FONT.render(f"money:{player.money}", 1, COLORS["black"]) #TODO put this in player class?
    WIN.blit(player_money_text, (WIDTH + 10, 10 + round_start_text.get_height() + 10 + player_health_text.get_height() + 10))

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
    mapTileList, mapNodeHead = make_map() 
    make_buttons()
    clock = pygame.time.Clock()
    player = Player()

    run = True
    last_round = 0
    last_unit_spawn = 0
    units_to_spawn = 0
    while run:
        clock.tick(FPS)
        # vlt ersttmal nen Menü? aber kann später kommen

        if last_round + pygame.time.get_ticks() >= ROUND_COOLDOWN: # automatic round start
            print("round starting")
            last_round = - pygame.time.get_ticks()
            round_num = pygame.time.get_ticks()//ROUND_COOLDOWN
            units_to_spawn = round_num

        if units_to_spawn > 0 and last_unit_spawn + pygame.time.get_ticks() >= (ROUND_COOLDOWN*0.25)/(pygame.time.get_ticks()//ROUND_COOLDOWN): # staggered unit spawn
            unit = random.choice(["basic", "fast", "tank"])
            Unit(unit, mapNodeHead, player)
            units_to_spawn -= 1
            last_unit_spawn = - pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:       # linksclick check buttons
                    for b in BUTTON_LIST:
                        if b.rect.collidepoint(mouse.get_pos()):
                            b.pressed()
                elif event.button == 3:     # rechtcklick spawn turm 
                    for c in mapTileList:
                        for i in c:
                            if i.rect.collidepoint(mouse.get_pos()[0], mouse.get_pos()[1]):
                                tower = random.choice(["basic", "singleTarget", "superFast"])
                                i.spawn_tower(tower, player)
        update_objects()
        draw_window(mapTileList, player, last_round)    
    pygame.quit()


# ------------------- Save for multiple files being executed -------------------

if __name__ == "__main__":
    main()
