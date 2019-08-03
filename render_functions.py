# -*- coding: utf-8 -*-
"""
Created on Tue Jun 25 19:35:17 2019

@author: theoldestnoob
"""

import tcod
from enum import Enum

from game_states import GameStates
from menus import inventory_menu, level_up_menu, character_screen


class RenderOrder(Enum):
    STAIRS = 1
    CORPSE = 2
    ITEM = 3
    ACTOR = 4


def render_bar(panel, x, y, total_width, name, value, maximum, bar_color,
               back_color):
    bar_width = int(float(value) / maximum * total_width)
    panel.draw_rect(x, y, total_width, 1, ord(" "), bg=back_color)
    if bar_width > 0:
        panel.draw_rect(x, y, bar_width, 1, ord(" "), bg=bar_color)
    panel.print(int(x + total_width / 2), y, f"{name}: {value}/{maximum}",
                fg=tcod.white, alignment=tcod.CENTER)


def mouseover_names(console, game_map, mouse_x, mouse_y, entities, curr_entity,
                    omnivision):
    map_x, map_y = get_map_offset(console, game_map, curr_entity)
    con_x, con_y = get_console_offset(console, game_map)
    x_off = map_x - con_x
    y_off = map_y - con_y
    mouse_x += x_off
    mouse_y += y_off
    if ((mouse_x < game_map.width and mouse_y < game_map.height)
            and (curr_entity.fov_map.fov[mouse_y][mouse_x]
                 or omnivision)):
        names = []
        for entity in entities:
            if (entity.x == mouse_x and entity.y == mouse_y
                    and entity is not entities[0]
                    and curr_entity is not entities[0]):
                names.append(entity.name)
        namelist = ", ".join(names)
        return namelist


def render_all(con, panel_ui, panel_map, entities, game_map, curr_entity,
               constants, omnivision, msg_log, mouse_x, mouse_y, game_state):
    # pull our constants out into variables
    screen_width = constants["screen_width"]
    screen_height = constants["screen_height"]
    bar_width = constants["bar_width"]
    panel_ui_y = constants["panel_ui_y"]
    colors = constants["colors"]
    # sort our entities so we render them in the right order
    entities_sorted = sorted(entities, key=lambda x: x.render_order.value)

    # if we're currently controlling entity 0, we see things differently
    if curr_entity.aetherial:
        gray_map(panel_map)
        for entity in entities_sorted:
            if entity == curr_entity:
                draw_entity(panel_map, game_map, entity, curr_entity,
                            omnivision)
            elif entity.soul:
                draw_soul(panel_map, game_map, entity, curr_entity, omnivision)

    # otherwise, we see things normally:
    else:
        # draw all the tiles in the game map
        if not curr_entity.aetherial:
            draw_map(panel_map, game_map, curr_entity, colors, omnivision)

        # draw all the entities in the list, except for entity 0
        for entity in entities_sorted:
            if not entity.aetherial:
                draw_entity(panel_map, game_map, entity, curr_entity,
                            omnivision)

    # draw UI panel
    # Dungeon Level
    panel_ui.print(1, 3, f"Dungeon Level: {game_map.dlevel}", tcod.white)

    # HP bar
    render_bar(panel_ui, 1, 1, bar_width, "HP", curr_entity.fighter.hp,
               curr_entity.fighter.max_hp, tcod.light_red, tcod.darker_red)

    # message log
    y = 1
    msg_start = msg_log.bottom + msg_log.height - 1
    msg_end = msg_log.bottom - 1
    for i in range(msg_start, msg_end, -1):
        message = msg_log.messages[i]
        panel_ui.print(msg_log.x, y, message.text, fg=message.color,
                       alignment=tcod.LEFT)
        y += 1

    # anything we're mousing over
    namelist = mouseover_names(panel_map, game_map, mouse_x, mouse_y, entities,
                               curr_entity, omnivision)
    if namelist:
        panel_ui.print(1, 0, namelist, fg=tcod.light_gray, alignment=tcod.LEFT)

    # blit UI and map to root console
    panel_ui.blit(con, 0, panel_ui_y,
                  width=panel_ui.width, height=panel_ui.height)
    panel_map.blit(con, 0, 0, width=panel_map.width, height=panel_map.height)
    # display inventory menu if we're interacting with it
    if game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
        if game_state == GameStates.SHOW_INVENTORY:
            m_str = "Press the key next to an item to use it, or Esc to cancel"
        else:
            m_str = "Press the key next to an item to drop it, or Esc to cancel"
        inventory_menu(con, m_str, curr_entity, 50,
                       screen_width, screen_height)
    # display level up menu if we've leveled up
    elif game_state == GameStates.LEVEL_UP:
        level_up_menu(con, "Level up! Choose a stat to raise!", curr_entity,
                      40, screen_width, screen_height)
    elif game_state == GameStates.CHARACTER_SCREEN:
        character_screen(con, curr_entity, 30, 11, screen_width, screen_height)

    # clear map and ui panels for next time
    panel_map.clear()
    panel_ui.clear()


def draw_map(console, game_map, curr_entity, colors, omnivision):
    # our map panel's (tcod console) background array
    bg = console.bg

    # get our map panel's top left corner offset from the actual game map
    # these are 0 if the map is smaller in a dimension than the console
    map_off_x, map_off_y = get_map_offset(console, game_map, curr_entity)

    # get our map display offset from the console top left corner
    # these are 0 if the map is larger in a dimension than the console
    con_off_x, con_off_y = get_console_offset(console, game_map)

    # go through our map display area, update our map panel's background colors
    for y in range(min(console.height, game_map.height)):
        for x in range(min(console.width, game_map.width)):
            map_x = x + map_off_x
            map_y = y + map_off_y
            con_x = x + con_off_x
            con_y = y + con_off_y
            visible = curr_entity.fov_map.fov[map_y][map_x]
            wall = game_map.tiles[map_x][map_y].block_sight
            if visible:
                if wall:
                    bg[con_y][con_x] = colors["light_wall"]
                else:
                    bg[con_y][con_x] = colors["light_ground"]
            elif (curr_entity.ident in game_map.tiles[map_x][map_y].explored
                  or omnivision):
                if wall:
                    bg[con_y][con_x] = colors["dark_wall"]
                else:
                    bg[con_y][con_x] = colors["dark_ground"]
            else:
                bg[con_y][con_x] = tcod.black


def blank_map(console):
    bg = console.bg
    for y in range(console.height):
        for x in range(console.width):
            bg[y][x] = tcod.black


def gray_map(console):
    bg = console.bg
    for y in range(console.height):
        for x in range(console.width):
            bg[y][x] = tcod.grey


def draw_entity(console, game_map, entity, curr_entity, omnivision):
    if ((entity.stairs and curr_entity.ident in game_map.tiles[entity.x][entity.y].explored)
            or curr_entity.fov_map.fov[entity.y][entity.x]
            or omnivision):
        map_x, map_y = get_map_offset(console, game_map, curr_entity)
        con_x, con_y = get_console_offset(console, game_map)
        x_off = map_x - con_x
        y_off = map_y - con_y
        console.default_fg = entity.color
        console.put_char(entity.x - x_off, entity.y - y_off, ord(entity.char))


def draw_soul(console, game_map, entity, curr_entity, omnivision):
    map_x, map_y = get_map_offset(console, game_map, curr_entity)
    if curr_entity.fov_map.fov[entity.y][entity.x] or omnivision:
        map_x, map_y = get_map_offset(console, game_map, curr_entity)
        con_x, con_y = get_console_offset(console, game_map)
        x_off = map_x - con_x
        y_off = map_y - con_y
        console.default_fg = entity.soul.color
        console.put_char(entity.x - x_off, entity.y - y_off,
                         ord(entity.soul.char))


def clear_entity(console, entity):
    # erase the character that represents this object
    console.put_char(entity.x, entity.y, ord(" "))


def display_space(console, space, color):
    for x, y in space:
        tcod.console_set_char_background(console, x, y, color, tcod.BKGND_SET)


def get_soul_char(soul):
    tens_digit = soul // 10
    if tens_digit % 2 == 0:
        char = '*'
    else:
        char = '+'
    return char


def get_soul_color(soul):
    if soul < 20:
        color = tcod.red
    elif soul < 40:
        color = tcod.orange
    elif soul < 60:
        color = tcod.yellow
    elif soul < 80:
        color = tcod.green
    elif soul < 100:
        color = tcod.blue
    else:
        color = tcod.violet
    return color


def get_map_offset(console, game_map, curr_entity):
    # get our map panel's top left corner offset from the actual game map
    map_x = int(curr_entity.x - console.width / 2)
    if map_x < 0:
        map_x = 0
    elif map_x + console.width > game_map.width:
        map_x = game_map.width - console.width
    map_y = int(curr_entity.y - console.height / 2)
    if map_y < 0:
        map_y = 0
    elif map_y + console.height > game_map.height:
        map_y = game_map.height - console.height

    return (map_x, map_y)


def get_console_offset(console, game_map):
    # get our map's display offset from the top left corner of the console
    con_x = int((console.width - game_map.width) / 2)
    con_y = int((console.height - game_map.height) / 2)
    if con_x < 0:
        con_x = 0
    if con_y < 0:
        con_y = 0

    return (con_x, con_y)
