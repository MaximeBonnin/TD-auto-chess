import pygame

from all_classes import *
from Variables import *


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
    Button("start round", "Start Round", (WIDTH + 10, 100))

    for t in TOWER_TYPES.keys():
        y_pos = BUTTON_LIST[-1].rect.bottomleft[1] + 10
        Button(t, f"{TOWER_TYPES[t]['cost']}: {TOWER_TYPES[t]['display_name']}", (WIDTH + 10, y_pos))


def info_box(player):
    info_box = pygame.Surface((MENU_W, 200))
    x, y = WIDTH, HEIGHT-200

    if player.info_requested: # displays info about towers
        
        # Buttons for selling and upgrades
        info_box.fill(COLORS[player.info_requested.towerType["color"]])

        info = MAIN_FONT.render(f"{player.info_requested.towerType['display_name']}", 1, COLORS["black"])

        info_box.blit(info, (10, 0))

        if player.unit_sell_button not in BUTTON_LIST:
            player.unit_sell_button = Button("sell", f"Sell (75%): {player.info_requested.towerType['cost'] * 0.75}", (x+10, y+20))
        info_box.blit(player.unit_sell_button.surface, (10, 20))

        if player.unit_upgrade_a_button not in BUTTON_LIST and "upgrade_a" in player.info_requested.towerType["upgrades"].keys():
            player.unit_upgrade_a_button = Button("upgrade_a", f'{player.info_requested.towerType["upgrades"]["upgrade_a"]["cost"]}: {player.info_requested.towerType["upgrades"]["upgrade_a"]["display_name"]}', (x+10, y+40))
        info_box.blit(player.unit_upgrade_a_button.surface, (10, 40))

        if player.unit_upgrade_b_button not in BUTTON_LIST and "upgrade_a" in player.info_requested.towerType["upgrades"].keys():
            player.unit_upgrade_b_button = Button("upgrade_b", f'{player.info_requested.towerType["upgrades"]["upgrade_a"]["cost"]}: {player.info_requested.towerType["upgrades"]["upgrade_b"]["display_name"]}', (x+10, y+60))
        info_box.blit(player.unit_upgrade_b_button.surface, (10, 60))

        # Stats
        title_render = MAIN_FONT.render(f"Stats", 1, COLORS["black"])
        info_box.blit(title_render, (10, 100))

        index = 0
        for stat in player.info_requested.stats:
            stat_txt = SMALL_FONT.render(f"{stat}: {player.info_requested.stats[stat]}", 1, COLORS["black"])
            info_box.blit(stat_txt, (10, 100 + title_render.get_height() + index * stat_txt.get_height()))
            index += 1


    else: # before first select: display controls
        tutorial_info = [
            "Click and drop towers",
            "Right click to unselect",
            "Hold Lshift to keep selected",
            "Upgrade and sell buttons"
        ]

        headline = MAIN_FONT.render("Controls", 1, COLORS["white"])
        info_box.blit(headline, (10, 10))

        for line in tutorial_info:
            text = MEDIUM_FONT.render(line, 1, COLORS["white"])
            info_box.blit(text, (10, 30 + tutorial_info.index(line) * text.get_height()))

    return info_box


def draw_window(tile_list, player, round):
    # Function that draws everything on screen (every frame)

    WIN.fill(COLORS["white"])

    # Draw all map tiles
    for c in tile_list:
        for r in c:
            WIN.blit(r.surface, r.rect)
    
    for t in TOWER_LIST: # display all towers on screen
        WIN.blit(t.surface, t.rect)

    for u in UNIT_LIST: # display all units on screen
        WIN.blit(u.surface, u.rect)

    for p in PROJ_LIST: # display all projectiles on screen
        WIN.blit(p.surface, p.rect)

    for e in EFFECT_LIST: # display all effects on screen
        WIN.blit(e.surface, e.rect)
        e.tick()

    WIN.blit(info_box(player), (WIDTH, HEIGHT-200))

    for b in BUTTON_LIST: # display all buttons on screen
        b.check_hover()
        WIN.blits(((b.surface, b.rect),(b.rendered_text, b.rect)))

    if player.selected: # drag and drop tower display
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


def menu_loop():
    clock = pygame.time.Clock()
    
    #menu_surface = pygame.Surface(WIDTH+MENU_W, HEIGHT)
    menu_img = pygame.image.load(os.path.join("Assets","Images","menu_bg.png"))

    run = True
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    return

        WIN.blit(menu_img, (0, 0))
        pygame.display.update()

    pygame.quit()

# ------------------- Save for multiple files being executed -------------------

if __name__ == "__main__":
    print("Don't run this as main.")