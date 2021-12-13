# ------------------- Import -------------------

import pygame
import math
import random
import os


# ------------------- Global Variables -------------------

WIDTH, HEIGHT = 500, 500
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
FPS = 60

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

def draw_window():
    # Function that draws everything on screen (every frame)

    WIN.fill(COLORS["white"])
    pygame.display.update()


# ------------------- Main Game Loop -------------------

def main():
    clock = pygame.time.Clock()

    run = True
    while run:
        clock.tick(FPS)
        # vlt ersttmal nen Menü? aber kann später kommen
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        draw_window()
    pygame.quit()


# ------------------- Save for multiple files being executed -------------------
if __name__ == "__main__":
    main()
