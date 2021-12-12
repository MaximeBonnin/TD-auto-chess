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
    "red": (255, 255, 204),
    "yellow": (255, 255, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255)
}


# ------------------- Initiallize -------------------

pygame.init
pygame.display.set_caption("Tower Defence Game")


# ------------------- CLASSES -------------------

class Tower:
    # Class that describes towers
    def __init__(self):
        pass

class Unit:
    # Class that describes units
    def __init__(self):
        pass


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
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        

        draw_window()
    pygame.quit()


# ------------------- Save for multiple files being executed -------------------
if __name__ == "__main__":
    main()
