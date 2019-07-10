# -*- coding: utf-8 -*-
"""
Created on Tue Jun 25 19:35:17 2019

@author: theoldestnoob
"""

import tcod


def render_all(con, entities, game_map, curr_entity, render_update,
               screen_width, screen_height, colors, omnivision):
    # if we're currently controlling entity 0, we see things differently
    if curr_entity.ident == 0:
        gray_map(con, game_map)
        for entity in entities:
            if entity == curr_entity:
                draw_entity(con, entity, curr_entity.fov_map, omnivision)
            else:
                draw_soul(con, entity, curr_entity.fov_map, omnivision)

    # otherwise, we see things normally:
    else:
        # draw all the tiles in the game map
        if curr_entity.ident != 0:
            draw_map(con, game_map, curr_entity, render_update,
                     colors, omnivision)

        # draw all the entities in the list, except for entity 0
        for entity in entities:
            if entity.ident != 0:
                draw_entity(con, entity, curr_entity.fov_map, omnivision)

    # tcod.console_blit(con, 0, 0, screen_width, screen_height, 0, 0, 0)


def clear_all(con, entities):
    for entity in entities:
        clear_entity(con, entity)


def draw_map(con, game_map, curr_entity, render_update, colors, omnivision):
    if render_update:
        for y in range(game_map.height):
            for x in range(game_map.width):
                visible = tcod.map_is_in_fov(curr_entity.fov_map, x, y)
                wall = game_map.tiles[x][y].block_sight

                if visible:
                    if wall:
                        tcod.console_set_char_background(con, x, y,
                                                         colors["light_wall"],
                                                         tcod.BKGND_SET)
                    else:
                        tcod.console_set_char_background(con, x, y,
                                                         colors["light_ground"],
                                                         tcod.BKGND_SET)
                elif (curr_entity.ident in game_map.tiles[x][y].explored
                      or omnivision):
                    if wall:
                        tcod.console_set_char_background(con, x, y,
                                                         colors["dark_wall"],
                                                         tcod.BKGND_SET)
                    else:
                        tcod.console_set_char_background(con, x, y,
                                                         colors["dark_ground"],
                                                         tcod.BKGND_SET)


def blank_map(con, game_map):
    for y in range(game_map.height):
        for x in range(game_map.width):
            tcod.console_set_char_background(con, x, y, tcod.black,
                                             tcod.BKGND_SET)


def gray_map(con, game_map):
    for y in range(game_map.height):
        for x in range(game_map.width):
            tcod.console_set_char_background(con, x, y, tcod.grey,
                                             tcod.BKGND_SET)


def draw_entity(con, entity, fov_map, omnivision):
    if tcod.map_is_in_fov(fov_map, entity.x, entity.y) or omnivision:
        con.default_fg = entity.color
        con.put_char(entity.x, entity.y, ord(entity.char))


def draw_soul(con, entity, fov_map, omnivision):
    if tcod.map_is_in_fov(fov_map, entity.x, entity.y) or omnivision:
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
