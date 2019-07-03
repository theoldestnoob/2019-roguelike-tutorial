# -*- coding: utf-8 -*-
"""
Created on Tue Jun 25 19:35:17 2019

@author: theoldestnoob
"""

import tcod


def render_all(con, entities, game_map, fov_map, fov_recompute,
               screen_width, screen_height, colors, omnivision):
    # draw all the tiles in the game map
    draw_map(con, game_map, fov_map, fov_recompute, colors, omnivision)

    # draw all the entities in the list
    for entity in entities:
        draw_entity(con, entity, fov_map, omnivision)

    # tcod.console_blit(con, 0, 0, screen_width, screen_height, 0, 0, 0)


def clear_all(con, entities):
    for entity in entities:
        clear_entity(con, entity)


def draw_map(con, game_map, fov_map, fov_recompute, colors, omnivision):
    if fov_recompute:
        for y in range(game_map.height):
            for x in range(game_map.width):
                visible = tcod.map_is_in_fov(fov_map, x, y)
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
                    game_map.tiles[x][y].explored = True
                elif game_map.tiles[x][y].explored or omnivision:
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


def draw_entity(con, entity, fov_map, omnivision):
    if tcod.map_is_in_fov(fov_map, entity.x, entity.y) or omnivision:
        con.default_fg = entity.color
        con.put_char(entity.x, entity.y, ord(entity.char))


def clear_entity(con, entity):
    # erase the character that represents this object
    con.put_char(entity.x, entity.y, ord(" "))


def display_space(con, space, color):
    for x, y in space:
        tcod.console_set_char_background(con, x, y, color, tcod.BKGND_SET)
