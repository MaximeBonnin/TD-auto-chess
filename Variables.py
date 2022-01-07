import pygame

import asset_list
from asset_list import (tower_base_img, unit_basic_img, unit_fast_img,
                        unit_tank_img)

pygame.font.init()

WIDTH, HEIGHT = 32*20, 32*20
MENU_W, MENU_H = int(WIDTH*0.25), HEIGHT
WIN = pygame.display.set_mode((WIDTH+MENU_W, HEIGHT))
FPS = 60

MAIN_FONT = pygame.font.SysFont("Arial", 20)
ROUND_COOLDOWN = 10*1000 # in milliseconds

TILE_SIZE = (32, 32)
PROJ_SIZE = (4, 4)
TOWER_SIZE = (32, 32)
NUM_TILES = (WIDTH//TILE_SIZE[0], HEIGHT//TILE_SIZE[1]) # numbers of tiles as tuple (columns, rows)

UNIT_LIST =[]
TOWER_LIST = []
PROJ_LIST = []
BUTTON_LIST = []
EFFECT_LIST = []

USEREVENTS = {
    "round_start": pygame.USEREVENT,
    "unit_spawn": pygame.USEREVENT + 1
}

COLORS = {
    "black": (0, 0, 0),
    "blue": (0, 0, 255),
    "blue_dark": (0, 0, 139),
    "blue_light": (173, 216, 230),
    "brown": (153, 120, 0),
    "gray": (128, 128, 128),
    "green": (0, 255, 0),
    "green_dark": (0, 120, 0),
    "red": (255, 0, 0),
    "white": (255, 255, 255),
    "yellow": (255, 255, 0)
}

TOWER_TYPES = {
    "basic": {
        "atk_speed": 1,    
        "cost": 10,
        "color": "white",
        "range": 150,
        "proj_type": "basic",
        "crit_chance": 0.1,
        "skin": tower_base_img
    },
    "singleTarget": {
        "atk_speed": 5,     
        "cost": 25,
        "color": "yellow",
        "range": 300,
        "proj_type": "seeking",
        "crit_chance": 0.5,
        "skin": tower_base_img
    },
    "AoE": {
        "atk_speed": 3,     
        "cost": 50,
        "color": "red",
        "range": 100,
        "proj_type": "AoE",
        "crit_chance": 0.1,
        "skin": tower_base_img
    },
    "superFast": {
        "atk_speed": 0.2,     
        "cost": 50,
        "color": "blue_light",
        "range": 100,
        "proj_type": "weak",
        "crit_chance": 0.2,
        "skin": tower_base_img
    },
    # "lightning": {
    #     "atk_speed": 0.2,     
    #     "cost": 25,
    #     "color": "blue_light",
    #     "range": 100,
    #     "proj_type": "weak"
    #     "crit_chance": 0.1,
    # }
}

UNIT_TYPES = {
    "basic": {
        "move_speed": 2,
        "hp": 10,
        "size": (20, 20),          
        "gold_value": 5,
        "special": False,   
        "skin": unit_basic_img
    },
    "fast": {
        "move_speed": 5,
        "hp": 5,
        "size": (20, 20),          
        "gold_value": 4,
        "special": False,    
        "skin": unit_fast_img
    },
    "tank": {
        "move_speed": 1,
        "hp": 25,
        "size": (20, 20),          
        "gold_value": 10,
        "special": False,    
        "skin": unit_tank_img
    }
}

PROJ_TYPES = {
    "basic": {
        "dmg": 3,
        "speed": 20,
        "spread": 1, # ???
        "AoE": False,
        "AoE_area": 0,
        "seeking": False,
        "color": "white"
    },
    "seeking": {
        "dmg": 10,
        "speed": 6,
        "spread": 1, # ???
        "AoE": False,
        "AoE_area": 0,
        "seeking": True,
        "color": "blue"
    },
    "weak": {
        "dmg": 1,
        "speed": 50,
        "spread": 1, # ???
        "AoE": False,
        "AoE_area": 0,
        "seeking": True,
        "color": "blue_light"
    },
    "AoE": {
        "dmg": 2,
        "speed": 10,
        "spread": 1, # ???
        "AoE": True,
        "AoE_area": 50,
        "seeking": True,
        "color": "red"
    }
}
