# -*- coding: utf-8 -*-
"""
Created on Sat Jul 27 18:12:22 2019

@author: theoldestnoob
"""

import tcod


def get_constants():
    # "global" variables
    debug_f = True
    seed = "testseed"

    # window settings
    window_title = "Roguelike Tutorial 2019 - theoldestnoob"
    screen_width = 80
    screen_height = 50

    # ui element settings
    bar_width = 20
    panel_ui_width = screen_width
    panel_ui_height = 7
    panel_ui_y = screen_height - panel_ui_height

    message_x = bar_width + 2
    message_width = screen_width - bar_width - 2
    message_height = panel_ui_height - 1

    panel_map_width = 80
    panel_map_height = 43

    # fov settings
    fov_algorithm = 0
    fov_light_walls = True
    fov_radius = 10
    omnivision = False

    # map settings
    map_width = 100
    map_height = 60

    # various map settings - TODO: move to other module
    mapset_bsprect = {
            "room_max_size": 15,
            "room_min_size": 8,
            "min_rooms": 8,
            "max_rooms": 30,
            "ratio_vh": 1,
            "ratio_hv": 1,
            "ratio_d": 0,
            "hall_rand": False,
            "circ_rooms": 0,
            "rect_rooms": 1,
            "unused": True,
            "bsp_range": 0.15,
            "bsp_depth": 4,
            "max_monsters_per_room": 3,
            "max_items_per_room": 2
    }

    mapset_bspcirc = {
            "room_max_size": 26,
            "room_min_size": 8,
            "min_rooms": 8,
            "max_rooms": 30,
            "ratio_vh": 0,
            "ratio_hv": 0,
            "ratio_d": 1,
            "hall_rand": True,
            "circ_rooms": 1,
            "rect_rooms": 0,
            "unused": True,
            "bsp_range": 0.25,
            "bsp_depth": 4,
            "max_monsters_per_room": 3,
            "max_items_per_room": 2
    }

    mapset_bsprand = {
            "room_max_size": 20,
            "room_min_size": 6,
            "min_rooms": 5,
            "max_rooms": 30,
            "ratio_vh": 1,
            "ratio_hv": 1,
            "ratio_d": 1,
            "hall_rand": True,
            "circ_rooms": 1,
            "rect_rooms": 1,
            "unused": True,
            "bsp_range": 0.4,
            "bsp_depth": 4,
            "max_monsters_per_room": 3,
            "max_items_per_room": 26
    }

    colors = {
            "dark_wall": tcod.Color(0, 0, 100),
            "dark_ground": tcod.Color(50, 50, 150),
            "light_wall": tcod.Color(130, 110, 50),
            "light_ground": tcod.Color(200, 180, 50)
    }

    # put it all into a dict to pass around
    constants = {
            "debug_f": debug_f,
            "seed": seed,
            "window_title": window_title,
            "screen_width": screen_width,
            "screen_height": screen_height,
            "bar_width": bar_width,
            "panel_ui_width": panel_ui_width,
            "panel_ui_height": panel_ui_height,
            "panel_ui_y": panel_ui_y,
            "message_x": message_x,
            "message_width": message_width,
            "message_height": message_height,
            "panel_map_width": panel_map_width,
            "panel_map_height": panel_map_height,
            "map_width": map_width,
            "map_height": map_height,
            "fov_algorithm": fov_algorithm,
            "fov_light_walls": fov_light_walls,
            "fov_radius": fov_radius,
            "omnivision": omnivision,
            "mapset": mapset_bsprand,
            "colors": colors
            }

    return constants
