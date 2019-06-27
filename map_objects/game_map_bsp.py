# -*- coding: utf-8 -*-
"""
Created on Wed Jun 26 23:04:23 2019

@author: theoldestnoob
"""

from random import seed as randseed
from random import randint
from random import uniform

from map_objects.geometry import Rect
from map_objects.geometry import line_lerp_orthogonal
from map_objects.tile import Tile
from map_objects.game_map import GameMap


class GameMapBSP(GameMap):
    def make_map(self, player, *args, room_min_size=6, room_max_size=10,
                 bsp_depth=5, bsp_min=0.45, bsp_max=0.55, **kwargs):
        map_width = self.width
        map_height = self.height
        randseed(self.seed)

        space = Rect(0, 0, map_width, map_height)
        self.partition(space, bsp_depth, bsp_min, bsp_max,
                       room_min_size, room_max_size)

    def partition(self, space, bsp_depth, bsp_min, bsp_max,
                  room_min_size, room_max_size):
        if bsp_depth == 0 or space.h < room_min_size or space.w < room_min_size:
            self.create_room(space)
            return True
        bsp_depth -= 1
        xy = randint(0, 1)
        if space.w >= room_min_size and space.w <= room_max_size:
            xy = 0
            print("Width fit!")
        elif space.h >= room_min_size and space.h <= room_max_size:
            xy = 1
            print("Height fit!")
        part_ratio = uniform(bsp_min, bsp_max)
        print(f"space {space}")
        print(f"ratio {part_ratio}")
        # partition space into two smaller Rects
        if xy == 0:
            # horizontal split
            part_height = int(part_ratio * space.h)
            part_a_h = part_height
            part_b_h = space.h - part_height - 1
            part_a = Rect(space.x1, space.y1, space.w, part_a_h)
            part_b = Rect(space.x1, space.y1 + part_a_h, space.w, part_b_h)
            print(f"part_height {part_height}, part_a_h {part_a_h}, part_b_h {part_b_h}")
        else:
            # vertical split
            part_width = int(part_ratio * space.w)
            part_a_w = part_width
            part_b_w = space.w - part_width - 1
            part_a = Rect(space.x1, space.y1, part_a_w, space.h)
            part_b = Rect(space.x1 + part_a_w, space.y1, part_b_w, space.h)
            print(f"part_width {part_width}, part_a_w {part_a_w}, part_b_w {part_b_w}")

        # recurse, draw a room in the partition if the subfunction creates a room that's too small
        print(f"part_a {part_a}")
        print(f"part_b {part_b}")
        # self.create_room(part_a)
        # self.create_room(part_b)
        self.partition(part_a, bsp_depth, bsp_min, bsp_max,
                       room_min_size, room_max_size)
        self.partition(part_b, bsp_depth, bsp_min, bsp_max,
                       room_min_size, room_max_size)
