# -*- coding: utf-8 -*-
"""
Created on Wed Jun 26 23:04:23 2019

@author: theoldestnoob
"""

from random import seed as randseed
from random import randint
from random import uniform
from random import choice

from map_objects.geometry import Rect
from map_objects.geometry import Circle
from map_objects.game_map import GameMap


# TODO: store BSP tree structure for later use when generating halls
class GameMapBSP(GameMap):
    def make_map(self, player, *args,
                 room_min_size=8, room_max_size=15, min_rooms=8, max_rooms=30,
                 bsp_depth=4, bsp_min=0.35, bsp_max=0.65,
                 ratio_vh=1, ratio_hv=1, ratio_d=0, hall_rand=False,
                 circ_rooms=0, rect_rooms=1, **kwargs):
        map_width = self.width - 1
        map_height = self.height - 1
        randseed(self.seed)
        self.rect_rooms = rect_rooms
        self.circ_rooms = circ_rooms

        space = Rect(1, 1, map_width - 2, map_height - 2)
        while True:
            self.rooms = []
            self.tiles = self.initialize_tiles()
            self.partition(space, bsp_depth, bsp_min, bsp_max,
                           room_min_size, room_max_size)
            numrooms = len(self.rooms)
            if min_rooms < numrooms < max_rooms:
                break
        if hall_rand:
            self.make_halls_random(space, player, ratio_vh, ratio_hv, ratio_d)
        else:
            self.make_halls(space, player, ratio_vh, ratio_hv, ratio_d)

    def partition(self, space, bsp_depth, bsp_min, bsp_max,
                  room_min_size, room_max_size):
        if bsp_depth == 0 or (space.h < room_max_size and space.w < room_max_size):
            bounds = Rect(space.x1 + 1, space.y1 + 1, space.w - 2, space.h - 2)
            # self.rooms.append(space)
            if bounds.h < room_min_size or bounds.w < room_min_size:
                return True
            roomw = randint(room_min_size, room_max_size)
            roomh = randint(room_min_size, room_max_size)
            if roomw > bounds.w:
                roomw = bounds.w
            if roomh > bounds.h:
                roomh = bounds.h
            # print(f"Bounds: {bounds}, Roomw: {roomw}, Roomh: {roomh}")
            if bounds.x1 == bounds.x1 + bounds.w - roomw:
                roomx = bounds.x1
            else:
                roomx = randint(bounds.x1, bounds.x1 + (bounds.w - roomw))
            if bounds.y1 == bounds.y1 + bounds.h - roomh:
                roomy = bounds.y1
            else:
                roomy = randint(bounds.y1, bounds.y1 + (bounds.h - roomh))
            room = Rect(roomx, roomy, roomw, roomh)

            randpool = self.circ_rooms + self.rect_rooms
            roll = uniform(0, randpool)
            if roll < self.circ_rooms:
                (c_x, c_y) = room.center()
                r = room.w // 2
                circ = Circle(c_x, c_y, r)
                self.create_room(circ)
                self.rooms.append(circ)
            else:
                self.create_room(room)
                self.rooms.append(room)

            return True
        bsp_depth -= 1
        xy = randint(0, 1)
        if space.w >= room_min_size and space.w <= room_max_size:
            xy = 0
            # print("Width fit!")
        elif space.h >= room_min_size and space.h <= room_max_size:
            xy = 1
            # print("Height fit!")
        part_ratio = uniform(bsp_min, bsp_max)
        # print(f"space {space}")
        # print(f"ratio {part_ratio}")
        # partition space into two smaller Rects
        if xy == 0:
            # horizontal split
            part_height = int(part_ratio * space.h) - 1
            part_a_h = part_height
            part_b_h = space.h - part_height - 1
            part_a = Rect(space.x1, space.y1, space.w, part_a_h)
            part_b = Rect(space.x1, space.y1 + part_a_h + 1, space.w, part_b_h)
            # print(f"part_height {part_height}, part_a_h {part_a_h}, part_b_h {part_b_h}")
        else:
            # vertical split
            part_width = int(part_ratio * space.w) - 1
            part_a_w = part_width
            part_b_w = space.w - part_width - 1
            part_a = Rect(space.x1, space.y1, part_a_w, space.h)
            part_b = Rect(space.x1 + part_a_w + 1, space.y1, part_b_w, space.h)
            # print(f"part_width {part_width}, part_a_w {part_a_w}, part_b_w {part_b_w}")

        # recurse, draw a room in the partition if the subfunction creates a room that's too small
        # print(f"part_a {part_a}")
        # print(f"part_b {part_b}")
        # self.create_room(part_a)
        # self.create_room(part_b)
        self.partition(part_a, bsp_depth, bsp_min, bsp_max,
                       room_min_size, room_max_size)
        self.partition(part_b, bsp_depth, bsp_min, bsp_max,
                       room_min_size, room_max_size)
