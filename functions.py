import pygame

import Variables
from Variables import NUM_TILES
from Variables import TILE_SIZE
from Variables import BUTTON_LIST
from Variables import TOWER_TYPES
from Variables import WIDTH
from Variables import COLORS
from Variables import WIN
from Variables import TOWER_LIST
from Variables import UNIT_LIST
from Variables import EFFECT_LIST
from Variables import MAIN_FONT
from Variables import ROUND_COOLDOWN
from Variables import PROJ_LIST
from Variables import USEREVENTS

import Clases
from Clases import Tile
from Clases import MapNode
from Clases import Button



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


def draw_window(tile_list, player, round):
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

    for e in EFFECT_LIST:
        WIN.blit(e.surface, e.rect)
        e.tick()

    for b in BUTTON_LIST:
        b.check_hover()
        WIN.blits(((b.surface, b.rect),(b.rendered_text, b.rect)))

    if player.selected:
        selected_unit_img, selected_unit_coords = player.display_selected()
        WIN.blit(selected_unit_img, selected_unit_coords)


    if round['number'] > 1:
        round_start_text = MAIN_FONT.render(f"Next round ({round['number']}): {(ROUND_COOLDOWN - (pygame.time.get_ticks() - round['time']))//1000}", 1, COLORS["black"]) 
        WIN.blit(round_start_text, (WIDTH+10, 10))
    else:
        round_start_text = MAIN_FONT.render(f"Not started", 1, COLORS["black"]) 
        WIN.blit(round_start_text, (WIDTH+10, 10))

    player_health_text = MAIN_FONT.render(f"HP:{player.hp}/{player.max_hp}", 1, COLORS["black"]) #TODO put this in player class?
    WIN.blit(player_health_text, (WIDTH+10, 10 + round_start_text.get_height() + 10))

    player_money_text = MAIN_FONT.render(f"Money:{player.money}", 1, COLORS["black"]) #TODO put this in player class?
    WIN.blit(player_money_text, (WIDTH + 10, 10 + round_start_text.get_height() + 10 + player_health_text.get_height() + 10))

    pygame.display.update()


def update_objects():
    for t in TOWER_LIST:
        t.shoot(UNIT_LIST)
    for p in PROJ_LIST:
        p.move()
    for u in UNIT_LIST:
        u.move()


def handle_rounds(round):
    
    unit_spawn_spacing = int(ROUND_COOLDOWN*0.25/round["number"])
    unit_event = pygame.event.Event(USEREVENTS["unit_spawn"])
    pygame.time.set_timer(unit_event, unit_spawn_spacing)
