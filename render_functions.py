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


def render_all(con, panel, entities, game_map, curr_entity, screen_width,
               screen_height, bar_width, panel_height, panel_y, colors,
               omnivision):
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
        '''hp_str = f"HP: n/a  "
        tcod.console_set_default_foreground(con, tcod.white)
        tcod.console_print_ex(con, 1, screen_height - 2, tcod.BKGND_NONE,
                              tcod.LEFT, hp_str)'''

    # otherwise, we see things normally:
    else:
        # draw all the tiles in the game map
        if curr_entity.ident != 0:
            draw_map(con, game_map, curr_entity, colors, omnivision)

        # draw all the entities in the list, except for entity 0
        for entity in entities_sorted:
            if entity.ident != 0:
                draw_entity(con, entity, curr_entity.fov_map, omnivision)

        '''hp_str = (f"HP: {curr_entity.fighter.hp:02}"
                  f"/{curr_entity.fighter.max_hp:02}")
        tcod.console_set_default_foreground(con, tcod.white)
        tcod.console_print_ex(con, 1, screen_height - 2, tcod.BKGND_NONE,
                              tcod.LEFT, hp_str)'''
    render_bar(panel, 1, 1, bar_width, "HP", curr_entity.fighter.hp,
               curr_entity.fighter.max_hp, tcod.light_red, tcod.darker_red)
    tcod.console_blit(panel, 0, 0, screen_width, panel_height, 0, 0, panel_y)
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
