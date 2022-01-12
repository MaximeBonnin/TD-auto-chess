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
        self.surface = pygame.Surface((self.rect.width, self.rect.height))
        if self.type == "explosion":
            self.surface.set_colorkey(COLORS["black"])
            pygame.draw.circle(self.surface, COLORS["red"], (self.rect.width/2, self.rect.height/2), self.rect.width/2)
        elif self.type == "iceplosion":
            self.surface.set_colorkey(COLORS["black"])
            pygame.draw.circle(self.surface, COLORS["blue_light"], (self.rect.width/2, self.rect.height/2), self.rect.width/2)
        elif self.type == "player_dmg":
            self.surface.blit(player_dmg_effect_img, (0, 0))

        EFFECT_LIST.append(self)

    def tick(self):
        self.frame += 1
        self.surface.set_alpha(255 - 255 * self.frame/self.maxframe)

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
                if self.AoE:
                    self.AoE_rect = pygame.Rect((self.rect.x - self.AoE_area//2, self.rect.y - self.AoE_area//2), (self.AoE_area, self.AoE_area))
                    if self.projType["effect"]:
                        Effect(self.projType["effect"], self.AoE_rect)
                    for unit2 in UNIT_LIST:
                        if unit2.rect.colliderect(self.AoE_rect):
                            if self.projType["condition"] == "slow":
                                unit2.conditions[self.projType["condition"]] = {
                                    "effect_start": pygame.time.get_ticks(),
                                    "effect_duration": 2 * 1000,
                                    "effect_cooldown": 2 * 1000,
                                    "effect_strength": 1
                                }
                            unit2.take_dmg(self.dmg, self.origin)
            
                else:
                    unit.take_dmg(self.dmg, self.origin)

                    if self.projType["condition"] == "poison":
                        unit.conditions[self.projType["condition"]] = {
                            "effect_start": pygame.time.get_ticks(),
                            "effect_duration": 5 * 1000,
                            "effect_cooldown": 5 * 1000,
                            "effect_strength": 1
                        }

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
        self.towerTypeName = towerType
        self.towerType = TOWER_TYPES[towerType]
        self.tile = tile
        self.last_shot = pygame.time.get_ticks()
        self.player = player
        self.stats = {
            "Attack Speed": self.towerType["atk_speed"],
            "Crit Chance": self.towerType["crit_chance"],
            "Range": self.towerType["range"],
            "Projectile": self.towerType["proj_type"],
            "Proj. Damage": PROJ_TYPES[self.towerType["proj_type"]]["dmg"],
            "Kills": 0
        }
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
        
    def sell(self):
        explosion.play()
        self.player.money += self.towerType["cost"] * 0.75
        TOWER_LIST.remove(self)
        self.player.request_info()
        self.tile.has_tower = False

    def upgrade(self, direction):
        if direction in self.towerType["upgrades"].keys() and self.player.money >= self.towerType['upgrades'][direction]['cost']:
            print(f"Upgrading {self.towerType['display_name']} to {self.towerType['upgrades'][direction]['display_name']}")

            self.towerType = self.towerType["upgrades"][direction]
            temp_kills = self.stats["Kills"]
            self.stats = {
                "Attack Speed": self.towerType["atk_speed"],
                "Crit Chance": self.towerType["crit_chance"],
                "Range": self.towerType["range"],
                "Projectile": self.towerType["proj_type"],
                "Proj. Damage": PROJ_TYPES[self.towerType["proj_type"]]["dmg"],
                "Kills": temp_kills
            }

            self.surface.fill(COLORS["green_dark"])
            self.inner_surface = pygame.Surface((TOWER_SIZE[0]-8, TOWER_SIZE[1]-8))
            self.color = COLORS[self.towerType["color"]]
            self.inner_surface.fill(self.color)
            self.surface.blit(self.inner_surface, (4, 4))
            self.surface.blit(tower_base_img, (0,0))
            self.surface.blit(tower_turret_img, (0,0))

            self.player.money -= self.towerType['cost']
            self.player.request_info()
        elif direction in self.towerType["upgrades"].keys() and self.player.money < self.towerType['upgrades'][direction]['cost']:
            print(f"Not enough money: {self.towerType['upgrades'][direction]['cost']} needed.")
            error_sound.play()
        else:
            print("No upgrade here")
            error_sound.play()


class Unit:
    # Class that describes units
    def __init__(self, unitType, mapNodeHead, player, round):
        self.unitType = UNIT_TYPES[unitType]
        self.current_node = mapNodeHead
        self.next_node = self.current_node.next_val
        self.player = player
        self.lvl = round["number"]
        self.max_hp = self.unitType["hp"] * 1.05 ** self.lvl # 5% mehr hp pro runde? zu viel?
        self.hp = self.unitType["hp"] * 1.05 ** self.lvl
        self.special = self.unitType["special"]
        self.conditions = {
            "sample_effect": {
                "effect_start": 0,
                "effect_duration": 1000,
                "effect_cooldown": 1000,
                "effect_strength": 1
            }
        }
        self.last_stim = 10000
        self.speed = self.unitType["move_speed"]
        self.moved = 0

        self.random_move_modifier = random.randint(1, 10)/100

        self.x = mapNodeHead.position[0]*TILE_SIZE[0]*1.5 - self.unitType["size"][0]/2
        self.y = mapNodeHead.position[1]*TILE_SIZE[1]*1.5 + self.unitType["size"][1]/2
        self.rect = pygame.Rect((self.x, self.y), self.unitType["size"])
        self.surface = pygame.Surface(self.unitType["size"])
        self.surface.blit(self.unitType["skin"], (0,0))
        self.surface.set_colorkey((0,0,0))

        self.hp_bar = pygame.Surface((self.surface.get_width(), 3))
        self.hp_bar.fill(COLORS["green"])
        self.surface.blit(self.hp_bar, (0,0))

        global TOWER_LIST   # eig schlechte Lösung aber erstmal so: Globale variable mit allen Units
        UNIT_LIST.append(self)
    
    def die(self, origin):
        origin.stats["Kills"] += 1
        origin.player.money += self.unitType["gold_value"]
        explosion.play()
        UNIT_LIST.remove(self)

        #TODO animation
    
    def update_hp_bar(self):
        hp_left = self.hp/self.max_hp
        if hp_left > 0:
            hp_bar_green = pygame.Surface((self.surface.get_width() * hp_left, 3))
            self.hp_bar.fill(COLORS["red"])
            hp_bar_green.fill(COLORS["green"])
            self.hp_bar.blit(hp_bar_green, (0,0))
            self.surface.blit(self.hp_bar, (0,0))

    def take_dmg(self, amount, origin):
        self.hp -= amount

        self.check_special()
        self.check_conditions()
        self.update_hp_bar()

        hit.play()
        if self.hp <= 0:
            self.die(origin)


    def check_conditions(self):
        # remove conditions that have ended
        to_remove = []
        for cond in self.conditions.keys():
            if self.conditions[cond]["effect_start"] + self.conditions[cond]["effect_cooldown"] <= pygame.time.get_ticks():
                to_remove.append(cond)
        for i in to_remove:
            self.conditions.pop(i, None)
        
        # Movement conditions
        if "slow" in self.conditions.keys():
            if self.conditions["slow"]["effect_start"] + self.conditions["slow"]["effect_duration"] >= pygame.time.get_ticks():
                self.speed = self.unitType["move_speed"] / (2 * self.conditions["slow"]["effect_strength"])
            else:
                self.speed = self.unitType["move_speed"]

        if "stim" in self.conditions.keys():
            if self.conditions["stim"]["effect_start"] + self.conditions["stim"]["effect_duration"] >= pygame.time.get_ticks():
                self.speed = self.unitType["move_speed"] * (2 * self.conditions["stim"]["effect_strength"])
            else:
                self.speed = self.unitType["move_speed"]

        # Health conditions
        if "regen" in self.conditions.keys():
            hp_per_sec = self.max_hp * (0.05 * self.conditions["regen"]["effect_strength"])
            if self.hp < self.max_hp:
                self.hp += hp_per_sec / FPS
                self.update_hp_bar()
        
        if "poison" in self.conditions.keys():
            hp_per_sec = self.max_hp * (0.1 * self.conditions["poison"]["effect_strength"]) # poison does 10% per sec? THIS IS NOT COUNTED AS A HIT -> DOESNT KILL (good?)
            if self.hp < self.max_hp:
                self.hp -= hp_per_sec / FPS
                self.update_hp_bar()


    def check_special(self):

        if self.special == "stim" and "stim" not in self.conditions.keys():     # speed up after getting hit
            if self.hp < self.max_hp:
                self.conditions["stim"] = {
                    "effect_start": pygame.time.get_ticks(),
                    "effect_duration": 2 * 1000,
                    "effect_cooldown": 6 * 1000,
                    "effect_strength": 1
                }

        if self.special == "regen" and "regen" not in self.conditions.keys():     # regenerate health 
            if self.hp < self.max_hp:
                self.conditions["regen"] = {
                    "effect_start": pygame.time.get_ticks(),
                    "effect_duration": 800 * 1000,
                    "effect_cooldown": 800 * 1000,
                    "effect_strength": 1
                }

     
    
    def move(self): # move to next node in path
        if self.current_node.position[0] > self.next_node.position[0]:      # move left
            self.x -= self.speed*(1 + self.random_move_modifier)
        elif self.current_node.position[0] < self.next_node.position[0]:    # move right
            self.x += self.speed*(1 + self.random_move_modifier)
        elif self.current_node.position[1] < self.next_node.position[1]:    # move down
            self.y += self.speed*(1 + self.random_move_modifier)
        else:                                                               # move up
            self.y -= self.speed*(1 + self.random_move_modifier)
        self.rect.x = self.x
        self.rect.y = self.y

        self.moved += self.speed

        
        self.check_conditions()
        
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
        self.selected = None #TODO rename this and change it with actual selected
        self.info_requested = None
        self.unit_sell_button = None
        self.unit_upgrade_a_button = None
        self.unit_upgrade_b_button = None

    def lose_life(self, amount):
        self.hp -= amount
        Effect("player_dmg", pygame.Rect((0, 0), (WIDTH, HEIGHT)))

        if self.hp <= 0:
            print("Player lost the game.")

    def display_selected(self):
        display_surface = pygame.Surface((TOWER_TYPES[self.selected]["range"]*2, TOWER_TYPES[self.selected]["range"]*2))
        display_surface.set_colorkey(COLORS["black"])
        pygame.draw.circle(display_surface, COLORS["red"], display_surface.get_rect().center, TOWER_TYPES[self.selected]["range"], width=2)
        to_display = tower_base_img  #TODO make this work again: TOWER_TYPES[self.selected]["skin"]
        display_surface.blit(to_display, (display_surface.get_width()/2 - to_display.get_width()/2, display_surface.get_height()/2 - to_display.get_height()/2))

        img_w, img_h = display_surface.get_width(), display_surface.get_height()
        m_x, m_y = pygame.mouse.get_pos()
        x, y = m_x - img_w//2, m_y - img_h//2

        return (display_surface, (x, y))

    def select(self, towerType = None): # select given tower type, if no type is given -> set to None
        self.selected = towerType

    def request_info(self, tower = None):
        self.info_requested = tower

        if self.info_requested == None:
            if self.unit_upgrade_a_button in BUTTON_LIST:
                BUTTON_LIST.remove(self.unit_upgrade_a_button)
            if self.unit_upgrade_b_button in BUTTON_LIST:
                BUTTON_LIST.remove(self.unit_upgrade_b_button)
            if self.unit_sell_button in BUTTON_LIST:
                BUTTON_LIST.remove(self.unit_sell_button)

        elif "upgrade_a" in self.info_requested.towerType["upgrades"].keys(): #TODO add the price here as well 
            if self.unit_upgrade_a_button != None:
                self.unit_upgrade_a_button.update_text(f'{self.info_requested.towerType["upgrades"]["upgrade_a"]["cost"]}: {self.info_requested.towerType["upgrades"]["upgrade_a"]["display_name"]}')

            if self.unit_upgrade_b_button != None:
                self.unit_upgrade_b_button.update_text(f'{self.info_requested.towerType["upgrades"]["upgrade_b"]["cost"]}: {self.info_requested.towerType["upgrades"]["upgrade_b"]["display_name"]}')
        else:
            print("No more upgrades here")
        

class MapNode:
    def __init__(self, position, prev_val, next_val=None):
        self.position = position
        self.prev_val = prev_val
        self.next_val = next_val


class Button:
    def __init__(self, text, text_to_render, coords):
        self.text = text
        self.text_to_render = text_to_render  
        self.rendered_text = MEDIUM_FONT.render(self.text_to_render, 1, COLORS["black"])
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

    def update_text(self, text_to_render):
        self.text_to_render = text_to_render
        self.rendered_text = MEDIUM_FONT.render(self.text_to_render, 1, COLORS["black"])
        self.surface.fill(self.color)
        self.surface.blit(self.rendered_text, self.coords)

    def pressed(self, player):
        click.play()
        if self.text == "start round" and self.last_round_start_press + ROUND_COOLDOWN//4 <= pygame.time.get_ticks(): # Button to start the next round early, can't be spammed
            round_event = pygame.event.Event(USEREVENTS["round_start"])
            pygame.event.post(round_event)
            self.last_round_start_press = pygame.time.get_ticks()
        elif self.text == "sell":
            if player.info_requested:
                player.info_requested.sell()
        elif self.text == "upgrade_a":
            if player.info_requested:
                player.info_requested.upgrade("upgrade_a")
        elif self.text == "upgrade_b":
            if player.info_requested:
                player.info_requested.upgrade("upgrade_b")
        else:
            for t in TOWER_TYPES.keys():
                if self.text == t:
                    print(f"Selecting {t} tower")
                    player.select(t)
                    break

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