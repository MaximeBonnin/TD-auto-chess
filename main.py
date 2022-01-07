#
#  ------------------- Import -------------------

# https://www.pygame.org/docs/
# https://www.youtube.com/watch?v=jO6qQDNa2UY
# https://csatlas.com/python-import-file-module/ (HowTo multi file)

import random
import shutil

import pygame
from pygame import mouse

from all_classes import *
from functions import *
from Variables import *

# ------------------- Initiallize -------------------

pygame.init()
pygame.display.set_caption("Tower Defence Game")

# ------------------- Main Game Loop -------------------

def main():
    mapTileList, mapNodeHead = make_map() 
    make_buttons()
    clock = pygame.time.Clock()
    player = Player()

    run = True
    round = {
        "time": 0,
        "number": 1
    }
    
    while run:
        clock.tick(FPS)
        # vlt ersttmal nen Menü? aber kann später kommen

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:       # linksclick check buttons
                    for b in BUTTON_LIST:
                        if b.rect.collidepoint(mouse.get_pos()):
                            b.pressed(player)
                            break

                    for c in mapTileList: # linksclick ausgewählten spawn turm #TODO this is a weird way of handleing tower spawns
                        for i in c:
                            if player.selected and i.rect.collidepoint(mouse.get_pos()):
                                tower = player.selected
                                i.spawn_tower(tower, player)
                                if not pygame.key.get_pressed()[pygame.K_LSHIFT]: # holding shift keeps unit selected after placing
                                    player.select()
                                break

                    for t in TOWER_LIST: # left click on tower displays info and gives options to interact
                        if t.rect.collidepoint(mouse.get_pos()):
                            player.request_info(t)
                            break

                elif event.button == 3:     # rechtcklick spawn turm 
                    player.select()

            elif event.type == USEREVENTS["round_start"]: # triggers after every coolddown or when button is pressed
                handle_rounds(round)
                units_to_spawn = round["number"]

                round["number"] += 1
                round["time"] = pygame.time.get_ticks()

                round_event = pygame.event.Event(USEREVENTS["round_start"])
                pygame.time.set_timer(round_event, ROUND_COOLDOWN)

            elif event.type == USEREVENTS["unit_spawn"]: # triggers on the start of the round and spawns units until number of units in the round is reached
                if units_to_spawn > 0:
                    unit = random.choice(list(UNIT_TYPES.keys()))
                    Unit(unit, mapNodeHead, player)
                    units_to_spawn -= 1
                else:
                    unit_event = pygame.event.Event(USEREVENTS["unit_spawn"])
                    pygame.time.set_timer(unit_event, 0)

        update_objects()
        draw_window(mapTileList, player, round)    
    pygame.quit()
    shutil.rmtree("__pycache__", ignore_errors=False, onerror=None)



# ------------------- Save for multiple files being executed -------------------

if __name__ == "__main__":
    main()
