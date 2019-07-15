# -*- coding: utf-8 -*-
"""
Created on Tue Jun 25 19:35:17 2019

@author: theoldestnoob
"""

import tcod
from enum import Enum


class RenderOrder(Enum):
    CORPSE = 1
    ITEM = 2
    ACTOR = 3


def render_bar(panel, x, y, total_width, name, value, maximum, bar_color,
               back_color):
    bar_width = int(float(value) / maximum * total_width)
    panel.draw_rect(x, y, total_width, 1, ord(" "), bg=back_color)
    if bar_width > 0:
        panel.draw_rect(x, y, bar_width, 1, ord(" "), bg=bar_color)
    panel.print(int(x + total_width / 2), y, f"{name}: {value}/{maximum}",
                fg=tcod.white, alignment=tcod.CENTER)


def mouseover_names(game_map, mouse_x, mouse_y, entities, curr_entity,
                    omnivision):
    if ((mouse_x < game_map.width and mouse_y < game_map.height)
            and (curr_entity.fov_map.fov[mouse_y][mouse_x] or omnivision)):
        names = []
        for entity in entities:
            if (entity.x == mouse_x and entity.y == mouse_y
                    and entity is not entities[0]
                    and curr_entity is not entities[0]):
                names.append(entity.name)
        namelist = ", ".join(names)
        return namelist


def render_all(con, panel_ui, panel_map, entities, game_map, curr_entity,
               screen_width, screen_height,
               bar_width, panel_ui_width, panel_ui_height, panel_ui_y,
               panel_map_width, panel_map_height,
               colors, message_log, mouse_x, mouse_y, omnivision):
    # sort our entities so we render them in the right order
    entities_sorted = sorted(entities, key=lambda x: x.render_order.value)

    # if we're currently controlling entity 0, we see things differently
    if curr_entity.ident == 0:
        gray_map(con, game_map)
        for entity in entities_sorted:
            if entity == curr_entity:
                draw_entity(con, entity, curr_entity.fov_map, omnivision)
            elif entity.soul > 0:
                draw_soul(con, entity, curr_entity.fov_map, omnivision)

    # otherwise, we see things normally:
    else:
        # draw all the tiles in the game map
        if curr_entity.ident != 0:
            draw_map(con, game_map, curr_entity, colors, omnivision)

        # draw all the entities in the list, except for entity 0
        for entity in entities_sorted:
            if entity.ident != 0:
                draw_entity(con, entity, curr_entity.fov_map, omnivision)

    # draw UI panel
    panel_ui.clear()

    # HP bar
    render_bar(panel_ui, 1, 1, bar_width, "HP", curr_entity.fighter.hp,
               curr_entity.fighter.max_hp, tcod.light_red, tcod.darker_red)

    # message log
    y = 1
    for message in message_log.messages:
        panel_ui.print(message_log.x, y, message.text, fg=message.color,
                       alignment=tcod.LEFT)
        y += 1

    # anything we're mousing over
    namelist = mouseover_names(game_map, mouse_x, mouse_y, entities,
                               curr_entity, omnivision)
    if namelist:
        panel_ui.print(1, 0, namelist, fg=tcod.light_gray, alignment=tcod.LEFT)

    # blit UI and map to root console
    tcod.console_blit(panel_ui, 0, 0, panel_ui_width, panel_ui_height, 0, 0,
                      panel_ui_y)
    tcod.console_blit(con, 0, 0, screen_width, screen_height, 0, 0, 0)


def clear_all(con, entities):
    for entity in entities:
        clear_entity(con, entity)


def draw_map(con, game_map, curr_entity, colors, omnivision):
    bg = con.bg
    for y in range(game_map.height):
        for x in range(game_map.width):
            visible = curr_entity.fov_map.fov[y][x]
            wall = game_map.tiles[x][y].block_sight
            if visible:
                if wall:
                    bg[y][x] = colors["light_wall"]
                else:
                    bg[y][x] = colors["light_ground"]
            elif (curr_entity.ident in game_map.tiles[x][y].explored
                  or omnivision):
                if wall:
                    bg[y][x] = colors["dark_wall"]
                else:
                    bg[y][x] = colors["dark_ground"]
            else:
                bg[y][x] = tcod.black


def blank_map(con, game_map):
    bg = con.bg
    for y in range(game_map.height):
        for x in range(game_map.width):
            bg[y][x] = tcod.black


def gray_map(con, game_map):
    bg = con.bg
    for y in range(game_map.height):
        for x in range(game_map.width):
            bg[y][x] = tcod.grey


def draw_entity(con, entity, fov_map, omnivision):
    if fov_map.fov[entity.y][entity.x] or omnivision:
        con.default_fg = entity.color
        con.put_char(entity.x, entity.y, ord(entity.char))


def draw_soul(con, entity, fov_map, omnivision):
    if fov_map.fov[entity.y][entity.x] or omnivision:
        soul_char = get_soul_char(entity.soul)
        soul_color = get_soul_color(entity.soul)
        con.default_fg = soul_color
        con.put_char(entity.x, entity.y, ord(soul_char))


def clear_entity(con, entity):
    # erase the character that represents this object
    con.put_char(entity.x, entity.y, ord(" "))


def display_space(con, space, color):
    for x, y in space:
        tcod.console_set_char_background(con, x, y, color, tcod.BKGND_SET)


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
