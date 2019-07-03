# -*- coding: utf-8 -*-
"""
Created on Tue Jul  2 20:57:10 2019

@author: theoldestnoob
"""

import tcod


def initialize_fov(game_map):
    fov_map = tcod.map_new(game_map.width, game_map.height)

    for y in range(game_map.height):
        for x in range(game_map.width):
            tcod.map_set_properties(fov_map, x, y,
                                    not game_map.tiles[x][y].block_sight,
                                    not game_map.tiles[x][y].blocked)

    return fov_map
