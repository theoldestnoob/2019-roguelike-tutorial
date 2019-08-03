# -*- coding: utf-8 -*-
"""
Created on Tue Jul  2 20:57:10 2019

@author: theoldestnoob
"""

import tcod


def initialize_fov(game_map):

    fov_map = tcod.map.Map(width=game_map.width, height=game_map.height)
    transparency = game_map.game_map_to_transparent_array()
    for y in range(game_map.height):
        for x in range(game_map.width):
            fov_map.transparent[y][x] = transparency[x][y]

    return fov_map


def init_fov_aetherial(game_map):

    fov_map = tcod.map.Map(width=game_map.width, height=game_map.height)
    fov_map.transparent[:] = True

    return fov_map


def recompute_fov(game_map, entity, radius, light_walls=True, algorithm=0):

    entity.fov_map.compute_fov(entity.x, entity.y, radius, light_walls,
                               algorithm)

    for y in range(game_map.height):
        for x in range(game_map.width):
            visible = entity.fov_map.fov[y][x]
            if visible and entity.ident not in game_map.tiles[x][y].explored:
                game_map.tiles[x][y].explored.append(entity.ident)
