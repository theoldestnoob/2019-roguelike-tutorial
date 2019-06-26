# -*- coding: utf-8 -*-
"""
Created on Tue Jun 25 19:35:17 2019

@author: theoldestnoob
"""

import tcod


def render_all(con, entities, game_map, screen_width, screen_height, colors):
    # draw all the tiles in the game map
    for y in range(game_map.height):
        for x in range(game_map.width):
            wall = game_map.tiles[x][y].block_sight

            if wall:
                tcod.console_set_char_background(con, x, y,
                                                 colors["dark_wall"],
                                                 tcod.BKGND_SET)
            else:
                tcod.console_set_char_background(con, x, y,
                                                 colors["dark_ground"],
                                                 tcod.BKGND_SET)

    # draw all the entities in the list
    for entity in entities:
        draw_entity(con, entity)

    # tcod.console_blit(con, 0, 0, screen_width, screen_height, 0, 0, 0)


def clear_all(con, entities):
    for entity in entities:
        clear_entity(con, entity)


def draw_entity(con, entity):
    con.default_fg = entity.color
    con.put_char(entity.x, entity.y, ord(entity.char))


def clear_entity(con, entity):
    # erase the character that represents this object
    con.put_char(entity.x, entity.y, ord(" "))
