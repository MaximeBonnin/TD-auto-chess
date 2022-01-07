import math
import random

import pygame
from pygame import mouse

from asset_list import *
from Variables import *


class Effect:
    def __init__(self, effectType, rect):
        self.type = effectType
        self.frame = 1
        self.maxframe = 30
        self.rect = rect
        self.color = COLORS["red"]
        self.surface = pygame.Surface((self.rect.width, self.rect.height))
        self.surface.fill(self.color)

        EFFECT_LIST.append(self)

    def tick(self):
        self.frame += 1
        self.surface.set_alpha(255 - 255 * self.frame/self.maxframe)
        self.surface.fill(self.color)

        if self.frame > self.maxframe:
            EFFECT_LIST.remove(self)


class Projectile:
    def __init__(self, projType, origin, target, player, is_crit):
        self.projType = PROJ_TYPES[projType]
        self.origin = origin
        self.target = target
        self.x, self.y = origin.tile.rect.centerx - PROJ_SIZE[0]//2, origin.tile.rect.centery - PROJ_SIZE[0]//2
        self.player = player
        self.is_crit = is_crit
        if is_crit:
            self.color = COLORS["black"]
            self.dmg = self.projType["dmg"] * 2
        else:
            self.color = origin.color
            self.dmg = self.projType["dmg"]
        self.last_move = pygame.time.get_ticks()
        self.AoE = self.projType["AoE"]
        self.AoE_area = self.projType["AoE_area"]

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
                #TODO add Aoe image / animation
                if self.AoE:
                    self.AoE_rect = pygame.Rect((self.rect.x - self.AoE_area//2, self.rect.y - self.AoE_area//2), (self.AoE_area, self.AoE_area))
                    Effect("explosion", self.AoE_rect)
                    for unit2 in UNIT_LIST:
                        if unit2.rect.colliderect(self.AoE_rect):
                            unit2.take_dmg(self.projType["dmg"], self.origin)
            
                else:
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

                distance = ((self.target.rect.centery - self.y)**2+(self.target.rect.centerx - self.x)**2)**(1/2)
                if distance <= self.projType["speed"]: # avoid overshooting 
                    self.dx = math.cos(self.angle)*distance
                    self.dy = math.sin(self.angle)*distance
                else:
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
    # TODO eventuell einen kreis um den zu platzierenden Turm zeichnen, für die Schussreichweite?
    def __init__(self, towerType, tile, player):
        self.towerType = TOWER_TYPES[towerType]
        self.tile = tile
        self.last_shot = pygame.time.get_ticks()
        self.player = player
        self.kills = 0      # Zählen von kills für stats oder lvl system?
        self.rect = self.tile.rect
        self.surface = pygame.Surface(TOWER_SIZE)
        self.surface.fill(COLORS["green_dark"])
        self.inner_surface = pygame.Surface((TOWER_SIZE[0]-8, TOWER_SIZE[1]-8)) #TODO der Tower hat nach dem platzieren immer noch einen dunkelgrünen rand, den würde ich gerne durch das img ersetzen, aber ich habe keine Ahnung wie das geh
        self.color = COLORS[self.towerType["color"]]
        self.inner_surface.fill(self.color)
        self.surface.blit(self.inner_surface, (4, 4))
        self.surface.blit(tower_base_img, (0,0))
        self.surface.blit(tower_turret_img, (0,0))
        self.targeting = "close"

        click_plop.play()
        global TOWER_LIST   # eig schlechte Lösung aber erstmal so: Globale variable mit allen Türmen
        TOWER_LIST.append(self)

    def aim(self, unitList):
        # kürzeste distanz von unit
        m = self.tile.rect.center
        target = False
        distance_list = []

        if self.targeting == "close":
            for u in unitList: #TODO make this more efficient, currently every turret checks every unit every frame => num_units * num_turrets calcs per sec; maybe recursive?
                m_u = u.rect.center
                distance = ((m[0]-m_u[0])**2 + (m[1]-m_u[1])**2)**(1/2) # a^2+b^2 = c^2
                distance_list.append(distance)
            target = UNIT_LIST[distance_list.index(min(distance_list))]
            distance = min(distance_list)

        elif self.targeting == "first": #TODO this doesnt work at all, fix it! maybe try/except?
            max_moved_in_range = 0
            for u in UNIT_LIST:
                m_u = u.rect.center
                distance = ((m[0]-m_u[0])**2 + (m[1]-m_u[1])**2)**(1/2)
                if distance <= self.towerType["range"]:
                    if u.moved >= max_moved_in_range:
                        target = u

            if not target:
                target = UNIT_LIST[distance_list.index(max([unit.moved for unit in UNIT_LIST]))]
                print("no target in range")

        else:
            print("This should not happen")
    
        angle = math.atan2(target.rect.centery - self.rect.centery, target.rect.centerx - self.rect.centerx) * -180/math.pi
        rotated_image = pygame.transform.rotate(tower_turret_img, angle)

        new_rect = rotated_image.get_rect(center = tower_turret_img.get_rect().center)

        self.surface.fill(COLORS["green_dark"])
        self.surface.blit(self.inner_surface, (4, 4))
        self.surface.blit(tower_base_img, (0,0))
        self.surface.blit(rotated_image, new_rect.topleft)

        return target, distance

    def shoot(self, unitList):
        if unitList:
            target, distance = self.aim(unitList)
            cooldown = self.towerType["atk_speed"]*1000
            now = pygame.time.get_ticks()

            if distance <= self.towerType["range"] and (now - self.last_shot) >= cooldown:
                
                if random.random() <= self.towerType["crit_chance"]:
                    is_crit = True
                else:
                    is_crit = False

                pew.play()
                Projectile(self.towerType["proj_type"], self, target, self.player, is_crit)
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
        self.moved = 0

        self.random_move_modifier = random.randint(1, 10)/100

        self.x = mapNodeHead.position[0]*TILE_SIZE[0]*1.5 - self.unitType["size"][0]/2
        self.y = mapNodeHead.position[1]*TILE_SIZE[1]*1.5 + self.unitType["size"][1]/2
        self.rect = pygame.Rect((self.x, self.y), self.unitType["size"])
        self.surface = pygame.Surface(self.unitType["size"])
        self.surface.blit(self.unitType["skin"], (0,0))
        self.surface.set_colorkey((0,0,0))

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
        # self.color = (int(255 * (1-health_percent)), int(255 * health_percent), 0)
        self.surface = pygame.Surface(self.unitType["size"]) # @MJ sehr nice das du das auch gefunden hast! dann müssen wir mit hp-bar nochmal gucken
        self.surface.blit(self.unitType["skin"], (0,0))
        self.surface.set_colorkey((0,0,0))

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

        self.moved += self.unitType["move_speed"]
        
        next_node_coords = (self.next_node.position[0]*TILE_SIZE[0] + TILE_SIZE[0]/2, self.next_node.position[1]*TILE_SIZE[1] + TILE_SIZE[1]/2)

        if self.rect.collidepoint(next_node_coords): # next node if arrived at node
            self.current_node = self.current_node.next_val
            self.next_node = self.current_node.next_val

        # check if off screen and remove 
        if self.x < 0 or self.x > WIDTH:
            UNIT_LIST.remove(self)
            self.player.lose_life(1)
            return
        elif self.y < 0 or self.y > HEIGHT:
            UNIT_LIST.remove(self)
            self.player.lose_life(1)
            return


class Tile:
    # Class that describes the map tiles
    def __init__(self, tileType, position):
        self.tileType = tileType
        self.position = position

        if self.tileType == 0:
            skin = tile_gras_img    # @Maxime habe ich das hier mit skin so richtig gemacht? Also es funktioniert, aber ich habe deine Struktur noch nicht ganz verstanden
        elif self.tileType == 1:
            skin = tile_path_img
        else:
            print("Tile Type Error")

        self.rect = pygame.Rect(self.position, TILE_SIZE)

        self.surface = pygame.Surface(TILE_SIZE)
        self.surface.blit(skin, (0,0))
        self.surface.set_colorkey((0,0,0))   

        self.has_tower = False

    def spawn_tower(self, towerType, player):
        if self.tileType == 1:
            error_sound.play()
            #print("This is a path, you cannot place towers here.")
        elif self.has_tower:
            error_sound.play()
            #print("This tile already has a tower on it.")
        elif player.money >= TOWER_TYPES[towerType]["cost"]:
            player.money -= TOWER_TYPES[towerType]["cost"]
            self.has_tower = Tower(towerType, self, player)
            self.color = COLORS[TOWER_TYPES[towerType]["color"]]
            self.surface.blit(tile_gras_img, (0,0))     # @Maxime hier habe ich das auch als img eingefügt würde das aber gerne über "skin" nachen. nur bekomme ich das nicht hin
            self.surface.set_colorkey((0,0,0))
        else:
            #print(f"Not enough money: {player.money}")
            error_sound.play()
            

class Player:
    def __init__(self, money=100, life=100):
        self.money = money
        self.max_hp = life
        self.hp = life
        self.selected = None
        self.info_requested = None

    def lose_life(self, amount):
        self.hp -= amount

        if self.hp <= 0:
            print("Player lost the game.")

    def display_selected(self):
        to_display = TOWER_TYPES[self.selected]["skin"]
        img_w, img_h = to_display.get_width(), to_display.get_height()
        m_x, m_y = pygame.mouse.get_pos()
        x, y = m_x - img_w//2, m_y - img_h//2

        return (to_display, (x, y))

    def select(self, towerType = None): # select given tower type, if no type is given -> set to None
        self.selected = towerType


    def display_info(self):
        if self.info_requested:
            print(f"{self.info_requested=}")

    def request_info(self, towerType = None): # select given tower type, if no type is given -> set to None
        self.selected = towerType

class MapNode:
    def __init__(self, position, prev_val, next_val=None):
        self.position = position
        self.prev_val = prev_val
        self.next_val = next_val


class Button:
    def __init__(self, text, coords):
        self.text = text
        self.text_to_render = text
        if self.text in TOWER_TYPES.keys():
            self.text_to_render = f"{TOWER_TYPES[self.text]['cost']} - {self.text}" 
        self.rendered_text = MAIN_FONT.render(self.text_to_render, 1, COLORS["black"])
        self.coords = coords
        self.pressed_down = False
        self.size = (MENU_W - 20, self.rendered_text.get_height()) # ?
        self.rect = pygame.Rect(self.coords, self.size)
        self.color = COLORS["blue_light"]
        self.surface = pygame.Surface(self.size)
        self.surface.fill(self.color)
        self.surface.blit(self.rendered_text, self.coords)

        self.last_round_start_press = pygame.time.get_ticks()
        

        BUTTON_LIST.append(self)

    def pressed(self, player):
        click.play()
        if self.text == "start round" and self.last_round_start_press + ROUND_COOLDOWN//4 <= pygame.time.get_ticks(): # Button to start the next round early, can't be spammed
            round_event = pygame.event.Event(USEREVENTS["round_start"])
            pygame.event.post(round_event)
            self.last_round_start_press = pygame.time.get_ticks()

        for t in TOWER_TYPES.keys():
            if self.text == t:
                print(f"Selecting {t} tower")
                player.select(t)


        self.surface.fill(self.color)
        self.surface.blit(self.rendered_text, self.coords)

    def check_hover(self):
        if self.rect.collidepoint(mouse.get_pos()):
            if pygame.mouse.get_pressed()[0]:
                self.pressed_down = True
                self.color = COLORS["blue_dark"]
                self.surface.fill(self.color)
                self.surface.blit(self.rendered_text, self.coords)
            else:
                self.pressed_down = False
                self.color = COLORS["blue"]
                self.surface.fill(self.color)
                self.surface.blit(self.rendered_text, self.coords)
        else:
            self.pressed_down = False
            self.color = COLORS["blue_light"]
            self.surface.fill(self.color)
            self.surface.blit(self.rendered_text, self.coords)

# ------------------- Save for multiple files being executed -------------------

if __name__ == "__main__":
    print("Don't run this as main.")