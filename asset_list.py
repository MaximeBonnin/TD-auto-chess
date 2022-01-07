import os
import pygame

pygame.mixer.init()

#TODO add central volume control
MASTER_VOLUME = 0.1

# ------------------- Images -------------------
tower_base_img = pygame.image.load(os.path.join("Assets","Images","tower_base.png"))
tower_turret_img = pygame.image.load(os.path.join("Assets","Images","tower_turret.png"))
unit_basic_img = pygame.image.load(os.path.join("Assets","Images","unit_basic.png"))
unit_fast_img = pygame.image.load(os.path.join("Assets","Images","unit_fast.png"))
unit_tank_img = pygame.image.load(os.path.join("Assets","Images","unit_tank.png"))
tile_gras_img = pygame.image.load(os.path.join("Assets","Images","tile_gras.png"))
tile_path_img = pygame.image.load(os.path.join("Assets","Images","tile_path.png"))

# ------------------- Sounds -------------------
pew = pygame.mixer.Sound(os.path.join("Assets","Sound","pew.wav"))
pew.set_volume(0.1*MASTER_VOLUME)
hit = pygame.mixer.Sound(os.path.join("Assets","Sound","hit.mp3"))
hit.set_volume(0.2*MASTER_VOLUME)
explosion = pygame.mixer.Sound(os.path.join("Assets","Sound","explosion.wav"))
explosion.set_volume(0.4*MASTER_VOLUME)
click = pygame.mixer.Sound(os.path.join("Assets","Sound","click.wav"))
click.set_volume(0.4*MASTER_VOLUME)
click_plop = pygame.mixer.Sound(os.path.join("Assets","Sound","click_plop.wav"))
click_plop.set_volume(0.4*MASTER_VOLUME)
error_sound = pygame.mixer.Sound(os.path.join("Assets","Sound","error.wav"))
error_sound.set_volume(0.4*MASTER_VOLUME)

# ------------------- Save for multiple files being executed -------------------

if __name__ == "__main__":
    print("Don't run this as main.")